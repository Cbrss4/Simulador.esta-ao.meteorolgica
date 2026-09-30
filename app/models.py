from datetime import datetime
from typing import Annotated, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

DeviceId = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ReadingPayloadV1(BaseModel):
    """Payload MQTT proposto para a versão 1 do contrato de dados."""

    model_config = ConfigDict(extra="forbid", strict=True)

    schema_version: Literal[1]
    device_id: DeviceId
    captured_at: datetime | None
    temperature_c: float | None
    humidity_pct: float | None = Field(ge=0, le=100)
    pressure_hpa: float | None
    gas_raw: int | None
    light_detected: bool | None
    rain_detected: bool | None

    sensor_fields: ClassVar[tuple[str, ...]] = (
        "temperature_c",
        "humidity_pct",
        "pressure_hpa",
        "gas_raw",
        "light_detected",
        "rain_detected",
    )

    @field_validator("captured_at")
    @classmethod
    def require_timezone_when_captured_at_is_available(
        cls, value: datetime | None
    ) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("captured_at deve informar UTC ou um fuso horário")
        return value

    @property
    def is_partial(self) -> bool:
        """Indica se pelo menos uma leitura de sensor está indisponível."""
        return any(getattr(self, field) is None for field in self.sensor_fields)

    @property
    def reading_status(self) -> Literal["valid", "partial"]:
        return "partial" if self.is_partial else "valid"


class ReadingRecord(BaseModel):
    """Leitura armazenada e devolvida pela API."""

    model_config = ConfigDict(extra="forbid")

    id: int
    schema_version: int
    device_id: str
    captured_at: datetime | None
    received_at: datetime
    temperature_c: float | None
    humidity_pct: float | None
    pressure_hpa: float | None
    gas_raw: int | None
    light_detected: bool | None
    rain_detected: bool | None
    status: Literal["valid", "partial", "invalid"]
    validation_error: str | None
