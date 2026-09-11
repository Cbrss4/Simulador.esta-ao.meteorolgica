# 🌦️ Estação Meteorológica Inteligente

Projeto integrador da disciplina **Projeto e Desenvolvimento II** — Ciência da Computação (2º semestre).

Simulação de uma estação meteorológica com ESP32, sensor ambiental BME280 (temperatura, umidade e pressão), sensor de luminosidade (LDR), sensor de qualidade do ar (MQ-135) e sensor de chuva.

## 📋 O que tem neste repositório

```
├── src/
│   └── main.cpp          → código-fonte do firmware (C++/Arduino)
├── platformio.ini         → configuração do projeto PlatformIO
├── diagram.json           → diagrama de ligação dos componentes (Wokwi)
├── wokwi.toml              → configuração da simulação Wokwi
├── .vscode/
│   └── extensions.json     → extensões recomendadas do VS Code
└── README.md               → este arquivo
```

## 🚀 Como rodar o projeto — 2 formas

Você pode simular este projeto de **duas formas diferentes**. Escolha a que for mais fácil pra você.

---

### Opção A — Direto no navegador (mais simples, recomendado para começar)

Não precisa instalar nada no computador.

1. Acesse **https://wokwi.com** e crie uma conta gratuita (ou faça login)
2. Clique em **"New Project"** → escolha **"ESP32"**
3. Abra o arquivo `sketch.ino` do novo projeto e substitua todo o conteúdo pelo conteúdo de [`src/main.cpp`](src/main.cpp) deste repositório
4. Abra o arquivo `diagram.json` do novo projeto e substitua pelo conteúdo de [`diagram.json`](diagram.json) deste repositório
5. No menu lateral do Wokwi, clique no ícone de **biblioteca (Library Manager)** e adicione:
   - `Adafruit BME280 Library`
   - `Adafruit Unified Sensor`
6. Clique no botão verde ▶️ **"Start Simulation"**
7. O Serial Monitor vai abrir automaticamente mostrando as leituras dos sensores

---

### Opção B — No VS Code (mais rápido para uso contínuo, exige instalação)

#### Pré-requisitos

- [VS Code](https://code.visualstudio.com) instalado
- [Python 3](https://www.python.org/downloads/) instalado (no Linux, geralmente já vem instalado)
- Conta gratuita no [Wokwi](https://wokwi.com) (para gerar a licença da extensão)

#### Passo 1 — Instalar as extensões no VS Code

No VS Code, vá em **Extensions** (ícone de quadrados no menu lateral) e instale:
- **PlatformIO IDE**
- **Wokwi Simulator**

#### Passo 2 — Clonar este repositório

```bash
git clone <URL-DO-SEU-REPOSITORIO>
cd <nome-da-pasta>
```

Ou baixe o ZIP pelo botão verde **"Code" → "Download ZIP"** no GitHub e extraia.

#### Passo 3 — Abrir a pasta no VS Code

`File → Open Folder` e selecione a pasta do projeto clonado/extraído.

O PlatformIO deve reconhecer automaticamente o `platformio.ini` e configurar o ambiente.

#### Passo 4 — Compilar o projeto

1. Clique no ícone da formiguinha do PlatformIO na barra lateral
2. Em **PROJECT TASKS → esp32doit-devkit-v1 → General**, clique em **Build**
3. Espere aparecer `[SUCCESS]` no terminal

#### Passo 5 — Rodar a simulação

1. Aperte **F1** (ou Ctrl+Shift+P)
2. Digite `Wokwi: Start Simulator` e aperte Enter
3. O diagrama e o Serial Monitor devem abrir automaticamente

> ⚠️ **Problemas comuns na instalação (Linux):** se o PlatformIO travar pedindo `python3.X-venv`, rode `sudo apt install python3.12-venv -y` (ajuste a versão do Python conforme a sua) e tente novamente.

---

## 🔌 Diagrama de ligação (hardware físico)

| Componente | Pino ESP32 | Observação |
|---|---|---|
| BME280 — VCC | 3V3 | |
| BME280 — GND | GND | |
| BME280 — SDA | D21 | I2C |
| BME280 — SCL | D22 | I2C |
| LDR — VCC | 3V3 | |
| LDR — GND | GND | |
| LDR — AOUT | D34 | Entrada analógica |
| MQ-135 — VCC | 5V (fonte externa recomendada) | Consome corrente extra no aquecimento |
| MQ-135 — GND | GND | |
| MQ-135 — AOUT | D35 | Entrada analógica |
| Sensor de chuva — VCC | 3V3–5V | |
| Sensor de chuva — GND | GND | |
| Sensor de chuva — D0 | D32 | Saída digital |

## 🧠 O que o código faz

- Inicializa o sensor BME280 via I2C
- A cada 2 segundos, lê:
  - Temperatura (°C), umidade (%) e pressão (hPa) do BME280
  - Luminosidade do LDR (valor analógico 0–4095)
  - Qualidade do ar do MQ-135 (valor analógico 0–4095)
  - Detecção de chuva (digital: SIM/NÃO)
- Imprime tudo formatado no Serial Monitor

## 📚 Próximas etapas do projeto (conforme plano de ensino)

- [ ] Adicionar conexão WiFi e envio dos dados via MQTT
- [ ] Desenvolver backend em Python para recepção e armazenamento
- [ ] Criar banco de dados para histórico das leituras
- [ ] Desenvolver dashboard web público
- [ ] Aplicar geometria analítica para geolocalização

## 🛒 Lista de materiais (hardware físico)

| Item | Função |
|---|---|
| ESP32 DevKit V1 | Microcontrolador |
| Sensor BME280 | Temperatura, umidade e pressão |
| Sensor MQ-135 | Qualidade do ar |
| Módulo LDR | Luminosidade |
| Módulo sensor de chuva | Detecção de chuva |
| Protoboard 830 pontos | Montagem do circuito |
| Kit jumpers (M-M, M-F, F-F) | Conexões |
| Kit resistores sortidos | Resistor pull-up |
| Módulo fonte MB102 | Alimentação da protoboard |
| Cabo Micro-USB | Programação do ESP32 |

---

Projeto desenvolvido para a disciplina de Projeto e Desenvolvimento II — Ciência da Computação.
