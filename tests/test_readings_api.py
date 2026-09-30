import json
from datetime import datetime
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app, get_repository
from app.models import ReadingPayloadV1
from app.repository import MAX_HISTORY_LIMIT, ReadingRepository


def make_reading() -> ReadingPayloadV1:
    payload = {
        "schema_version": 1,
        "device_id": "station-01",
        "captured_at": None,
        "temperature_c": 25.4,
        "humidity_pct": 61.2,
        "pressure_hpa": 1012.8,
        "gas_raw": None,
        "light_detected": True,
        "rain_detected": False,
    }
    return ReadingPayloadV1.model_validate_json(json.dumps(payload))


@pytest.fixture
def api_client(tmp_path) -> Iterator[tuple[TestClient, ReadingRepository]]:
    repository = ReadingRepository(tmp_path / "test.db")
    app.dependency_overrides[get_repository] = lambda: repository

    try:
        with TestClient(app) as client:
            yield client, repository
    finally:
        app.dependency_overrides.pop(get_repository, None)


def test_latest_returns_404_when_no_reading_exists(api_client) -> None:
    client, _ = api_client

    response = client.get("/api/v1/readings/latest")

    assert response.status_code == 404
    assert response.json() == {"detail": "Nenhuma leitura disponível"}


def test_latest_returns_most_recent_reading(api_client) -> None:
    client, repository = api_client
    reading_id = repository.save(
        make_reading(),
        received_at=datetime.fromisoformat("2026-09-30T18:30:00Z"),
    )

    response = client.get("/api/v1/readings/latest")

    assert response.status_code == 200
    assert response.json() == {
        "id": reading_id,
        "schema_version": 1,
        "device_id": "station-01",
        "captured_at": None,
        "received_at": "2026-09-30T18:30:00Z",
        "temperature_c": 25.4,
        "humidity_pct": 61.2,
        "pressure_hpa": 1012.8,
        "gas_raw": None,
        "light_detected": True,
        "rain_detected": False,
        "status": "partial",
        "validation_error": None,
    }


def test_history_returns_empty_list_when_no_reading_exists(api_client) -> None:
    client, _ = api_client

    response = client.get("/api/v1/readings")

    assert response.status_code == 200
    assert response.json() == []


def test_history_returns_limited_readings_in_descending_order(api_client) -> None:
    client, repository = api_client
    older_id = repository.save(
        make_reading(),
        received_at=datetime.fromisoformat("2026-09-30T18:00:00Z"),
    )
    latest_id = repository.save(
        make_reading(),
        received_at=datetime.fromisoformat("2026-09-30T19:00:00Z"),
    )

    response = client.get("/api/v1/readings", params={"limit": 1})

    assert response.status_code == 200
    body = response.json()
    assert [reading["id"] for reading in body] == [latest_id]
    assert older_id not in [reading["id"] for reading in body]


@pytest.mark.parametrize("limit", [0, MAX_HISTORY_LIMIT + 1])
def test_history_rejects_limit_outside_allowed_range(api_client, limit: int) -> None:
    client, _ = api_client

    response = client.get("/api/v1/readings", params={"limit": limit})

    assert response.status_code == 422


def test_reading_by_id_returns_existing_reading(api_client) -> None:
    client, repository = api_client
    reading_id = repository.save(
        make_reading(),
        received_at=datetime.fromisoformat("2026-09-30T18:30:00Z"),
    )

    response = client.get(f"/api/v1/readings/{reading_id}")

    assert response.status_code == 200
    assert response.json()["id"] == reading_id
    assert response.json()["device_id"] == "station-01"


def test_reading_by_id_returns_404_for_unknown_id(api_client) -> None:
    client, _ = api_client

    response = client.get("/api/v1/readings/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Leitura não encontrada"}


@pytest.mark.parametrize("reading_id", [0, -1])
def test_reading_by_id_rejects_non_positive_id(api_client, reading_id: int) -> None:
    client, _ = api_client

    response = client.get(f"/api/v1/readings/{reading_id}")

    assert response.status_code == 422
