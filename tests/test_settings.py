import pytest
from pydantic import ValidationError

from app.settings import Settings

ENVIRONMENT_KEYS = [
    "MQTT_HOST",
    "MQTT_PORT",
    "MQTT_TOPIC",
    "MQTT_QOS",
    "MQTT_KEEPALIVE",
    "WEATHER_DATABASE_PATH",
]


def clear_environment(monkeypatch) -> None:
    for key in ENVIRONMENT_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_settings_use_safe_local_defaults(monkeypatch) -> None:
    clear_environment(monkeypatch)

    settings = Settings(_env_file=None)

    assert settings.mqtt_host == "127.0.0.1"
    assert settings.mqtt_port == 1883
    assert settings.mqtt_topic == "weather/station-01/readings"
    assert settings.mqtt_qos == 1
    assert settings.mqtt_keepalive == 60
    assert settings.weather_database_path.as_posix() == "data/station.db"


def test_settings_accept_environment_overrides(monkeypatch, tmp_path) -> None:
    clear_environment(monkeypatch)
    database_path = tmp_path / "custom.db"
    monkeypatch.setenv("MQTT_HOST", "broker.local")
    monkeypatch.setenv("MQTT_PORT", "2883")
    monkeypatch.setenv("MQTT_TOPIC", "weather/station-02/readings")
    monkeypatch.setenv("MQTT_QOS", "0")
    monkeypatch.setenv("MQTT_KEEPALIVE", "30")
    monkeypatch.setenv("WEATHER_DATABASE_PATH", str(database_path))

    settings = Settings(_env_file=None)

    assert settings.mqtt_host == "broker.local"
    assert settings.mqtt_port == 2883
    assert settings.mqtt_topic == "weather/station-02/readings"
    assert settings.mqtt_qos == 0
    assert settings.mqtt_keepalive == 30
    assert settings.weather_database_path == database_path


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("MQTT_PORT", "0"),
        ("MQTT_PORT", "65536"),
        ("MQTT_QOS", "3"),
        ("MQTT_KEEPALIVE", "0"),
        ("MQTT_TOPIC", "weather/+/readings"),
        ("MQTT_TOPIC", "weather/#"),
    ],
)
def test_settings_reject_invalid_values(monkeypatch, key: str, value: str) -> None:
    clear_environment(monkeypatch)
    monkeypatch.setenv(key, value)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
