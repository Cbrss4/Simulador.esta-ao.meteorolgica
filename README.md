# Software da estação meteorológica

Backend local da estação meteorológica, desenvolvido com Python e FastAPI.

## Preparar o ambiente

```powershell
uv sync
```

Copie o arquivo de exemplo para criar a configuração local:

```powershell
Copy-Item .env.example .env
```

O `.env` não é versionado. Os valores padrão usam o broker local em `127.0.0.1:1883`, tópico `weather/station-01/readings`, QoS 1 e banco `data/station.db`. Para a integração pela rede, altere somente o `.env` local; não coloque IP pessoal ou credenciais no Git.

## Executar os testes

```powershell
uv run pytest
```

## Executar a API

```powershell
uv run uvicorn app.main:app --reload
```

## Executar o assinante MQTT

Com o Mosquitto em execução e o `.env` configurado:

```powershell
uv run python -m app.mqtt_subscriber
```

O assinante usa MQTT 3.1.1, conecta ao broker configurado e assina `MQTT_TOPIC` com `MQTT_QOS`. Mensagens válidas e parciais são armazenadas; mensagens inválidas são rejeitadas com o motivo registrado no log, sem encerrar o serviço.

Com o servidor em execução, o endpoint de verificação fica disponível em:

```text
http://127.0.0.1:8000/health
```

Resposta esperada:

```json
{"status": "ok"}
```

O dashboard pode consultar a leitura válida ou parcial mais recente em:

```text
http://127.0.0.1:8000/api/v1/readings/latest
```

Enquanto o banco estiver vazio, esse endpoint responde com HTTP 404 e `{"detail": "Nenhuma leitura disponível"}`.

O histórico fica disponível em:

```text
http://127.0.0.1:8000/api/v1/readings
```

O parâmetro `limit` aceita valores de 1 a 500 e usa 100 por padrão. O histórico retorna somente leituras `valid` ou `partial`, da mais recente para a mais antiga. Banco vazio resulta em uma lista JSON vazia.

Uma leitura específica pode ser consultada pelo identificador:

```text
http://127.0.0.1:8000/api/v1/readings/1
```

Identificadores inexistentes retornam HTTP 404. O identificador deve ser um número inteiro maior que zero.

## Inicializar o banco local

```powershell
uv run python -m app.database
```

Por padrão, o banco é criado em `data/station.db`. Para usar outro caminho, defina `WEATHER_DATABASE_PATH` antes de executar o comando.

O arquivo SQLite é local e não deve ser versionado. A tabela `readings` segue a proposta de contrato aprovada por Tales e ainda poderá mudar após a revisão de Gabriel.

## Validação das mensagens

O modelo `ReadingPayloadV1`, em `app/models.py`, valida o JSON proposto para o ESP32 antes da persistência. Ele exige todos os campos do contrato versão 1, rejeita campos extras e tipos incorretos, exige fuso em `captured_at` quando houver horário e classifica como parcial uma mensagem com algum sensor igual a `null`.

O consumidor MQTT ainda não faz parte desta etapa. O modelo segue a proposta aprovada por Tales e poderá ser revisado após a manifestação de Gabriel.

## Persistência das leituras

A classe `ReadingRepository`, em `app/repository.py`, recebe somente mensagens já validadas pelo Pydantic. Ela gera `received_at`, normaliza os horários para UTC e grava a leitura como `valid` ou `partial` na tabela `readings`.

Os testes dessa camada usam bancos temporários. Nenhuma leitura fictícia é inserida em `data/station.db` durante a suíte.
