from functools import lru_cache
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, Query, status

from app.models import ReadingRecord
from app.repository import (
    DEFAULT_HISTORY_LIMIT,
    MAX_HISTORY_LIMIT,
    ReadingRepository,
)

app = FastAPI(title="Estação Meteorológica", version="0.1.0")


@lru_cache
def get_repository() -> ReadingRepository:
    return ReadingRepository()


RepositoryDependency = Annotated[ReadingRepository, Depends(get_repository)]


@app.get("/health")
def health() -> dict[str, str]:
    """Confirma que a API está em execução."""
    return {"status": "ok"}


@app.get("/api/v1/readings/latest", response_model=ReadingRecord)
def latest_reading(repository: RepositoryDependency) -> ReadingRecord:
    reading = repository.get_latest()
    if reading is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma leitura disponível",
        )
    return reading


@app.get("/api/v1/readings", response_model=list[ReadingRecord])
def reading_history(
    repository: RepositoryDependency,
    limit: int = Query(
        default=DEFAULT_HISTORY_LIMIT,
        ge=1,
        le=MAX_HISTORY_LIMIT,
    ),
) -> list[ReadingRecord]:
    return repository.list_readings(limit=limit)


@app.get("/api/v1/readings/{reading_id}", response_model=ReadingRecord)
def reading_by_id(
    repository: RepositoryDependency,
    reading_id: int = Path(gt=0),
) -> ReadingRecord:
    reading = repository.get_by_id(reading_id)
    if reading is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leitura não encontrada",
        )
    return reading
