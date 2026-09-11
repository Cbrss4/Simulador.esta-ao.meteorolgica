# 📘 Manual do Projeto — Estação Meteorológica Inteligente

Simulação com ESP32, BME280, MQ-135, LDR e sensor de chuva.

Este manual explica, do zero, como o projeto funciona e como qualquer pessoa da equipe pode acessar, rodar e editar a simulação — mesmo sem experiência prévia em eletrônica ou programação.

---

## 1. Visão Geral do Projeto

Este projeto simula uma estação meteorológica inteligente utilizando um microcontrolador ESP32 e quatro sensores ambientais: temperatura/umidade/pressão (BME280), luminosidade (LDR), qualidade do ar (MQ-135) e detecção de chuva.

A simulação é feita através da ferramenta Wokwi, que permite testar o funcionamento do circuito e do código antes mesmo de montar o hardware físico. O projeto está organizado em um repositório no GitHub, o que permite que toda a equipe acesse, edite e acompanhe as mudanças do código de forma organizada.

### 1.1 O que você vai encontrar no repositório

| Arquivo/Pasta | O que é |
|---|---|
| `src/main.cpp` | Código-fonte do firmware (o que roda no ESP32) |
| `platformio.ini` | Arquivo de configuração do projeto (placa, bibliotecas) |
| `diagram.json` | Diagrama de ligação dos componentes na simulação |
| `wokwi.toml` | Configuração para a simulação encontrar o arquivo compilado |
| `.vscode/extensions.json` | Lista de extensões recomendadas do VS Code |
| `README.md` | Guia rápido de instalação e execução |

---

## 2. Como Acessar o Repositório

O repositório é privado — somente pessoas convidadas conseguem visualizar e baixar o projeto.

### 2.1 Se você já recebeu o convite

1. Você vai receber uma notificação por e-mail ou pelo GitHub avisando que foi adicionado como colaborador.
2. Clique no link do convite e faça login (ou crie uma conta gratuita no GitHub, se ainda não tiver).
3. Aceite o convite para ter acesso ao repositório.

### 2.2 Como baixar o projeto

1. Acesse a página do repositório no GitHub.
2. Clique no botão verde **"Code"**.
3. Clique em **"Download ZIP"** para baixar tudo de uma vez, ou copie o link e use `git clone` pelo terminal, se preferir.
4. Extraia o arquivo ZIP em uma pasta no seu computador.

---

## 3. Como Rodar a Simulação

Existem duas formas de simular o projeto. Escolha a que for mais prática para você.

### 3.1 Opção A — Pelo navegador (mais simples, recomendada)

Não exige nenhuma instalação no computador.

1. Acesse **https://wokwi.com** e crie uma conta gratuita (ou faça login).
2. Clique em **"New Project"** e escolha **"ESP32"**.
3. Abra o arquivo `sketch.ino` do novo projeto e substitua todo o conteúdo pelo conteúdo do arquivo `src/main.cpp` do repositório.
4. Abra o arquivo `diagram.json` do novo projeto e substitua pelo conteúdo do `diagram.json` do repositório.
5. No menu lateral, clique no ícone de biblioteca (Library Manager) e adicione: **"Adafruit BME280 Library"** e **"Adafruit Unified Sensor"**.
6. Clique no botão verde ▶️ **"Start Simulation"**.

O Serial Monitor deve abrir automaticamente, mostrando as leituras dos sensores a cada 2 segundos.

### 3.2 Opção B — Pelo VS Code (mais rápida no uso contínuo)

