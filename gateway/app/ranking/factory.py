"""Factory que escolhe a estratégia de ranking."""
from __future__ import annotations

from .strategies import RankByRatingStrategy, RankByRecentStrategy, RankingStrategy

_STRATEGIES = {
    "rating": RankByRatingStrategy,
    "recent": RankByRecentStrategy,
}


def create_ranking_strategy(by: str | None) -> RankingStrategy:
    strategy_cls = _STRATEGIES.get((by or "rating").lower(), RankByRatingStrategy)
    return strategy_cls()
