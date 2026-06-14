"""Repositórios em memória — usados nos testes e como fallback sem banco."""
from __future__ import annotations

from app.domain.entities import Friendship, LibraryEntry, Player, WishlistItem


class InMemoryPlayerRepository:
    def __init__(self) -> None:
        self._items: dict[str, Player] = {}

    def save(self, player: Player) -> None:
        self._items[player.id] = player

    def list_all(self) -> list[Player]:
        return sorted(self._items.values(), key=lambda p: p.name.lower())

    def find_by_id(self, player_id: str) -> Player | None:
        return self._items.get(player_id)


class InMemoryLibraryRepository:
    def __init__(self) -> None:
        self._items: list[LibraryEntry] = []

    def save(self, entry: LibraryEntry) -> None:
        self._items.append(entry)

    def list_by_player(self, player_id: str) -> list[LibraryEntry]:
        return [entry for entry in self._items if entry.player_id == player_id]

    def owns(self, player_id: str, game_id: str) -> bool:
        return any(e.player_id == player_id and e.game_id == game_id for e in self._items)


class InMemoryWishlistRepository:
    def __init__(self) -> None:
        self._items: list[WishlistItem] = []

    def save(self, item: WishlistItem) -> None:
        self._items.append(item)

    def list_by_player(self, player_id: str) -> list[WishlistItem]:
        return [item for item in self._items if item.player_id == player_id]

    def exists(self, player_id: str, game_id: str) -> bool:
        return any(i.player_id == player_id and i.game_id == game_id for i in self._items)

    def remove(self, player_id: str, game_id: str) -> bool:
        before = len(self._items)
        self._items = [
            i for i in self._items if not (i.player_id == player_id and i.game_id == game_id)
        ]
        return len(self._items) < before


class InMemoryFriendshipRepository:
    def __init__(self) -> None:
        self._items: list[Friendship] = []

    def save(self, friendship: Friendship) -> None:
        self._items.append(friendship)

    def list_by_player(self, player_id: str) -> list[Friendship]:
        return [f for f in self._items if f.involves(player_id)]

    def exists(self, player_id: str, friend_id: str) -> bool:
        return any(self._same_pair(f, player_id, friend_id) for f in self._items)

    def remove(self, player_id: str, friend_id: str) -> bool:
        before = len(self._items)
        self._items = [f for f in self._items if not self._same_pair(f, player_id, friend_id)]
        return len(self._items) < before

    @staticmethod
    def _same_pair(friendship: Friendship, a: str, b: str) -> bool:
        return {friendship.player_id, friendship.friend_id} == {a, b}
