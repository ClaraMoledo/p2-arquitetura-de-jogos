"""Factory que escolhe a política de preço conforme o histórico do jogador.

Mantém a regra de seleção num só lugar: o caso de uso de compra só conhece a
abstração `PricingPolicy`, nunca os `if`s de qual desconto aplicar.
"""
from __future__ import annotations

from .strategies import PricingPolicy, StandardPricing, VeteranPricing, WelcomePricing

_VETERAN_THRESHOLD = 5  # a partir de 5 jogos na biblioteca, vira veterano


def create_pricing_policy(owned_count: int) -> PricingPolicy:
    if owned_count <= 0:
        return WelcomePricing()
    if owned_count >= _VETERAN_THRESHOLD:
        return VeteranPricing()
    return StandardPricing()
