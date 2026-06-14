"""Caso de uso: obter um jogador pelo identificador."""
from __future__ import annotations

from app.domain.entities import Player
from app.domain.exceptions import NotFoundError
from app.domain.repositories import PlayerRepository


class GetPlayer:
    def __init__(self, repository: PlayerRepository) -> None:
        self._repository = repository

    def execute(self, player_id: str) -> Player:
        player = self._repository.find_by_id(player_id)
        if player is None:
            raise NotFoundError("Jogador não encontrado.")
        return player
