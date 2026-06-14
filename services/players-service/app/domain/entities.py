"""Entidades de domínio dos jogadores: perfil, carteira, biblioteca, amizades."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from .exceptions import DomainError

_WELCOME_BONUS_CENTS = 5000  # R$ 50,00 de boas-vindas na criação da conta


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Player:
    """
    Jogador da plataforma.

    Entidade imutável: as operações de carteira devolvem uma nova instância
    em vez de mutar o objeto. As regras de saldo moram aqui (Tell, Don't Ask),
    nunca nos casos de uso ou na API.
    """

    id: str
    name: str
    wallet_cents: int
    created_at: str

    @staticmethod
    def create(name: str) -> "Player":
        clean = (name or "").strip()
        if len(clean) < 2:
            raise DomainError("O apelido do jogador deve ter ao menos 2 caracteres.")
        return Player(
            id=str(uuid4()),
            name=clean,
            wallet_cents=_WELCOME_BONUS_CENTS,
            created_at=_now(),
        )

    @staticmethod
    def restore(*, id: str, name: str, wallet_cents: int, created_at: str) -> "Player":
        return Player(id=id, name=name, wallet_cents=wallet_cents, created_at=created_at)

    def deposit(self, amount_cents: int) -> "Player":
        if not isinstance(amount_cents, int) or isinstance(amount_cents, bool) or amount_cents <= 0:
            raise DomainError("O valor do depósito deve ser um inteiro em centavos maior que zero.")
        return self._with_wallet(self.wallet_cents + amount_cents)

    def charge(self, amount_cents: int) -> "Player":
        if not isinstance(amount_cents, int) or isinstance(amount_cents, bool) or amount_cents < 0:
            raise DomainError("O valor da cobrança é inválido.")
        if amount_cents > self.wallet_cents:
            raise DomainError("Saldo insuficiente na carteira. Adicione fundos para concluir a compra.")
        return self._with_wallet(self.wallet_cents - amount_cents)

    def _with_wallet(self, wallet_cents: int) -> "Player":
        return Player(
            id=self.id,
            name=self.name,
            wallet_cents=wallet_cents,
            created_at=self.created_at,
        )


@dataclass(frozen=True)
class LibraryEntry:
    """Jogo que o jogador comprou. Guarda um instantâneo do título e do preço pago."""

    id: str
    player_id: str
    game_id: str
    title: str
    price_paid_cents: int
    purchased_at: str

    @staticmethod
    def create(*, player_id: str, game_id: str, title: str, price_paid_cents: int) -> "LibraryEntry":
        if not (player_id or "").strip():
            raise DomainError("A compra precisa referenciar um jogador.")
        if not (game_id or "").strip():
            raise DomainError("A compra precisa referenciar um jogo.")
        if not isinstance(price_paid_cents, int) or isinstance(price_paid_cents, bool) or price_paid_cents < 0:
            raise DomainError("O preço pago deve ser um inteiro em centavos maior ou igual a zero.")
        return LibraryEntry(
            id=str(uuid4()),
            player_id=player_id.strip(),
            game_id=game_id.strip(),
            title=(title or "").strip() or "Jogo sem título",
            price_paid_cents=price_paid_cents,
            purchased_at=_now(),
        )

    @staticmethod
    def restore(
        *, id: str, player_id: str, game_id: str, title: str, price_paid_cents: int, purchased_at: str
    ) -> "LibraryEntry":
        return LibraryEntry(
            id=id,
            player_id=player_id,
            game_id=game_id,
            title=title,
            price_paid_cents=price_paid_cents,
            purchased_at=purchased_at,
        )


@dataclass(frozen=True)
class WishlistItem:
    """Jogo que o jogador marcou como desejado (ainda não comprado)."""

    id: str
    player_id: str
    game_id: str
    title: str
    added_at: str

    @staticmethod
    def create(*, player_id: str, game_id: str, title: str) -> "WishlistItem":
        if not (player_id or "").strip():
            raise DomainError("O desejo precisa referenciar um jogador.")
        if not (game_id or "").strip():
            raise DomainError("O desejo precisa referenciar um jogo.")
        return WishlistItem(
            id=str(uuid4()),
            player_id=player_id.strip(),
            game_id=game_id.strip(),
            title=(title or "").strip() or "Jogo sem título",
            added_at=_now(),
        )

    @staticmethod
    def restore(*, id: str, player_id: str, game_id: str, title: str, added_at: str) -> "WishlistItem":
        return WishlistItem(id=id, player_id=player_id, game_id=game_id, title=title, added_at=added_at)


@dataclass(frozen=True)
class Friendship:
    """Amizade entre dois jogadores (relação simétrica)."""

    id: str
    player_id: str
    friend_id: str
    created_at: str

    @staticmethod
    def create(*, player_id: str, friend_id: str) -> "Friendship":
        left = (player_id or "").strip()
        right = (friend_id or "").strip()
        if not left or not right:
            raise DomainError("A amizade precisa de dois jogadores.")
        if left == right:
            raise DomainError("Um jogador não pode adicionar a si mesmo como amigo.")
        return Friendship(id=str(uuid4()), player_id=left, friend_id=right, created_at=_now())

    @staticmethod
    def restore(*, id: str, player_id: str, friend_id: str, created_at: str) -> "Friendship":
        return Friendship(id=id, player_id=player_id, friend_id=friend_id, created_at=created_at)

    def involves(self, player_id: str) -> bool:
        return player_id in (self.player_id, self.friend_id)

    def other_side(self, player_id: str) -> str:
        return self.friend_id if player_id == self.player_id else self.player_id
