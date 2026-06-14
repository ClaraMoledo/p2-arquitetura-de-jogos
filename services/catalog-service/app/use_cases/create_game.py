"""Caso de uso: cadastrar um jogo no catálogo."""
from __future__ import annotations

from app.domain.entities import Game
from app.domain.repositories import GameRepository


class CreateGame:
    """Orquestra a criação de um jogo. Depende apenas da abstração (DIP)."""

    def __init__(self, repository: GameRepository) -> None:
        self._repository = repository

    def execute(
        self,
        *,
        title: str,
        genre: str,
        platform: str,
        price_cents: int,
        release_year: int,
    ) -> Game:
        game = Game.create(title, genre, platform, price_cents, release_year)
        self._repository.save(game)
        return game
