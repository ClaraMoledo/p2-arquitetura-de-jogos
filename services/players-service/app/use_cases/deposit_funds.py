"""Caso de uso: adicionar fundos à carteira do jogador."""
from __future__ import annotations

from app.domain.entities import Player
from app.domain.exceptions import NotFoundError
from app.domain.repositories import PlayerRepository


class DepositFunds:
    def __init__(self, repository: PlayerRepository) -> None:
        self._repository = repository

    def execute(self, *, player_id: str, amount_cents: int) -> Player:
        player = self._repository.find_by_id(player_id)
        if player is None:
            raise NotFoundError("Jogador não encontrado.")
        updated = player.deposit(amount_cents)  # a regra de saldo mora na entidade
        self._repository.save(updated)
        return updated
