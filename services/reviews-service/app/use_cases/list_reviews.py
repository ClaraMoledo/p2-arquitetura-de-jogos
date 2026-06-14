"""Caso de uso: listar avaliações (de um jogo ou todas)."""
from __future__ import annotations

from app.domain.entities import Review
from app.domain.repositories import ReviewRepository


class ListReviews:
    def __init__(self, repository: ReviewRepository) -> None:
        self._repository = repository

    def execute(self, game_id: str | None = None) -> list[Review]:
        if game_id:
            return self._repository.list_by_game(game_id)
        return self._repository.list_all()
