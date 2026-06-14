"""Entidades de domínio do catálogo de jogos."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from .exceptions import DomainError

_MIN_YEAR = 1958  # primeiro videogame conhecido


@dataclass(frozen=True)
class Game:
    """
    Jogo do catálogo.

    Entidade pura: concentra as regras de negócio e não conhece banco,
    framework web ou qualquer detalhe de infraestrutura.
    """

    id: str
    title: str
    genre: str
    platform: str
    price_cents: int
    release_year: int
    available: bool

    @staticmethod
    def create(
        title: str,
        genre: str,
        platform: str,
        price_cents: int,
        release_year: int,
        available: bool = True,
    ) -> "Game":
        clean_title = (title or "").strip()
        if len(clean_title) < 2:
            raise DomainError("O título do jogo deve ter ao menos 2 caracteres.")

        if not isinstance(price_cents, int) or isinstance(price_cents, bool) or price_cents < 0:
            raise DomainError("O preço deve ser um inteiro em centavos, maior ou igual a zero.")

        max_year = datetime.now().year + 1
        if not isinstance(release_year, int) or release_year < _MIN_YEAR or release_year > max_year:
            raise DomainError(f"Ano de lançamento deve estar entre {_MIN_YEAR} e {max_year}.")

        return Game(
            id=str(uuid4()),
            title=clean_title,
            genre=(genre or "").strip() or "Indefinido",
            platform=(platform or "").strip() or "Multiplataforma",
            price_cents=price_cents,
            release_year=release_year,
            available=available,
        )

    @staticmethod
    def restore(
        *,
        id: str,
        title: str,
        genre: str,
        platform: str,
        price_cents: int,
        release_year: int,
        available: bool,
    ) -> "Game":
        """Reidrata a entidade a partir de dados já persistidos (sem revalidar)."""
        return Game(
            id=id,
            title=title,
            genre=genre,
            platform=platform,
            price_cents=price_cents,
            release_year=release_year,
            available=available,
        )
