# Evidências da entrega S2

## Fluxo testado

Em 30/09/2026, foi executado localmente o caminho completo da mensagem:

```text
mosquitto_pub → Mosquitto → assinante Python → Pydantic → SQLite → FastAPI
```

Foi usado um banco descartável, separado do banco de desenvolvimento e removido depois da execução.

## Ambiente

| Componente | Versão ou estado |
|---|---|
| Python | 3.12.13 |
| `uv` | 0.10.12 |
| Eclipse Mosquitto | 2.1.2 |
| Serviço Mosquitto | Em execução, com inicialização automática |
| Paho MQTT | 2.1.0 |
| Protocolo | MQTT 3.1.1 |
| Tópico | `weather/station-01/readings` |
| QoS | 1 |

## Testes automatizados

Comando:

```powershell
uv run pytest -q
```

Resultado:

```text
66 passed, 1 warning in 1.68s
```

Os testes verificam:

- criação e restrições do banco SQLite;
- validação de mensagens válidas, parciais e inválidas;
- armazenamento e horários em UTC;
- leitura atual, histórico e consulta por ID;
- configurações e processamento MQTT.

O aviso é de depreciação na integração entre `fastapi.testclient` e HTTPX e não causou falhas.

## Teste integrado

| Caso | Resultado |
|---|---|
| Conexão MQTT | O assinante conectou a `127.0.0.1:1883` e assinou o tópico com QoS 1 |
| Mensagem válida | Armazenada como ID 1, com status `valid`, e retornada pela API |
| Horário | `received_at` gerado em UTC pelo backend |
| Mensagem parcial | `gas_raw: null`, armazenada como ID 2 e status `partial` |
| Histórico | IDs 2 e 1 retornados do mais recente para o mais antigo |
| Mensagem inválida | Umidade igual a 150 rejeitada e registrada no log |
| Continuidade | A API continuou respondendo depois da rejeição |
| Isolamento | Banco de desenvolvimento preservado e banco descartável removido |

## Repetição manual

Para conferir o procedimento do README, o teste foi repetido com o banco separado `data/s2-print.db`. Uma mensagem fictícia foi publicada com `mosquitto_pub`, recebida pelo assinante, armazenada como ID 1 e consultada pela API com resposta HTTP 200.

No Windows PowerShell, a publicação foi feita assim:

```powershell
$payload | & 'C:\Program Files\mosquitto\mosquitto_pub.exe' -h 127.0.0.1 -p 1883 -t 'weather/station-01/readings' -q 1 -s
```

![Leitura manual de teste retornada pela API](evidencias/api-leitura-json.png)

Os dados da imagem são fictícios e foram publicados manualmente para testar o caminho entre MQTT, banco de dados e API. O ESP32 e os sensores não participaram desse teste.

## Cuidados com os arquivos locais

O `.env`, os bancos SQLite, a `.venv` e os caches não são versionados. Os testes automatizados usam bancos temporários.

## O que ainda falta testar

- publicação pelo ESP32 e leitura dos sensores físicos;
- funcionamento pela rede do hotspot;
- acesso ao broker e à API por outro dispositivo;
- regras de firewall para acesso externo ao notebook;
- queda e reconexão real do broker;
- calibração e precisão física dos sensores.

O contrato MQTT ainda aguarda a revisão de Gabriel.
