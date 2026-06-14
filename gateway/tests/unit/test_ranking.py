"""Testes das estratégias de ranking (Strategy)."""
from app.ranking.factory import create_ranking_strategy

GAMES = [
    {"id": "1", "title": "A", "releaseYear": 2020, "average": 4.0, "reviewCount": 2},
    {"id": "2", "title": "B", "releaseYear": 2024, "average": 5.0, "reviewCount": 1},
    {"id": "3", "title": "C", "releaseYear": 2022, "average": None, "reviewCount": 0},
]


def test_ranking_por_nota():
    ordered = create_ranking_strategy("rating").order(GAMES)
    assert [game["id"] for game in ordered] == ["2", "1", "3"]


def test_ranking_por_lancamento():
    ordered = create_ranking_strategy("recent").order(GAMES)
    assert [game["id"] for game in ordered] == ["2", "3", "1"]


def test_estrategia_padrao_e_por_nota():
    assert create_ranking_strategy(None).name == "rating"
    assert create_ranking_strategy("desconhecida").name == "rating"
