"""Repositório em memória — testes e fallback sem banco."""
from __future__ import annotations

from app.domain.entities import Review


class InMemoryReviewRepository:
    def __init__(self) -> None:
        self._items: list[Review] = []

    def save(self, review: Review) -> None:
        self._items.append(review)

    def list_by_game(self, game_id: str) -> list[Review]:
        return [review for review in self._items if review.game_id == game_id]

    def list_all(self) -> list[Review]:
        return list(self._items)
