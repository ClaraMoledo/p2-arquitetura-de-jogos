"""Mapeamento ORM (SQLAlchemy) — detalhe de infraestrutura."""
from __future__ import annotations

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class GameModel(Base):
    __tablename__ = "games"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    genre: Mapped[str] = mapped_column(String, nullable=False, default="Indefinido")
    platform: Mapped[str] = mapped_column(String, nullable=False, default="Multiplataforma")
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    release_year: Mapped[int] = mapped_column(Integer, nullable=False)
    available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
