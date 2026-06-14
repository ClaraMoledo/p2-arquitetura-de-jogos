"""Caso de uso: criar um jogador."""
from __future__ import annotations

from app.domain.entities import Player
from app.domain.repositories import PlayerRepository


class CreatePlayer:
    def __init__(self, repository: PlayerRepository) -> None:
        self._repository = repository

    def execute(self, *, name: str) -> Player:
        player = Player.create(name)
        self._repository.save(player)
        return player
