"""Caso de uso: calcular a média de notas por jogo."""
from __future__ import annotations

from collections import defaultdict

from app.domain.repositories import ReviewRepository


class ComputeAverages:
    def __init__(self, repository: ReviewRepository) -> None:
        self._repository = repository

    def execute(self) -> list[dict]:
        reviews = self._repository.list_all()
        totals: dict[str, int] = defaultdict(int)
        counts: dict[str, int] = defaultdict(int)

        for review in reviews:
            totals[review.game_id] += review.rating
            counts[review.game_id] += 1

        return [
            {"gameId": game_id, "average": round(totals[game_id] / count, 1), "count": count}
            for game_id, count in counts.items()
        ]
