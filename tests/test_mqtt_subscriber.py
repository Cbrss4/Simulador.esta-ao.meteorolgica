import json
import logging
from contextlib import closing
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.database import connect_database
from app.mqtt_subscriber import MqttMessageProcessor, MqttSubscriber
from app.repository import ReadingRepository
from app.settings import Settings


def payload_bytes(**overrides: object) -> bytes:
    payload: dict[str, object] = {
        "schema_version": 1,
        "device_id": "station-01",
        "captured_at": None,
        "temperature_c": 25.4,
        "humidity_pct": 61.2,
        "pressure_hpa": 1012.8,
        "gas_raw": 840,
        "light_detected": True,
        "rain_detected": False,
    }
    payload.update(overrides)
    return json.dumps(payload).encode("utf-8")


def test_processor_stores_valid_message(tmp_path) -> None:
    database_path = tmp_path / "test.db"
    processor = MqttMessageProcessor(ReadingRepository(database_path))

    result = processor.process(payload_bytes())

    assert result.accepted is True
    assert result.reading_id is not None
    assert result.reading_status == "valid"

    with closing(connect_database(database_path)) as connection:
        row = connection.execute(
            "SELECT * FROM readings WHERE id = ?", (result.reading_id,)
        ).fetchone()

    assert row is not None
    assert row["device_id"] == "station-01"
    assert row["status"] == "valid"


def test_processor_stores_partial_message(tmp_path) -> None:
    database_path = tmp_path / "test.db"
    processor = MqttMessageProcessor(ReadingRepository(database_path))

    result = processor.process(payload_bytes(gas_raw=None))

    assert result.accepted is True
    assert result.reading_status == "partial"

    with closing(connect_database(database_path)) as connection:
        row = connection.execute(
            "SELECT * FROM readings WHERE id = ?", (result.reading_id,)
        ).fetchone()

    assert row is not None
    assert row["gas_raw"] is None
    assert row["status"] == "partial"


@pytest.mark.parametrize(
    "payload",
    [
        b'{"schema_version": 1',
        payload_bytes(schema_version=2),
        payload_bytes(humidity_pct=150),
        b"\xff\xfe\xfd",
    ],
)
def test_processor_rejects_invalid_message_without_persisting(
    tmp_path, payload: bytes, caplog
) -> None:
    database_path = tmp_path / "test.db"
    processor = MqttMessageProcessor(ReadingRepository(database_path))

    with caplog.at_level(logging.WARNING):
        result = processor.process(payload)

    assert result.accepted is False
    assert result.reading_id is None
    assert result.error
    assert "Mensagem MQTT rejeitada" in caplog.text

    with closing(connect_database(database_path)) as connection:
        count = connection.execute("SELECT COUNT(*) FROM readings").fetchone()[0]

    assert count == 0


def test_subscriber_subscribes_after_successful_connection(tmp_path) -> None:
    settings = Settings(_env_file=None)
    processor = MqttMessageProcessor(ReadingRepository(tmp_path / "test.db"))
    client = Mock()
    MqttSubscriber(settings, processor, client=client)

    client.on_connect(client, None, None, 0, None)

    client.subscribe.assert_called_once_with(
        "weather/station-01/readings",
        qos=1,
    )


def test_subscriber_does_not_subscribe_when_connection_is_refused(tmp_path) -> None:
    settings = Settings(_env_file=None)
    processor = MqttMessageProcessor(ReadingRepository(tmp_path / "test.db"))
    client = Mock()
    MqttSubscriber(settings, processor, client=client)

    client.on_connect(client, None, None, 1, None)

    client.subscribe.assert_not_called()


def test_subscriber_forwards_received_payload_to_processor(tmp_path) -> None:
    settings = Settings(_env_file=None)
    processor = Mock()
    client = Mock()
    MqttSubscriber(settings, processor, client=client)
    message = SimpleNamespace(payload=payload_bytes())

    client.on_message(client, None, message)

    processor.process.assert_called_once_with(message.payload)


def test_run_forever_uses_configured_connection(tmp_path) -> None:
    settings = Settings(
        mqtt_host="broker.local",
        mqtt_port=2883,
        mqtt_keepalive=30,
        _env_file=None,
    )
    processor = MqttMessageProcessor(ReadingRepository(tmp_path / "test.db"))
    client = Mock()
    subscriber = MqttSubscriber(settings, processor, client=client)

    subscriber.run_forever()

    client.connect.assert_called_once_with("broker.local", 2883, 30)
    client.loop_forever.assert_called_once_with(retry_first_connection=True)
