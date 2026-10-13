from pathlib import Path
from typing import Annotated

from pydantic import Field, StringConstraints, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Settings(BaseSettings):
    """Configuração local carregada do ambiente ou de um arquivo `.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    mqtt_host: NonEmptyText = "127.0.0.1"
    mqtt_port: int = Field(default=1883, ge=1, le=65535)
    mqtt_topic: NonEmptyText = "weather/station-01/readings"
    mqtt_qos: int = Field(default=1, ge=0, le=2)
    mqtt_keepalive: int = Field(default=60, ge=1, le=65535)
    weather_database_path: Path = Path("data/station.db")

    @field_validator("mqtt_topic")
    @classmethod
    def require_concrete_topic(cls, value: str) -> str:
        if "+" in value or "#" in value:
            raise ValueError("MQTT_TOPIC deve ser um tópico concreto, sem curingas")
        return value
