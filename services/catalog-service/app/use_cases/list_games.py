"""Caso de uso: listar os jogos do catálogo."""
from __future__ import annotations

from app.domain.entities import Game
from app.domain.repositories import GameRepository


class ListGames:
    def __init__(self, repository: GameRepository) -> None:
        self._repository = repository

    def execute(self) -> list[Game]:
        return self._repository.list_all()
