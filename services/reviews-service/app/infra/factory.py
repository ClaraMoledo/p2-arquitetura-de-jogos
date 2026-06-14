"""Factory de repositório de avaliações."""
from __future__ import annotations

from app.domain.repositories import ReviewRepository

from .memory import InMemoryReviewRepository
from .settings import settings


def create_review_repository() -> ReviewRepository:
    if settings.database_url:
        from .sql_repository import SqlReviewRepository

        return SqlReviewRepository()
    return InMemoryReviewRepository()
