"""Testes unitários da entidade Game (TDD)."""
import pytest

from app.domain.entities import Game
from app.domain.exceptions import DomainError


def test_cria_jogo_valido_com_id():
    game = Game.create("Aurora Frontier", "RPG", "PC", 19900, 2023)
    assert game.id
    assert game.title == "Aurora Frontier"
    assert game.price_cents == 19900
    assert game.available is True


def test_genero_e_plataforma_padrao_quando_vazios():
    game = Game.create("Jogo Sem Genero", "", "", 1000, 2020)
    assert game.genre == "Indefinido"
    assert game.platform == "Multiplataforma"


def test_recusa_titulo_curto():
    with pytest.raises(DomainError):
        Game.create("A", "RPG", "PC", 1000, 2023)


def test_recusa_preco_negativo():
    with pytest.raises(DomainError):
        Game.create("Jogo X", "RPG", "PC", -1, 2023)


def test_recusa_ano_invalido():
    with pytest.raises(DomainError):
        Game.create("Jogo X", "RPG", "PC", 1000, 1900)
