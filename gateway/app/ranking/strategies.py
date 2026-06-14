"""Estratégias de ordenação do ranking (Strategy Pattern)."""
from __future__ import annotations

from typing import Protocol


class RankingStrategy(Protocol):
    name: str

    def order(self, games: list[dict]) -> list[dict]:
        ...


class RankByRatingStrategy:
    """Ordena por melhor média de avaliação (e número de avaliações como desempate)."""

    name = "rating"

    def order(self, games: list[dict]) -> list[dict]:
        return sorted(
            games,
            key=lambda game: (game.get("average") or 0, game.get("reviewCount") or 0),
            reverse=True,
        )


class RankByRecentStrategy:
    """Ordena pelos lançamentos mais recentes."""

    name = "recent"

    def order(self, games: list[dict]) -> list[dict]:
        return sorted(games, key=lambda game: game.get("releaseYear") or 0, reverse=True)
