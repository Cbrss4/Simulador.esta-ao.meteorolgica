# Estação meteorológica — software

Este repositório contém o backend da estação meteorológica. Ele recebe leituras por MQTT, valida o JSON, salva os dados em SQLite e permite consultá-los por uma API FastAPI.

```text
ESP32 → Mosquitto → assinante Python → SQLite → API → dashboard
```

Na etapa atual, uma publicação manual com `mosquitto_pub` ocupa o lugar do ESP32. Os valores usados nesse teste são fictícios.

## Estado atual

Já funcionam localmente:

- recebimento de mensagens pelo Mosquitto;
- validação do payload com Pydantic;
- armazenamento de leituras válidas e parciais;
- rejeição de mensagens inválidas sem interromper o serviço;
- consulta da leitura atual e do histórico pela API;
- testes automatizados com bancos descartáveis.

A integração com ESP32, sensores e hotspot ainda não foi testada.

## Requisitos

- Python 3.12;
- `uv`;
- Eclipse Mosquitto.

Na pasta `software`, instale as dependências e crie a configuração local:

```powershell
uv sync
Copy-Item .env.example .env
```

O arquivo `.env` guarda a configuração local e já está incluído no `.gitignore`.

## Como executar

Confirme que o Mosquitto está ativo:

```powershell
Get-Service mosquitto
```

Abra dois terminais na pasta `software`.

No primeiro, inicie o assinante MQTT:

```powershell
uv run python -m app.mqtt_subscriber
```

No segundo, inicie a API:

```powershell
uv run uvicorn app.main:app --reload
```

## Teste rápido

Com o assinante e a API em execução, abra um terceiro PowerShell e publique uma leitura:

```powershell
$payload = '{"schema_version":1,"device_id":"station-01","captured_at":null,"temperature_c":26.1,"humidity_pct":58.4,"pressure_hpa":1011.7,"gas_raw":812,"light_detected":true,"rain_detected":false}'
$payload | & 'C:\Program Files\mosquitto\mosquitto_pub.exe' -h 127.0.0.1 -p 1883 -t 'weather/station-01/readings' -q 1 -s
```

O uso de `-s` preserva as aspas do JSON no Windows PowerShell.

Consulte a leitura recebida:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/api/v1/readings/latest' | Format-List
```

## Endpoints

| Rota | Função |
|---|---|
| `GET /health` | Verifica se a API está ativa |
| `GET /api/v1/readings/latest` | Retorna a leitura mais recente |
| `GET /api/v1/readings?limit=100` | Retorna o histórico |
| `GET /api/v1/readings/{id}` | Busca uma leitura pelo ID |

## Testes automatizados

```powershell
uv run pytest -q
```

Os testes usam bancos temporários e não alteram `data/station.db`.

## Documentação

- [Evidências da S2](docs/evidencias-s2.md)

`gas_raw` é um valor bruto, não ppm. Os estados de luz e chuva também não representam lux ou milímetros.
