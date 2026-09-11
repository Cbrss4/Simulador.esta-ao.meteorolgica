# Instruções para agentes de codificação (Codex, etc.)

Este é um projeto de simulação de estação meteorológica com ESP32, usando PlatformIO e Wokwi.

## Setup do ambiente

Execute estes comandos, em ordem, para preparar o ambiente do zero:

```bash
sudo apt-get update
sudo apt-get install -y python3-venv
python3 -c "$(curl -fsSL https://raw.githubusercontent.com/platformio/platformio-core-installer/master/get-platformio.py)"
export PATH="$PATH:$HOME/.platformio/penv/bin"
echo 'export PATH="$PATH:$HOME/.platformio/penv/bin"' >> ~/.bashrc
```

## Build

Depois do setup, compile o firmware com:

```bash
pio run
```

O binário compilado fica em `.pio/build/esp32doit-devkit-v1/firmware.bin`.

## Estrutura do projeto

- `src/main.cpp` — código-fonte do firmware (C++/Arduino)
- `platformio.ini` — configuração da placa (ESP32 DoIt DevKit V1) e bibliotecas
- `diagram.json` — diagrama de ligação dos componentes para simulação no Wokwi
- `wokwi.toml` — aponta o Wokwi para o binário compilado

## Bibliotecas usadas

- Adafruit BME280 Library
- Adafruit Unified Sensor

## Regras para o agente

- Sempre rode `pio run` depois de qualquer alteração em `src/main.cpp` para confirmar que compila sem erros antes de considerar a tarefa concluída.
- Não altere `wokwi.toml` a menos que o nome do ambiente em `platformio.ini` (`esp32doit-devkit-v1`) também mude — os dois precisam ficar sincronizados.
- Ao adicionar novas bibliotecas, edite a seção `lib_deps` do `platformio.ini`.
- Ao adicionar novos sensores simulados, edite `diagram.json` seguindo o padrão de `parts` (componente) e `connections` (fiação).
- Sempre documente mudanças relevantes no `README.md` e no `MANUAL.md`.

## Testes

Este projeto não roda testes automatizados de hardware. A validação é feita rodando a simulação no Wokwi e conferindo a saída do Serial Monitor (mensagens de temperatura, umidade, pressão, luminosidade, qualidade do ar e chuva impressas a cada 2 segundos).
