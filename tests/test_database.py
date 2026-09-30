import sqlite3
from contextlib import closing

import pytest

from app.database import DATABASE_VERSION, connect_database, initialize_database


EXPECTED_COLUMNS = [
    "id",
    "schema_version",
    "device_id",
    "captured_at",
    "received_at",
    "temperature_c",
    "humidity_pct",
    "pressure_hpa",
    "gas_raw",
    "light_detected",
    "rain_detected",
    "status",
    "validation_error",
]


def test_initialize_database_creates_versioned_readings_table(tmp_path) -> None:
    database_path = tmp_path / "nested" / "test.db"

    initialized_path = initialize_database(database_path)
    initialize_database(database_path)

    assert initialized_path == database_path
    assert database_path.exists()

    with closing(connect_database(database_path)) as connection:
        columns = connection.execute("PRAGMA table_info(readings)").fetchall()
        database_version = connection.execute("PRAGMA user_version").fetchone()[0]

    assert [column["name"] for column in columns] == EXPECTED_COLUMNS
    assert database_version == DATABASE_VERSION


def test_readings_table_accepts_initial_contract_values(tmp_path) -> None:
    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    with closing(connect_database(database_path)) as connection:
        connection.execute(
            """
            INSERT INTO readings (
                schema_version,
                device_id,
                captured_at,
                received_at,
                temperature_c,
                humidity_pct,
                pressure_hpa,
                gas_raw,
                light_detected,
                rain_detected,
                status,
                validation_error
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                1,
                "station-01",
                None,
                "2026-09-30T18:30:00Z",
                25.4,
                61.2,
                1012.8,
                840,
                1,
                0,
                "valid",
                None,
            ),
        )

        row = connection.execute("SELECT * FROM readings").fetchone()

    assert row is not None
    assert row["device_id"] == "station-01"
    assert row["captured_at"] is None
    assert row["light_detected"] == 1
    assert row["rain_detected"] == 0


@pytest.mark.parametrize(
    ("humidity_pct", "status"),
    [(-0.1, "valid"), (100.1, "valid"), (50.0, "unknown")],
)
def test_readings_table_rejects_invalid_constraints(
    tmp_path, humidity_pct: float, status: str
) -> None:
    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    with closing(connect_database(database_path)) as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO readings (
                    schema_version,
                    device_id,
                    received_at,
                    humidity_pct,
                    status
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (1, "station-01", "2026-09-30T18:30:00Z", humidity_pct, status),
            )
