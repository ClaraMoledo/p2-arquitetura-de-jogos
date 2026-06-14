"""Testes unitários da entidade Review (TDD)."""
import pytest

from app.domain.entities import Review
from app.domain.exceptions import DomainError


def test_cria_avaliacao_valida():
    review = Review.create("game-1", "Marina", 5, "Ótimo jogo!")
    assert review.id
    assert review.game_id == "game-1"
    assert review.rating == 5
    assert review.author == "Marina"


def test_recusa_nota_acima_de_5():
    with pytest.raises(DomainError):
        Review.create("game-1", "Marina", 6)


def test_recusa_nota_abaixo_de_1():
    with pytest.raises(DomainError):
        Review.create("game-1", "Marina", 0)


def test_recusa_autor_curto():
    with pytest.raises(DomainError):
        Review.create("game-1", "M", 4)


def test_recusa_sem_jogo():
    with pytest.raises(DomainError):
        Review.create("", "Marina", 4)
