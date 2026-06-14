"""Schemas de entrada da API de avaliações."""
from __future__ import annotations

from pydantic import BaseModel, Field


class ReviewIn(BaseModel):
    gameId: str
    author: str
    rating: int = Field(ge=1, le=5)
    comment: str | None = None
