param(
    [ValidateRange(0, 86400)]
    [int]$DuracaoSegundos = 0,

    [ValidateRange(1, 65535)]
    [int]$PortaApi = 8000
)

$ErrorActionPreference = "Stop"

$softwareDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$python = Join-Path $softwareDir ".venv\Scripts\python.exe"
$runId = "estacao-meteorologica-$PID"
$tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
$sessionDir = Join-Path $tempRoot $runId
$databasePath = Join-Path $sessionDir "leituras.db"
$subscriberOut = Join-Path $sessionDir "subscriber.out.log"
$subscriberErr = Join-Path $sessionDir "subscriber.err.log"
$apiOut = Join-Path $sessionDir "api.out.log"
$apiErr = Join-Path $sessionDir "api.err.log"
$processes = @()

function Stop-ProcessTree {
    param([System.Diagnostics.Process]$Process)

    if ($null -ne $Process -and -not $Process.HasExited) {
        & taskkill.exe /PID $Process.Id /T /F 2>$null | Out-Null
    }
}

function Show-LogIfPresent {
    param([string]$Path)

    if (Test-Path -LiteralPath $Path) {
        $content = Get-Content -Raw -LiteralPath $Path
        if (-not [string]::IsNullOrWhiteSpace($content)) {
            Write-Host $content
        }
    }
}

if (-not (Test-Path -LiteralPath $python)) {
    throw "Ambiente Python nao encontrado. Na pasta software, execute primeiro: uv sync"
}

$mosquitto = Get-Service -Name "mosquitto" -ErrorAction Stop
if ($mosquitto.Status -ne "Running") {
    try {
        Start-Service -Name "mosquitto" -ErrorAction Stop
    }
    catch {
        throw "O Mosquitto esta parado. Abra o PowerShell como administrador e execute: Start-Service mosquitto"
    }
}

New-Item -ItemType Directory -Path $sessionDir -ErrorAction Stop | Out-Null

$env:WEATHER_DATABASE_PATH = $databasePath
$env:MQTT_HOST = "127.0.0.1"
$env:MQTT_PORT = "1883"
$env:MQTT_TOPIC = "weather/station-01/readings"
$env:MQTT_QOS = "1"
$apiUrl = "http://127.0.0.1:$PortaApi"

try {
    $subscriber = Start-Process -FilePath $python `
        -ArgumentList @("-m", "app.mqtt_subscriber") `
        -WorkingDirectory $softwareDir `
        -WindowStyle Hidden `
        -RedirectStandardOutput $subscriberOut `
        -RedirectStandardError $subscriberErr `
        -PassThru
    $processes += $subscriber

    $api = Start-Process -FilePath $python `
        -ArgumentList @(
            "-m", "uvicorn", "app.main:app",
            "--host", "127.0.0.1",
            "--port", $PortaApi
        ) `
        -WorkingDirectory $softwareDir `
        -WindowStyle Hidden `
        -RedirectStandardOutput $apiOut `
        -RedirectStandardError $apiErr `
        -PassThru
    $processes += $api

    $apiReady = $false
    $startupDeadline = [DateTime]::UtcNow.AddSeconds(20)
    while ([DateTime]::UtcNow -lt $startupDeadline) {
        if ($subscriber.HasExited) {
            Show-LogIfPresent $subscriberErr
            throw "O assinante MQTT encerrou durante a inicializacao."
        }
        if ($api.HasExited) {
            Show-LogIfPresent $apiErr
            throw "A API encerrou durante a inicializacao. Verifique se a porta $PortaApi esta livre."
        }

        try {
            $health = Invoke-RestMethod -Uri "$apiUrl/health" -TimeoutSec 2
            if ($health.status -eq "ok") {
                $apiReady = $true
                break
            }
        }
        catch {
            Start-Sleep -Milliseconds 250
        }
    }

    if (-not $apiReady) {
        throw "A API nao ficou disponivel em ate 20 segundos."
    }

    Write-Host "Estacao em execucao. Pressione Ctrl+C para encerrar."
    Write-Host "Aguardando a primeira leitura do ESP32..."
    $startedAt = [DateTime]::UtcNow

    while ($true) {
        if ($DuracaoSegundos -gt 0 -and
            ([DateTime]::UtcNow - $startedAt).TotalSeconds -ge $DuracaoSegundos) {
            break
        }
        if ($subscriber.HasExited) {
            Show-LogIfPresent $subscriberErr
            throw "O assinante MQTT foi encerrado inesperadamente."
        }
        if ($api.HasExited) {
            Show-LogIfPresent $apiErr
            throw "A API foi encerrada inesperadamente."
        }

        try {
            $reading = Invoke-RestMethod `
                -Uri "$apiUrl/api/v1/readings/latest" `
                -TimeoutSec 2

            try {
                Clear-Host
            }
            catch {
                # A limpeza de tela pode falhar em terminais não interativos.
                # Isso não deve ocultar uma leitura recebida corretamente.
            }
            Write-Host "Estacao meteorologica - atualizacao aproximada de 500 ms"
            Write-Host "Pressione Ctrl+C para encerrar.`n"
            [PSCustomObject]@{
                RecebidoEm       = $reading.received_at
                TemperaturaC     = $reading.temperature_c
                UmidadePct       = $reading.humidity_pct
                PressaoHpa       = $reading.pressure_hpa
                GasBruto         = $reading.gas_raw
                LuminosidadeBruta = $reading.light_raw
                LuzDetectada     = $reading.light_detected
                ChuvaDetectada   = $reading.rain_detected
                Status           = $reading.status
            } | Format-List
        }
        catch {
            Write-Host "Aguardando a primeira leitura do ESP32..."
        }

        Start-Sleep -Milliseconds 500
    }
}
finally {
    foreach ($process in $processes) {
        Stop-ProcessTree $process
    }

    Start-Sleep -Milliseconds 500
    $resolvedSession = [IO.Path]::GetFullPath($sessionDir)
    if ($resolvedSession.StartsWith($tempRoot) -and
        (Split-Path -Leaf $resolvedSession) -eq $runId -and
        (Test-Path -LiteralPath $resolvedSession)) {
        Remove-Item -LiteralPath $resolvedSession -Recurse -Force
    }

    Write-Host "Teste encerrado; processos e arquivos temporarios removidos."
}
