"""Schemas de entrada/saída da API (Pydantic)."""
from __future__ import annotations

from pydantic import BaseModel, Field


class GameIn(BaseModel):
    title: str
    genre: str | None = None
    platform: str | None = None
    priceCents: int = Field(ge=0)
    releaseYear: int
