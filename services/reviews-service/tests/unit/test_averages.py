"""Teste do cálculo de médias (TDD)."""
from app.infra.memory import InMemoryReviewRepository
from app.use_cases.add_review import AddReview
from app.use_cases.compute_averages import ComputeAverages


def test_calcula_media_por_jogo():
    repository = InMemoryReviewRepository()
    add = AddReview(repository)
    add.execute(game_id="g1", author="Ana", rating=5)
    add.execute(game_id="g1", author="Bia", rating=3)
    add.execute(game_id="g2", author="Caio", rating=4)

    averages = {item["gameId"]: item for item in ComputeAverages(repository).execute()}

    assert averages["g1"]["average"] == 4.0
    assert averages["g1"]["count"] == 2
    assert averages["g2"]["average"] == 4.0
    assert averages["g2"]["count"] == 1
