# Estação Meteorológica Inteligente

Projeto integrador da disciplina Projeto e Desenvolvimento II, do segundo semestre de Ciência da Computação.

Esta primeira sprint apresenta um protótipo virtual da estação meteorológica. O objetivo é validar o circuito lógico, o firmware do ESP32 e a integração das leituras antes da aquisição e montagem dos componentes físicos.

## Estado da S1

O simulador realiza leituras a cada dois segundos de:

- temperatura;
- umidade;
- pressão atmosférica;
- luminosidade;
- qualidade do ar simulada;
- presença de chuva.

O firmware foi compilado com sucesso e as seis leituras foram confirmadas no monitor serial. Consulte [ENTREGA_S1.md](ENTREGA_S1.md) para ver o resultado, as limitações e o checklist da sprint.

**[Abrir a simulação pronta no Wokwi](https://wokwi.com/projects/474895435837456385)**

Para uma avaliação rápida, basta abrir o link, clicar no botão verde de iniciar e acompanhar as leituras no monitor serial. Não é necessário instalar o VS Code, o PlatformIO ou a extensão local do Wokwi.

![Simulação do circuito e saída serial](evidencias/simulacao-wokwi-funcionando.png)

## Componentes da simulação

O protótipo físico previsto no escopo utiliza BME280, MQ-135, LDR e módulo sensor de chuva. Como nem todos estão disponíveis de forma nativa no Wokwi, esta simulação utiliza componentes equivalentes para validar o fluxo do programa.

| Variável | Protótipo físico | Simulação Wokwi |
|---|---|---|
| Temperatura e umidade | BME280 | DHT22 |
| Pressão atmosférica | BME280 | BMP180 |
| Luminosidade | Módulo LDR | Módulo LDR |
| Qualidade do ar | MQ-135 | Potenciômetro |
| Presença de chuva | Módulo de chuva | Chave deslizante |

Essas equivalências não substituem a calibração, os testes elétricos ou a avaliação de precisão com o hardware real.

## Estrutura

```text
├── README.md
├── ENTREGA_S1.md
├── evidencias/
│   └── simulacao-wokwi-funcionando.png
├── diagrama-fluxo-codigo.svg
├── diagrama-ligacao.svg
└── repo-estacao/
    ├── src/
    │   └── main.cpp
    ├── .gitignore
    ├── diagram.json
    ├── platformio.ini
    └── wokwi.toml
```

O `diagrama-ligacao.svg` representa o protótipo físico planejado. O circuito efetivamente usado na simulação está em `repo-estacao/diagram.json`.

## Pré-requisitos

Para executar pelo link do Wokwi no navegador, é necessário apenas um navegador com acesso à internet.

Os itens abaixo são necessários somente para executar a cópia local:

- Visual Studio Code;
- extensão PlatformIO IDE;
- extensão Wokwi Simulator;
- Community License gratuita do Wokwi ativa.

Não é necessário adquirir uma licença paga para executar a S1 online no VS Code.

## Como executar

### Pelo navegador (recomendado para avaliação)

1. Abra [Estação Meteorológica — S1 no Wokwi](https://wokwi.com/projects/474895435837456385).
2. Clique no botão verde `Start the simulation`.
3. Aguarde a compilação e acompanhe as leituras no monitor serial.

### Localmente no VS Code

1. Abra especificamente a pasta `repo-estacao` no VS Code.
2. No PlatformIO, execute `PROJECT TASKS → esp32doit-devkit-v1 → General → Build`.
3. Aguarde a mensagem `[SUCCESS]`.
4. Pressione `F1` e execute `Wokwi: Start Simulator`.
5. Acompanhe as leituras no terminal chamado `Wokwi Terminal`.

O arquivo `.pio/build/esp32doit-devkit-v1/firmware.bin` é criado pelo Build. Se o Wokwi informar que o firmware não foi encontrado, compile novamente antes de iniciar o simulador.

### Terminal vazio no Windows

Com o simulador aberto e visível, execute em um terminal PowerShell:

```powershell
& "C:\Users\tales\.platformio\penv\Scripts\pio.exe" device monitor --port "rfc2217://localhost:4000" --baud 115200
```

Use `Ctrl+C` para encerrar o monitor.

## Como testar

- Altere temperatura e umidade no DHT22 e confira a próxima leitura.
- Altere a pressão no BMP180.
- Ajuste o LDR e observe a leitura de luminosidade.
- Gire o potenciômetro que representa o MQ-135.
- Mova a chave e confirme a alternância de chuva entre `SIM` e `NÃO`.

Valores inválidos de temperatura, umidade ou pressão são identificados no terminal. Caso o BMP180 não seja encontrado, o firmware informa o problema e mantém as demais leituras em funcionamento.

## Próximas etapas

- aquisição e teste isolado dos sensores físicos;
- montagem em protoboard;
- integração do BME280, MQ-135, LDR e módulo de chuva reais;
- conexão Wi-Fi e envio por MQTT;
- API em Python, banco SQLite e dashboard web;
- testes de campo e calibração.

Esses itens fazem parte das próximas sprints e não são apresentados como concluídos na S1.
