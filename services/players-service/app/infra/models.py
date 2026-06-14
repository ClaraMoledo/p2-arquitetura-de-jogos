"""Mapeamento ORM (SQLAlchemy) — detalhe de infraestrutura."""
from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class PlayerModel(Base):
    __tablename__ = "players"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    wallet_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[str] = mapped_column(String, nullable=False)


class LibraryEntryModel(Base):
    __tablename__ = "library_entries"
    __table_args__ = (UniqueConstraint("player_id", "game_id", name="uq_library_player_game"),)

    id: Mapped[str] = mapped_column(String, primary_key=True)
    player_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    game_id: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    price_paid_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    purchased_at: Mapped[str] = mapped_column(String, nullable=False)


class WishlistItemModel(Base):
    __tablename__ = "wishlist_items"
    __table_args__ = (UniqueConstraint("player_id", "game_id", name="uq_wishlist_player_game"),)

    id: Mapped[str] = mapped_column(String, primary_key=True)
    player_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    game_id: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    added_at: Mapped[str] = mapped_column(String, nullable=False)


class FriendshipModel(Base):
    __tablename__ = "friendships"
    __table_args__ = (UniqueConstraint("player_id", "friend_id", name="uq_friendship_pair"),)

    id: Mapped[str] = mapped_column(String, primary_key=True)
    player_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    friend_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    created_at: Mapped[str] = mapped_column(String, nullable=False)
