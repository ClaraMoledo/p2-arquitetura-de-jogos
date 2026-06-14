"""Rotas HTTP do serviço de jogadores (adaptadores de entrada)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.domain.entities import Friendship, LibraryEntry, Player, WishlistItem
from app.use_cases.create_player import CreatePlayer
from app.use_cases.deposit_funds import DepositFunds
from app.use_cases.get_player import GetPlayer
from app.use_cases.list_library import ListLibrary
from app.use_cases.list_players import ListPlayers
from app.use_cases.manage_friends import AddFriend, ListFriends, RemoveFriend
from app.use_cases.manage_wishlist import AddToWishlist, ListWishlist, RemoveFromWishlist
from app.use_cases.purchase_game import PurchaseGame, PurchaseResult

from . import dependencies as deps
from .schemas import DepositIn, FriendIn, PlayerIn, PurchaseIn, WishlistIn

router = APIRouter()


def _player_dict(player: Player) -> dict:
    return {
        "id": player.id,
        "name": player.name,
        "walletCents": player.wallet_cents,
        "createdAt": player.created_at,
    }


def _library_dict(entry: LibraryEntry) -> dict:
    return {
        "id": entry.id,
        "playerId": entry.player_id,
        "gameId": entry.game_id,
        "title": entry.title,
        "pricePaidCents": entry.price_paid_cents,
        "purchasedAt": entry.purchased_at,
    }


def _wishlist_dict(item: WishlistItem) -> dict:
    return {
        "id": item.id,
        "playerId": item.player_id,
        "gameId": item.game_id,
        "title": item.title,
        "addedAt": item.added_at,
    }


# ----- Jogadores -----------------------------------------------------------
@router.get("/players")
def list_players(use_case: ListPlayers = Depends(deps.provide_list_players)) -> dict:
    return {"data": [_player_dict(p) for p in use_case.execute()]}


@router.post("/players", status_code=status.HTTP_201_CREATED)
def create_player(payload: PlayerIn, use_case: CreatePlayer = Depends(deps.provide_create_player)) -> dict:
    return {"data": _player_dict(use_case.execute(name=payload.name))}


@router.get("/players/{player_id}")
def get_player(player_id: str, use_case: GetPlayer = Depends(deps.provide_get_player)) -> dict:
    return {"data": _player_dict(use_case.execute(player_id))}


@router.post("/players/{player_id}/deposit")
def deposit(
    player_id: str,
    payload: DepositIn,
    use_case: DepositFunds = Depends(deps.provide_deposit_funds),
) -> dict:
    player = use_case.execute(player_id=player_id, amount_cents=payload.amountCents)
    return {"data": _player_dict(player)}


# ----- Loja / Biblioteca ---------------------------------------------------
@router.post("/players/{player_id}/purchases", status_code=status.HTTP_201_CREATED)
def purchase(
    player_id: str,
    payload: PurchaseIn,
    use_case: PurchaseGame = Depends(deps.provide_purchase_game),
) -> dict:
    result: PurchaseResult = use_case.execute(
        player_id=player_id,
        game_id=payload.gameId,
        title=payload.title or "",
        base_price_cents=payload.basePriceCents,
    )
    return {
        "data": {
            "entry": _library_dict(result.entry),
            "wallet": {"walletCents": result.player.wallet_cents},
            "pricing": {
                "baseCents": result.pricing.base_cents,
                "finalCents": result.pricing.final_cents,
                "discountCents": result.pricing.discount_cents,
                "policy": result.pricing.policy,
                "label": result.pricing.label,
            },
        }
    }


@router.get("/players/{player_id}/library")
def library(player_id: str, use_case: ListLibrary = Depends(deps.provide_list_library)) -> dict:
    return {"data": [_library_dict(e) for e in use_case.execute(player_id)]}


# ----- Lista de desejos ----------------------------------------------------
@router.get("/players/{player_id}/wishlist")
def list_wishlist(player_id: str, use_case: ListWishlist = Depends(deps.provide_list_wishlist)) -> dict:
    return {"data": [_wishlist_dict(i) for i in use_case.execute(player_id)]}


@router.post("/players/{player_id}/wishlist", status_code=status.HTTP_201_CREATED)
def add_wishlist(
    player_id: str,
    payload: WishlistIn,
    use_case: AddToWishlist = Depends(deps.provide_add_to_wishlist),
) -> dict:
    item = use_case.execute(player_id=player_id, game_id=payload.gameId, title=payload.title or "")
    return {"data": _wishlist_dict(item)}


@router.delete("/players/{player_id}/wishlist/{game_id}")
def remove_wishlist(
    player_id: str,
    game_id: str,
    use_case: RemoveFromWishlist = Depends(deps.provide_remove_from_wishlist),
) -> dict:
    use_case.execute(player_id=player_id, game_id=game_id)
    return {"data": {"removed": True}}


# ----- Amigos --------------------------------------------------------------
@router.get("/players/{player_id}/friends")
def list_friends(player_id: str, use_case: ListFriends = Depends(deps.provide_list_friends)) -> dict:
    return {"data": [_player_dict(p) for p in use_case.execute(player_id)]}


@router.post("/players/{player_id}/friends", status_code=status.HTTP_201_CREATED)
def add_friend(
    player_id: str,
    payload: FriendIn,
    use_case: AddFriend = Depends(deps.provide_add_friend),
) -> dict:
    friendship: Friendship = use_case.execute(player_id=player_id, friend_id=payload.friendId)
    return {"data": {"id": friendship.id, "playerId": friendship.player_id, "friendId": friendship.friend_id}}


@router.delete("/players/{player_id}/friends/{friend_id}")
def remove_friend(
    player_id: str,
    friend_id: str,
    use_case: RemoveFriend = Depends(deps.provide_remove_friend),
) -> dict:
    use_case.execute(player_id=player_id, friend_id=friend_id)
    return {"data": {"removed": True}}
