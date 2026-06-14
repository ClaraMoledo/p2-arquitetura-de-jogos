"""Políticas de preço de compra (Strategy Pattern).

Cada política sabe transformar o preço de tabela no preço final e descrever
o porquê do desconto. Adicionar uma nova política não toca no caso de uso de
compra (Aberto/Fechado — o "O" de SOLID).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class PricedPurchase:
    base_cents: int
    final_cents: int
    discount_cents: int
    policy: str
    label: str


class PricingPolicy(Protocol):
    name: str

    def price(self, base_cents: int) -> PricedPurchase:
        ...


def _result(base_cents: int, final_cents: int, policy: str, label: str) -> PricedPurchase:
    final_cents = max(0, final_cents)
    return PricedPurchase(
        base_cents=base_cents,
        final_cents=final_cents,
        discount_cents=base_cents - final_cents,
        policy=policy,
        label=label,
    )


class StandardPricing:
    """Preço cheio, sem desconto."""

    name = "PADRAO"

    def price(self, base_cents: int) -> PricedPurchase:
        return _result(base_cents, base_cents, self.name, "Preço de tabela")


class WelcomePricing:
    """Primeira compra do jogador: 15% de boas-vindas."""

    name = "BOAS_VINDAS"
    _percent = 15

    def price(self, base_cents: int) -> PricedPurchase:
        final = round(base_cents * (100 - self._percent) / 100)
        return _result(base_cents, final, self.name, f"Primeira compra · -{self._percent}%")


class VeteranPricing:
    """Jogador veterano (biblioteca grande): 20% de fidelidade."""

    name = "VETERANO"
    _percent = 20

    def price(self, base_cents: int) -> PricedPurchase:
        final = round(base_cents * (100 - self._percent) / 100)
        return _result(base_cents, final, self.name, f"Fidelidade · -{self._percent}%")
