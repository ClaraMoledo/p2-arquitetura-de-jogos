"""Caso de uso: listar jogadores."""
from __future__ import annotations

from app.domain.entities import Player
from app.domain.repositories import PlayerRepository


class ListPlayers:
    def __init__(self, repository: PlayerRepository) -> None:
        self._repository = repository

    def execute(self) -> list[Player]:
        return self._repository.list_all()
