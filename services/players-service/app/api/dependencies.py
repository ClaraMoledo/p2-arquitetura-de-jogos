"""Provedores de dependência (injeção via FastAPI Depends).

Cada provider monta o caso de uso com seus repositórios concretos — é o
ponto onde a composição acontece, mantendo os casos de uso livres de infra.
"""
from __future__ import annotations

from app.infra.factory import (
    create_friendship_repository,
    create_library_repository,
    create_player_repository,
    create_wishlist_repository,
)
from app.use_cases.create_player import CreatePlayer
from app.use_cases.deposit_funds import DepositFunds
from app.use_cases.get_player import GetPlayer
from app.use_cases.list_library import ListLibrary
from app.use_cases.list_players import ListPlayers
from app.use_cases.manage_friends import AddFriend, ListFriends, RemoveFriend
from app.use_cases.manage_wishlist import AddToWishlist, ListWishlist, RemoveFromWishlist
from app.use_cases.purchase_game import PurchaseGame


def provide_create_player() -> CreatePlayer:
    return CreatePlayer(create_player_repository())


def provide_list_players() -> ListPlayers:
    return ListPlayers(create_player_repository())


def provide_get_player() -> GetPlayer:
    return GetPlayer(create_player_repository())


def provide_deposit_funds() -> DepositFunds:
    return DepositFunds(create_player_repository())


def provide_purchase_game() -> PurchaseGame:
    return PurchaseGame(
        create_player_repository(),
        create_library_repository(),
        create_wishlist_repository(),
    )


def provide_list_library() -> ListLibrary:
    return ListLibrary(create_library_repository())


def provide_add_to_wishlist() -> AddToWishlist:
    return AddToWishlist(
        create_player_repository(),
        create_wishlist_repository(),
        create_library_repository(),
    )


def provide_remove_from_wishlist() -> RemoveFromWishlist:
    return RemoveFromWishlist(create_wishlist_repository())


def provide_list_wishlist() -> ListWishlist:
    return ListWishlist(create_wishlist_repository())


def provide_add_friend() -> AddFriend:
    return AddFriend(create_player_repository(), create_friendship_repository())


def provide_remove_friend() -> RemoveFriend:
    return RemoveFriend(create_friendship_repository())


def provide_list_friends() -> ListFriends:
    return ListFriends(create_player_repository(), create_friendship_repository())
