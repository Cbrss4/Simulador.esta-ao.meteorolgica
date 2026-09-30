import json
from contextlib import closing
from datetime import datetime

import pytest

from app.database import connect_database
from app.models import ReadingPayloadV1
from app.repository import MAX_HISTORY_LIMIT, ReadingRepository


def make_reading(**overrides: object) -> ReadingPayloadV1:
    payload: dict[str, object] = {
        "schema_version": 1,
        "device_id": "station-01",
        "captured_at": "2026-09-30T15:30:00-03:00",
        "temperature_c": 25.4,
        "humidity_pct": 61.2,
        "pressure_hpa": 1012.8,
        "gas_raw": 840,
        "light_detected": True,
        "rain_detected": False,
    }
    payload.update(overrides)
    return ReadingPayloadV1.model_validate_json(json.dumps(payload))


def test_save_valid_reading_with_utc_timestamps(tmp_path) -> None:
    database_path = tmp_path / "test.db"
    repository = ReadingRepository(database_path)
    reading = make_reading()
    received_at = datetime.fromisoformat("2026-09-30T12:00:00-03:00")

    reading_id = repository.save(reading, received_at=received_at)

    with closing(connect_database(database_path)) as connection:
        row = connection.execute(
            "SELECT * FROM readings WHERE id = ?", (reading_id,)
        ).fetchone()

    assert row is not None
    assert row["captured_at"] == "2026-09-30T18:30:00Z"
    assert row["received_at"] == "2026-09-30T15:00:00Z"
    assert row["status"] == "valid"
    assert row["light_detected"] == 1
    assert row["rain_detected"] == 0
    assert row["validation_error"] is None


def test_save_partial_reading(tmp_path) -> None:
    database_path = tmp_path / "test.db"
    repository = ReadingRepository(database_path)
    reading = make_reading(gas_raw=None, captured_at=None)

    reading_id = repository.save(
        reading,
        received_at=datetime.fromisoformat("2026-09-30T18:30:00Z"),
    )

    with closing(connect_database(database_path)) as connection:
        row = connection.execute(
            "SELECT * FROM readings WHERE id = ?", (reading_id,)
        ).fetchone()

    assert row is not None
    assert row["captured_at"] is None
    assert row["gas_raw"] is None
    assert row["status"] == "partial"


def test_save_rejects_received_at_without_timezone(tmp_path) -> None:
    database_path = tmp_path / "test.db"
    repository = ReadingRepository(database_path)

    with pytest.raises(ValueError, match="fuso horário"):
        repository.save(make_reading(), received_at=datetime(2026, 9, 30, 18, 30))

    with closing(connect_database(database_path)) as connection:
        count = connection.execute("SELECT COUNT(*) FROM readings").fetchone()[0]

    assert count == 0


def test_get_latest_returns_none_when_database_is_empty(tmp_path) -> None:
    repository = ReadingRepository(tmp_path / "test.db")

    assert repository.get_latest() is None


def test_get_latest_orders_by_received_at_and_ignores_invalid(tmp_path) -> None:
    database_path = tmp_path / "test.db"
    repository = ReadingRepository(database_path)

    latest_id = repository.save(
        make_reading(temperature_c=30.0),
        received_at=datetime.fromisoformat("2026-09-30T20:00:00Z"),
    )
    repository.save(
        make_reading(temperature_c=20.0),
        received_at=datetime.fromisoformat("2026-09-30T19:00:00Z"),
    )

    with closing(connect_database(database_path)) as connection:
        connection.execute(
            """
            INSERT INTO readings (
                schema_version, device_id, received_at, status, validation_error
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (1, "station-01", "2026-09-30T21:00:00Z", "invalid", "teste"),
        )
        connection.commit()

    reading = repository.get_latest()

    assert reading is not None
    assert reading.id == latest_id
    assert reading.temperature_c == 30.0
    assert reading.status == "valid"


def test_list_readings_returns_empty_list_when_database_is_empty(tmp_path) -> None:
    repository = ReadingRepository(tmp_path / "test.db")

    assert repository.list_readings() == []


def test_list_readings_orders_limits_and_ignores_invalid(tmp_path) -> None:
    database_path = tmp_path / "test.db"
    repository = ReadingRepository(database_path)

    repository.save(
        make_reading(temperature_c=10.0),
        received_at=datetime.fromisoformat("2026-09-30T18:00:00Z"),
    )
    middle_id = repository.save(
        make_reading(temperature_c=20.0, gas_raw=None),
        received_at=datetime.fromisoformat("2026-09-30T19:00:00Z"),
    )
    latest_id = repository.save(
        make_reading(temperature_c=30.0),
        received_at=datetime.fromisoformat("2026-09-30T20:00:00Z"),
    )

    with closing(connect_database(database_path)) as connection:
        connection.execute(
            """
            INSERT INTO readings (
                schema_version, device_id, received_at, status, validation_error
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (1, "station-01", "2026-09-30T21:00:00Z", "invalid", "teste"),
        )
        connection.commit()

    readings = repository.list_readings(limit=2)

    assert [reading.id for reading in readings] == [latest_id, middle_id]
    assert [reading.status for reading in readings] == ["valid", "partial"]


@pytest.mark.parametrize("limit", [0, MAX_HISTORY_LIMIT + 1])
def test_list_readings_rejects_limit_outside_allowed_range(
    tmp_path, limit: int
) -> None:
    repository = ReadingRepository(tmp_path / "test.db")

    with pytest.raises(ValueError, match="limit deve estar entre"):
        repository.list_readings(limit=limit)


def test_get_by_id_returns_existing_reading(tmp_path) -> None:
    repository = ReadingRepository(tmp_path / "test.db")
    reading_id = repository.save(
        make_reading(temperature_c=27.5),
        received_at=datetime.fromisoformat("2026-09-30T20:00:00Z"),
    )

    reading = repository.get_by_id(reading_id)

    assert reading is not None
    assert reading.id == reading_id
    assert reading.temperature_c == 27.5


def test_get_by_id_returns_none_for_unknown_id(tmp_path) -> None:
    repository = ReadingRepository(tmp_path / "test.db")

    assert repository.get_by_id(999) is None


@pytest.mark.parametrize("reading_id", [0, -1])
def test_get_by_id_rejects_non_positive_id(tmp_path, reading_id: int) -> None:
    repository = ReadingRepository(tmp_path / "test.db")

    with pytest.raises(ValueError, match="maior que zero"):
        repository.get_by_id(reading_id)
