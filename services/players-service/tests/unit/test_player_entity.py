"""Testes da entidade Player (regras de carteira e criação)."""
import pytest

from app.domain.entities import Player
from app.domain.exceptions import DomainError


def test_novo_jogador_recebe_bonus_de_boas_vindas():
    player = Player.create("Nova")
    assert player.name == "Nova"
    assert player.wallet_cents == 5000
    assert player.id


def test_apelido_curto_e_recusado():
    with pytest.raises(DomainError):
        Player.create("N")


def test_deposito_soma_ao_saldo_e_mantem_imutabilidade():
    player = Player.create("Nova")
    atualizado = player.deposit(2000)
    assert atualizado.wallet_cents == 7000
    assert player.wallet_cents == 5000  # original não muda


def test_deposito_invalido_e_recusado():
    player = Player.create("Nova")
    with pytest.raises(DomainError):
        player.deposit(0)
    with pytest.raises(DomainError):
        player.deposit(-100)


def test_cobranca_dentro_do_saldo():
    player = Player.create("Nova").deposit(5000)  # 10000
    cobrado = player.charge(3000)
    assert cobrado.wallet_cents == 7000


def test_cobranca_acima_do_saldo_e_recusada():
    player = Player.create("Nova")  # 5000
    with pytest.raises(DomainError):
        player.charge(6000)
