"""Testes das políticas de preço (Strategy + Factory)."""
from app.pricing.factory import create_pricing_policy
from app.pricing.strategies import StandardPricing, VeteranPricing, WelcomePricing


def test_primeira_compra_usa_boas_vindas():
    policy = create_pricing_policy(owned_count=0)
    assert isinstance(policy, WelcomePricing)
    priced = policy.price(10000)
    assert priced.final_cents == 8500  # -15%
    assert priced.discount_cents == 1500


def test_jogador_intermediario_paga_preco_cheio():
    policy = create_pricing_policy(owned_count=2)
    assert isinstance(policy, StandardPricing)
    priced = policy.price(10000)
    assert priced.final_cents == 10000
    assert priced.discount_cents == 0


def test_veterano_ganha_desconto_de_fidelidade():
    policy = create_pricing_policy(owned_count=5)
    assert isinstance(policy, VeteranPricing)
    priced = policy.price(10000)
    assert priced.final_cents == 8000  # -20%


def test_preco_final_nunca_fica_negativo():
    priced = WelcomePricing().price(0)
    assert priced.final_cents == 0
