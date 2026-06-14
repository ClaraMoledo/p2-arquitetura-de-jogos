"""Repositório em memória — usado em testes e como fallback sem banco."""
from __future__ import annotations

from app.domain.entities import Game


class InMemoryGameRepository:
    def __init__(self) -> None:
        self._items: dict[str, Game] = {}

    def save(self, game: Game) -> None:
        self._items[game.id] = game

    def list_all(self) -> list[Game]:
        return list(self._items.values())
