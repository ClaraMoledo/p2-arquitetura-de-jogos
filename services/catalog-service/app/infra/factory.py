"""Factory de repositório: SQLAlchemy quando há banco; memória caso contrário."""
from __future__ import annotations

from app.domain.repositories import GameRepository

from .memory import InMemoryGameRepository
from .settings import settings


def create_game_repository() -> GameRepository:
    if settings.database_url:
        # Import tardio: evita carregar SQLAlchemy quando rodamos só em memória.
        from .sql_repository import SqlGameRepository

        return SqlGameRepository()
    return InMemoryGameRepository()
