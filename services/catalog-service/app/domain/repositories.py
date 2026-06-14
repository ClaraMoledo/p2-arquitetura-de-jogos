"""Portas (interfaces) de persistência do domínio."""
from __future__ import annotations

from typing import Protocol

from .entities import Game


class GameRepository(Protocol):
    """
    Repository Pattern. O domínio depende desta abstração; as implementações
    concretas (SQLAlchemy, memória) vivem na camada de infraestrutura.
    """

    def save(self, game: Game) -> None:
        ...

    def list_all(self) -> list[Game]:
        ...