**Pré-requisitos:**
- VS Code instalado ([code.visualstudio.com](https://code.visualstudio.com))
- Python 3 instalado no computador
- Conta gratuita no Wokwi (para ativar a extensão)

**Passo 1 — Instalar as extensões**

No VS Code, vá em "Extensions" (ícone de quadrados na barra lateral) e instale:
- **PlatformIO IDE**
- **Wokwi Simulator**

**Passo 2 — Abrir o projeto**

1. Extraia o ZIP baixado do GitHub em uma pasta.
2. No VS Code, vá em `File → Open Folder` e selecione essa pasta.
3. O PlatformIO deve reconhecer automaticamente o arquivo `platformio.ini`.

**Passo 3 — Compilar o código**

1. Clique no ícone da formiguinha do PlatformIO, na barra lateral.
2. Em "PROJECT TASKS" → `esp32doit-devkit-v1` → "General", clique em **Build**.
3. Espere aparecer `[SUCCESS]` no terminal — isso confirma que o código compilou sem erros.

**Passo 4 — Rodar a simulação**

1. Aperte **F1** (ou Ctrl+Shift+P).
2. Digite `Wokwi: Start Simulator` e aperte Enter.
3. O diagrama visual e o Serial Monitor devem abrir automaticamente.

> ⚠️ **Problema comum no Linux:** se o PlatformIO travar pedindo o pacote `python3.X-venv`, rode o comando abaixo (ajustando a versão do Python se necessário):
> ```bash
> sudo apt install python3.12-venv -y
> ```

---

## 4. Como Confirmar que Está Funcionando

Depois de iniciar a simulação, o sinal de que tudo está certo é ver um texto se repetindo a cada 2 segundos no Serial Monitor, parecido com isto:

Iniciando Estação Meteorológica...
Sensores prontos!
---- Leitura da Estação ----
Temperatura: 24.00 °C
Umidade: 25.00 %
Pressão: 1013.25 hPa
Luminosidade (LDR): 2048
Qualidade do ar (MQ-135): 2048
Chuva detectada: NÃO


Se esse texto aparece e os números mudam a cada leitura, a simulação está funcionando corretamente.

### 4.1 Onde encontrar o Serial Monitor

Se o Serial Monitor não aparecer automaticamente:

1. Aperte **F1**.
2. Digite `Serial Monitor: Focus on View` e aperte Enter.
3. Se ainda não aparecer, vá em `View → Output` (ou Ctrl+Shift+U) e procure "Wokwi" no menu suspenso do painel.

### 4.2 Testando a interatividade

- Arraste o potenciômetro simulado (representa o MQ-135) — o valor de "Qualidade do ar" deve mudar.
- Clique na chave (switch) simulada (representa o sensor de chuva) — o valor de "Chuva detectada" deve alternar entre SIM e NÃO.

---

## 5. Entendendo o Código (sem jargão técnico)

O código roda em um ciclo repetido (chamado de "loop"): a cada 2 segundos, ele repete os mesmos 3 passos:

1. Pergunta para cada sensor qual é o valor atual (temperatura, umidade, pressão, luminosidade, qualidade do ar e chuva).
2. Guarda essas respostas em variáveis (como se fossem "gavetas" temporárias de memória).
3. Imprime tudo formatado no Serial Monitor, para você conseguir ler.

Não é necessário entender a sintaxe do código para usar o projeto — o manual até aqui já é suficiente para rodar e testar a simulação.

### 5.1 Diagrama de ligação (para quando o hardware físico chegar)

| Componente | Pino do ESP32 | Observação |
|---|---|---|
| BME280 — VCC | 3V3 | |
| BME280 — GND | GND | |
| BME280 — SDA | D21 | Comunicação I2C |
| BME280 — SCL | D22 | Comunicação I2C |
| LDR — VCC | 3V3 | |
| LDR — GND | GND | |
| LDR — AOUT | D34 | Entrada analógica |
| MQ-135 — VCC | 5V (fonte externa) | Consome corrente extra |
| MQ-135 — GND | GND | |
| MQ-135 — AOUT | D35 | Entrada analógica |
| Sensor de chuva — VCC | 3,3–5V | |
| Sensor de chuva — GND | GND | |
| Sensor de chuva — D0 | D32 | Saída digital |

---

## 6. Lista de Materiais (Hardware Físico)

| Item | Função |
|---|---|
| ESP32 DevKit V1 | Microcontrolador principal |
| Sensor BME280 | Temperatura, umidade e pressão atmosférica |
| Sensor MQ-135 | Qualidade do ar |
| Módulo LDR | Luminosidade |
| Módulo sensor de chuva | Detecção de chuva |
| Protoboard 830 pontos | Montagem do circuito sem solda |
| Kit jumpers (M-M, M-F, F-F) | Conexões entre os componentes |
| Kit resistores sortidos | Resistor pull-up (se usar sensores alternativos) |
| Módulo fonte MB102 | Alimentação da protoboard (3,3V/5V) |
| Cabo Micro-USB | Conexão e programação do ESP32 |

---

## 7. Perguntas Frequentes

**"Fiz uma alteração no código, e agora?"**
Salve o arquivo, rode o Build novamente (Passo 3 da seção 3.2) e inicie a simulação de novo (F1 → `Wokwi: Start Simulator`).

**"Posso editar direto pelo GitHub, sem baixar nada?"**
Sim, para pequenas alterações de texto (como o README), é possível editar diretamente pela interface web do GitHub, clicando no ícone de lápis ao lado do arquivo. Para testar a simulação, porém, é necessário usar o Wokwi (Opção A ou B da seção 3).

**"Como eu convido mais alguém para o repositório?"**
1. No repositório do GitHub, clique em "Settings".
2. No menu lateral, clique em "Collaborators".
3. Clique em "Add people" e digite o nome de usuário ou e-mail da pessoa.

**"O que fazer se a simulação não iniciar?"**
- Confirme que o Build (compilação) terminou com `[SUCCESS]` antes de iniciar a simulação.
- Confirme que o arquivo `wokwi.toml` aponta para o caminho correto: `.pio/build/esp32doit-devkit-v1/firmware.bin`
- Tente fechar e reabrir o VS Code, e rodar o Build novamente.

**"Preciso ter o hardware físico para usar este manual?"**
Não. Toda a simulação funciona 100% no computador, sem necessidade de nenhum componente físico. O hardware só é necessário na fase de montagem real do protótipo, mais adiante no projeto.

---

## 8. Próximas Etapas do Projeto

Conforme o plano de ensino da disciplina, as próximas evoluções previstas para este projeto incluem:

- Conexão WiFi e envio dos dados via protocolo MQTT
- Desenvolvimento de um backend em Python para recepção e armazenamento dos dados
- Criação de um banco de dados para histórico das leituras
- Desenvolvimento de um dashboard web público para visualização dos dados
- Aplicação de geometria analítica para geolocalização
- Montagem e testes do protótipo físico com o hardware real

---

*Este manual será atualizado conforme o projeto avançar para as próximas unidades do plano de ensino.*
