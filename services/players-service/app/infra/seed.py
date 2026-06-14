"""Popular jogadores de demonstração (idempotente).

Os game_id usados aqui são os mesmos semeados no catalog-service, para que a
loja e a biblioteca já apareçam coerentes na primeira execução.
"""
from __future__ import annotations

from datetime import datetime, timezone

from .database import get_session_factory
from .models import FriendshipModel, LibraryEntryModel, PlayerModel, WishlistItemModel

_NOW = datetime.now(timezone.utc).isoformat()

_P1 = "c3000000-0000-0000-0000-000000000001"
_P2 = "c3000000-0000-0000-0000-000000000002"
_P3 = "c3000000-0000-0000-0000-000000000003"

_PLAYERS = [
    dict(id=_P1, name="Nova", wallet_cents=25000, created_at=_NOW),
    dict(id=_P2, name="Lumen", wallet_cents=12000, created_at=_NOW),
    dict(id=_P3, name="Pixel", wallet_cents=8000, created_at=_NOW),
]

_LIBRARY = [
    dict(id="d4000000-0000-0000-0000-000000000001", player_id=_P1,
         game_id="a1000000-0000-0000-0000-000000000001", title="Aurora Frontier",
         price_paid_cents=16915, purchased_at=_NOW),
    dict(id="d4000000-0000-0000-0000-000000000002", player_id=_P1,
         game_id="a1000000-0000-0000-0000-000000000004", title="Pixel Raiders",
         price_paid_cents=4900, purchased_at=_NOW),
    dict(id="d4000000-0000-0000-0000-000000000003", player_id=_P2,
         game_id="a1000000-0000-0000-0000-000000000003", title="Mistveil Chronicles",
         price_paid_cents=13515, purchased_at=_NOW),
]

_WISHLIST = [
    dict(id="e5000000-0000-0000-0000-000000000001", player_id=_P1,
         game_id="a1000000-0000-0000-0000-000000000005", title="Stellar Drift", added_at=_NOW),
    dict(id="e5000000-0000-0000-0000-000000000002", player_id=_P3,
         game_id="a1000000-0000-0000-0000-000000000002", title="Neon Circuit", added_at=_NOW),
]

_FRIENDSHIPS = [
    dict(id="f6000000-0000-0000-0000-000000000001", player_id=_P1, friend_id=_P2, created_at=_NOW),
]


def seed() -> None:
    session_factory = get_session_factory()
    with session_factory() as session:
        if session.query(PlayerModel).count() > 0:
            return
        session.add_all(PlayerModel(**row) for row in _PLAYERS)
        session.add_all(LibraryEntryModel(**row) for row in _LIBRARY)
        session.add_all(WishlistItemModel(**row) for row in _WISHLIST)
        session.add_all(FriendshipModel(**row) for row in _FRIENDSHIPS)
        session.commit()
