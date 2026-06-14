"""Casos de uso de amizades: adicionar, remover e listar amigos."""
from __future__ import annotations

from app.domain.entities import Friendship, Player
from app.domain.exceptions import ConflictError, NotFoundError
from app.domain.repositories import FriendshipRepository, PlayerRepository


class AddFriend:
    def __init__(self, players: PlayerRepository, friendships: FriendshipRepository) -> None:
        self._players = players
        self._friendships = friendships

    def execute(self, *, player_id: str, friend_id: str) -> Friendship:
        if self._players.find_by_id(player_id) is None:
            raise NotFoundError("Jogador não encontrado.")
        if self._players.find_by_id(friend_id) is None:
            raise NotFoundError("O jogador que você quer adicionar não existe.")
        if self._friendships.exists(player_id, friend_id):
            raise ConflictError("Vocês já são amigos.")
        friendship = Friendship.create(player_id=player_id, friend_id=friend_id)
        self._friendships.save(friendship)
        return friendship


class RemoveFriend:
    def __init__(self, friendships: FriendshipRepository) -> None:
        self._friendships = friendships

    def execute(self, *, player_id: str, friend_id: str) -> None:
        if not self._friendships.remove(player_id, friend_id):
            raise NotFoundError("Vocês não são amigos.")


class ListFriends:
    """Lista os amigos de um jogador, já resolvendo o jogador do outro lado."""

    def __init__(self, players: PlayerRepository, friendships: FriendshipRepository) -> None:
        self._players = players
        self._friendships = friendships

    def execute(self, player_id: str) -> list[Player]:
        friends: list[Player] = []
        for friendship in self._friendships.list_by_player(player_id):
            other_id = friendship.other_side(player_id)
            other = self._players.find_by_id(other_id)
            if other is not None:
                friends.append(other)
        friends.sort(key=lambda p: p.name.lower())
        return friends
