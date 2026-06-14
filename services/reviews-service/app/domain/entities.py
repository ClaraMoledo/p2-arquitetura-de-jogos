"""Entidade de domínio: avaliação de um jogo."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from .exceptions import DomainError


@dataclass(frozen=True)
class Review:
    id: str
    game_id: str
    author: str
    rating: int
    comment: str
    created_at: str

    @staticmethod
    def create(game_id: str, author: str, rating: int, comment: str = "") -> "Review":
        clean_game = (game_id or "").strip()
        if not clean_game:
            raise DomainError("A avaliação precisa referenciar um jogo.")

        clean_author = (author or "").strip()
        if len(clean_author) < 2:
            raise DomainError("Informe quem está avaliando (mínimo 2 caracteres).")

        if not isinstance(rating, int) or isinstance(rating, bool) or rating < 1 or rating > 5:
            raise DomainError("A nota deve ser um número inteiro de 1 a 5.")

        return Review(
            id=str(uuid4()),
            game_id=clean_game,
            author=clean_author,
            rating=rating,
            comment=(comment or "").strip(),
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    def restore(
        *,
        id: str,
        game_id: str,
        author: str,
        rating: int,
        comment: str,
        created_at: str,
    ) -> "Review":
        return Review(
            id=id,
            game_id=game_id,
            author=author,
            rating=rating,
            comment=comment,
            created_at=created_at,
        )
