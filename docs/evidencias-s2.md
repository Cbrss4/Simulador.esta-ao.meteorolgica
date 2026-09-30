# Evidências técnicas da entrega S2

## Escopo comprovado

O teste realizado em 2026-09-30 comprovou localmente o fluxo:

```text
mosquitto_pub → Mosquitto → assinante Python → Pydantic → SQLite → FastAPI
```

O teste utilizou um banco descartável separado do banco de desenvolvimento. O arquivo descartável foi removido após a execução.

## Ambiente verificado

| Componente | Versão ou estado observado |
|---|---|
| Python | 3.12.13 |
| `uv` | 0.10.12 |
| Eclipse Mosquitto | 2.1.2 |
| Serviço Mosquitto | Em execução, inicialização automática |
| Paho MQTT | 2.1.0 |
| Protocolo | MQTT 3.1.1 |
| Tópico | `weather/station-01/readings` |
| QoS | 1 |

## Testes automatizados

Comando executado:

```powershell
uv run pytest -q
```

Resultado observado:

```text
66 passed, 1 warning in 1.60s
```

O aviso é uma depreciação proveniente da integração entre `fastapi.testclient` e HTTPX. Ele não provocou falha nos testes.

Os testes cobrem:

- esquema e restrições do SQLite;
- validação de payload válido, parcial e inválido;
- persistência e horários em UTC;
- leitura atual, histórico e consulta por ID;
- limites e erros da API;
- configurações MQTT;
- processamento de mensagens MQTT sem broker real;
- rejeição de JSON malformado, versão incompatível, umidade inválida e bytes não UTF-8.

## Teste integrado local

| Caso | Evidência observada | Resultado |
|---|---|---|
| Conexão MQTT | Assinante conectou a `127.0.0.1:1883` e assinou o tópico com QoS 1 | Aprovado |
| Mensagem válida | Persistida como ID 1 e status `valid`; retornada pela API | Aprovado |
| Horário de recebimento | `received_at` gerado em UTC pelo backend | Aprovado |
| Mensagem parcial | `gas_raw: null`, persistida como ID 2 e status `partial` | Aprovado |
| Histórico | IDs 2 e 1 retornados do mais recente para o mais antigo | Aprovado |
| Mensagem inválida | `humidity_pct: 150` rejeitada e motivo exibido no log | Aprovado |
| Banco após rejeição | Histórico permaneceu com duas mensagens aceitas | Aprovado |
| Continuidade | `/health` respondeu HTTP 200 após a mensagem inválida | Aprovado |
| Isolamento | `data/station.db` preservado; banco descartável removido | Aprovado |

## Reprodução manual por Tales

Tales repetiu o fluxo em 2026-09-30 usando um banco separado, `data/s2-print.db`. Uma única mensagem fictícia foi publicada com `mosquitto_pub`, recebida no tópico MQTT, armazenada como ID 1 com status `valid` e consultada em `GET /api/v1/readings/latest` com resposta HTTP 200.

No Windows PowerShell, o JSON precisa ser enviado pela entrada padrão do `mosquitto_pub`:

```powershell
$validPayload | & 'C:\Program Files\mosquitto\mosquitto_pub.exe' -h 127.0.0.1 -p 1883 -t 'weather/station-01/readings' -q 1 -s
```

A tentativa anterior com `-m $validPayload` perdeu as aspas internas ao chamar o executável e foi rejeitada corretamente pela validação. O README foi corrigido para usar `-s`.

![Leitura manual de teste retornada pela API](evidencias/api-leitura-json.png)

Esta imagem mostra dados fictícios do teste. Ela não comprova leitura do ESP32 nem dos sensores físicos. Prints dos terminais não foram incluídos para evitar divulgar o usuário e os caminhos locais do computador.

## Versionamento

| Commit | Conteúdo |
|---|---|
| `cdd362e` | Fundação da API e do SQLite |
| `ac194b0` | Dependências e configuração MQTT |
| `bd3002f` | Assinante MQTT com validação e persistência |
| `379a1b7` | Procedimento local da S2 no README |

O repositório estava sem alterações pendentes após o commit `379a1b7`, antes da revisão final do README e destas evidências.

## Segurança e isolamento

- `.env` não é versionado.
- `.venv/`, caches e bancos SQLite são ignorados pelo Git.
- `.env.example` contém somente valores locais fictícios.
- Nenhuma senha, credencial ou IP pessoal foi incluído no código.
- Os testes automatizados usam bancos descartáveis.

## Limites não comprovados

- ESP32 e firmware não foram testados neste fluxo.
- Sensores físicos não foram lidos.
- Hotspot e acesso por outro dispositivo não foram testados.
- Firewall para acesso externo ao notebook não foi validado.
- Queda e reconexão real do broker ainda não foram testadas.
- O contrato MQTT aguarda revisão de Gabriel.
- Não há evidência de calibração ou precisão física dos sensores.
