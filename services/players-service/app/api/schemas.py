"""Schemas de entrada da API (Pydantic)."""
from __future__ import annotations

from pydantic import BaseModel, Field


class PlayerIn(BaseModel):
    name: str


class DepositIn(BaseModel):
    amountCents: int = Field(gt=0)


class PurchaseIn(BaseModel):
    gameId: str
    title: str | None = None
    basePriceCents: int = Field(ge=0)


class WishlistIn(BaseModel):
    gameId: str
    title: str | None = None


class FriendIn(BaseModel):
    friendId: str
