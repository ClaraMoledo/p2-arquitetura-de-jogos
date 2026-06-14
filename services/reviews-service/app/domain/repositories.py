"""Porta de persistência de avaliações (Repository Pattern)."""
from __future__ import annotations

from typing import Protocol

from .entities import Review


class ReviewRepository(Protocol):
    def save(self, review: Review) -> None:
        ...

    def list_by_game(self, game_id: str) -> list[Review]:
        ...

    def list_all(self) -> list[Review]:
        ...
