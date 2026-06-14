"""Caso de uso: comprar um jogo da loja."""
from __future__ import annotations

from dataclasses import dataclass

from app.domain.entities import LibraryEntry, Player
from app.domain.exceptions import ConflictError, NotFoundError
from app.domain.repositories import (
    LibraryRepository,
    PlayerRepository,
    WishlistRepository,
)
from app.pricing.factory import create_pricing_policy
from app.pricing.strategies import PricedPurchase


@dataclass(frozen=True)
class PurchaseResult:
    player: Player
    entry: LibraryEntry
    pricing: PricedPurchase


class PurchaseGame:
    """
    Orquestra a compra de um jogo:

    1. valida que o jogador existe e ainda não tem o jogo;
    2. escolhe a política de preço conforme a fidelidade (Strategy + Factory);
    3. cobra a carteira (a regra de saldo mora na entidade Player);
    4. registra o jogo na biblioteca e o remove da lista de desejos.

    Depende só de abstrações (DIP) e tem uma única responsabilidade (SRP).
    """

    def __init__(
        self,
        players: PlayerRepository,
        library: LibraryRepository,
        wishlist: WishlistRepository,
    ) -> None:
        self._players = players
        self._library = library
        self._wishlist = wishlist

    def execute(self, *, player_id: str, game_id: str, title: str, base_price_cents: int) -> PurchaseResult:
        player = self._players.find_by_id(player_id)
        if player is None:
            raise NotFoundError("Jogador não encontrado.")

        if self._library.owns(player_id, game_id):
            raise ConflictError("Este jogo já está na sua biblioteca.")

        owned_count = len(self._library.list_by_player(player_id))
        policy = create_pricing_policy(owned_count)
        pricing = policy.price(base_price_cents)

        charged = player.charge(pricing.final_cents)
        entry = LibraryEntry.create(
            player_id=player_id,
            game_id=game_id,
            title=title,
            price_paid_cents=pricing.final_cents,
        )

        self._players.save(charged)
        self._library.save(entry)
        self._wishlist.remove(player_id, game_id)  # comprou: sai da lista de desejos

        return PurchaseResult(player=charged, entry=entry, pricing=pricing)
