import json

import pytest
from pydantic import ValidationError

from app.models import ReadingPayloadV1


def valid_payload() -> dict[str, object]:
    return {
        "schema_version": 1,
        "device_id": "station-01",
        "captured_at": "2026-09-30T18:30:00Z",
        "temperature_c": 25.4,
        "humidity_pct": 61.2,
        "pressure_hpa": 1012.8,
        "gas_raw": 840,
        "light_detected": True,
        "rain_detected": False,
    }


def parse(payload: dict[str, object]) -> ReadingPayloadV1:
    return ReadingPayloadV1.model_validate_json(json.dumps(payload))


def test_valid_payload_is_accepted() -> None:
    reading = parse(valid_payload())

    assert reading.device_id == "station-01"
    assert reading.captured_at is not None
    assert reading.captured_at.utcoffset() is not None
    assert reading.reading_status == "valid"
    assert reading.is_partial is False


def test_missing_capture_time_does_not_make_sensor_reading_partial() -> None:
    payload = valid_payload()
    payload["captured_at"] = None

    reading = parse(payload)

    assert reading.captured_at is None
    assert reading.reading_status == "valid"


@pytest.mark.parametrize(
    "sensor_field",
    [
        "temperature_c",
        "humidity_pct",
        "pressure_hpa",
        "gas_raw",
        "light_detected",
        "rain_detected",
    ],
)
def test_null_sensor_value_makes_payload_partial(sensor_field: str) -> None:
    payload = valid_payload()
    payload[sensor_field] = None

    reading = parse(payload)

    assert reading.is_partial is True
    assert reading.reading_status == "partial"


@pytest.mark.parametrize(
    ("field", "invalid_value"),
    [
        ("schema_version", 2),
        ("device_id", "   "),
        ("captured_at", "2026-09-30T18:30:00"),
        ("temperature_c", "25.4"),
        ("humidity_pct", -0.1),
        ("humidity_pct", 100.1),
        ("gas_raw", 840.5),
        ("light_detected", 1),
    ],
)
def test_invalid_field_value_is_rejected(field: str, invalid_value: object) -> None:
    payload = valid_payload()
    payload[field] = invalid_value

    with pytest.raises(ValidationError):
        parse(payload)


def test_missing_required_field_is_rejected() -> None:
    payload = valid_payload()
    del payload["rain_detected"]

    with pytest.raises(ValidationError):
        parse(payload)


def test_extra_field_is_rejected() -> None:
    payload = valid_payload()
    payload["unexpected"] = "value"

    with pytest.raises(ValidationError):
        parse(payload)


def test_malformed_json_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ReadingPayloadV1.model_validate_json('{"schema_version": 1')
