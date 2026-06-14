"""Portas de persistência do domínio dos jogadores (Repository Pattern).

A aplicação depende apenas destas abstrações; as implementações concretas
(SQLAlchemy, memória) vivem na camada de infraestrutura — Inversão de
Dependência (o "D" de SOLID).
"""
from __future__ import annotations

from typing import Protocol

from .entities import Friendship, LibraryEntry, Player, WishlistItem


class PlayerRepository(Protocol):
    def save(self, player: Player) -> None:
        ...

    def list_all(self) -> list[Player]:
        ...

    def find_by_id(self, player_id: str) -> Player | None:
        ...


class LibraryRepository(Protocol):
    def save(self, entry: LibraryEntry) -> None:
        ...

    def list_by_player(self, player_id: str) -> list[LibraryEntry]:
        ...

    def owns(self, player_id: str, game_id: str) -> bool:
        ...


class WishlistRepository(Protocol):
    def save(self, item: WishlistItem) -> None:
        ...

    def list_by_player(self, player_id: str) -> list[WishlistItem]:
        ...

    def exists(self, player_id: str, game_id: str) -> bool:
        ...

    def remove(self, player_id: str, game_id: str) -> bool:
        ...


class FriendshipRepository(Protocol):
    def save(self, friendship: Friendship) -> None:
        ...

    def list_by_player(self, player_id: str) -> list[Friendship]:
        ...

    def exists(self, player_id: str, friend_id: str) -> bool:
        ...

    def remove(self, player_id: str, friend_id: str) -> bool:
        ...
