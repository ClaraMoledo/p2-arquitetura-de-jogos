"""Casos de uso da lista de desejos: adicionar, remover e listar."""
from __future__ import annotations

from app.domain.entities import WishlistItem
from app.domain.exceptions import ConflictError, NotFoundError
from app.domain.repositories import (
    LibraryRepository,
    PlayerRepository,
    WishlistRepository,
)


class AddToWishlist:
    def __init__(
        self,
        players: PlayerRepository,
        wishlist: WishlistRepository,
        library: LibraryRepository,
    ) -> None:
        self._players = players
        self._wishlist = wishlist
        self._library = library

    def execute(self, *, player_id: str, game_id: str, title: str) -> WishlistItem:
        if self._players.find_by_id(player_id) is None:
            raise NotFoundError("Jogador não encontrado.")
        if self._library.owns(player_id, game_id):
            raise ConflictError("Você já tem este jogo na biblioteca.")
        if self._wishlist.exists(player_id, game_id):
            raise ConflictError("Este jogo já está na sua lista de desejos.")
        item = WishlistItem.create(player_id=player_id, game_id=game_id, title=title)
        self._wishlist.save(item)
        return item


class RemoveFromWishlist:
    def __init__(self, wishlist: WishlistRepository) -> None:
        self._wishlist = wishlist

    def execute(self, *, player_id: str, game_id: str) -> None:
        if not self._wishlist.remove(player_id, game_id):
            raise NotFoundError("Este jogo não está na sua lista de desejos.")


class ListWishlist:
    def __init__(self, wishlist: WishlistRepository) -> None:
        self._wishlist = wishlist

    def execute(self, player_id: str) -> list[WishlistItem]:
        return self._wishlist.list_by_player(player_id)
