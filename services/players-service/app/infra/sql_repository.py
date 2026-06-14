"""Implementações dos repositórios com SQLAlchemy (adaptadores de saída).

Cada método traduz erros de conexão em DatabaseUnavailable, isolando o
restante da aplicação dos detalhes do driver.
"""
from __future__ import annotations

from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from app.domain.entities import Friendship, LibraryEntry, Player, WishlistItem
from app.domain.exceptions import DatabaseUnavailable

from .database import get_session_factory
from .errors import is_connection_error
from .models import FriendshipModel, LibraryEntryModel, PlayerModel, WishlistItemModel


def _translate(exc: SQLAlchemyError) -> Exception:
    if is_connection_error(exc):
        return DatabaseUnavailable()
    return exc


class SqlPlayerRepository:
    def save(self, player: Player) -> None:
        try:
            with get_session_factory()() as session:
                session.merge(
                    PlayerModel(
                        id=player.id,
                        name=player.name,
                        wallet_cents=player.wallet_cents,
                        created_at=player.created_at,
                    )
                )
                session.commit()
        except SQLAlchemyError as exc:
            raise _translate(exc) from exc

    def list_all(self) -> list[Player]:
        try:
            with get_session_factory()() as session:
                rows = session.query(PlayerModel).order_by(PlayerModel.name).all()
                return [self._to_entity(row) for row in rows]
        except SQLAlchemyError as exc:
            raise _translate(exc) from exc

    def find_by_id(self, player_id: str) -> Player | None:
        try:
            with get_session_factory()() as session:
                row = session.get(PlayerModel, player_id)
                return self._to_entity(row) if row else None
        except SQLAlchemyError as exc:
            raise _translate(exc) from exc

    @staticmethod
    def _to_entity(row: PlayerModel) -> Player:
        return Player.restore(
            id=row.id, name=row.name, wallet_cents=row.wallet_cents, created_at=row.created_at
        )


class SqlLibraryRepository:
    def save(self, entry: LibraryEntry) -> None:
        try:
            with get_session_factory()() as session:
                session.merge(
                    LibraryEntryModel(
                        id=entry.id,
                        player_id=entry.player_id,
                        game_id=entry.game_id,
                        title=entry.title,
                        price_paid_cents=entry.price_paid_cents,
                        purchased_at=entry.purchased_at,
                    )
                )
                session.commit()
        except SQLAlchemyError as exc:
            raise _translate(exc) from exc

    def list_by_player(self, player_id: str) -> list[LibraryEntry]:
        try:
            with get_session_factory()() as session:
                rows = (
                    session.query(LibraryEntryModel)
                    .filter(LibraryEntryModel.player_id == player_id)
                    .order_by(LibraryEntryModel.purchased_at.desc())
                    .all()
                )
                return [self._to_entity(row) for row in rows]
        except SQLAlchemyError as exc:
            raise _translate(exc) from exc

    def owns(self, player_id: str, game_id: str) -> bool:
        try:
            with get_session_factory()() as session:
                return (
                    session.query(LibraryEntryModel)
                    .filter(
                        LibraryEntryModel.player_id == player_id,
                        LibraryEntryModel.game_id == game_id,
                    )
                    .first()
                    is not None
                )
        except SQLAlchemyError as exc:
            raise _translate(exc) from exc

    @staticmethod
    def _to_entity(row: LibraryEntryModel) -> LibraryEntry:
        return LibraryEntry.restore(
            id=row.id,
            player_id=row.player_id,
            game_id=row.game_id,
            title=row.title,
            price_paid_cents=row.price_paid_cents,
            purchased_at=row.purchased_at,
        )


class SqlWishlistRepository:
    def save(self, item: WishlistItem) -> None:
        try:
            with get_session_factory()() as session:
                session.merge(
                    WishlistItemModel(
                        id=item.id,
                        player_id=item.player_id,
                        game_id=item.game_id,
                        title=item.title,
                        added_at=item.added_at,
                    )
                )
                session.commit()
        except SQLAlchemyError as exc:
            raise _translate(exc) from exc

    def list_by_player(self, player_id: str) -> list[WishlistItem]:
        try:
            with get_session_factory()() as session:
                rows = (
                    session.query(WishlistItemModel)
                    .filter(WishlistItemModel.player_id == player_id)
                    .order_by(WishlistItemModel.added_at.desc())
                    .all()
                )
                return [self._to_entity(row) for row in rows]
        except SQLAlchemyError as exc:
            raise _translate(exc) from exc

    def exists(self, player_id: str, game_id: str) -> bool:
        try:
            with get_session_factory()() as session:
                return (
                    session.query(WishlistItemModel)
                    .filter(
                        WishlistItemModel.player_id == player_id,
                        WishlistItemModel.game_id == game_id,
                    )
                    .first()
                    is not None
                )
        except SQLAlchemyError as exc:
            raise _translate(exc) from exc

    def remove(self, player_id: str, game_id: str) -> bool:
        try:
            with get_session_factory()() as session:
                deleted = (
                    session.query(WishlistItemModel)
                    .filter(
                        WishlistItemModel.player_id == player_id,
                        WishlistItemModel.game_id == game_id,
                    )
                    .delete()
                )
                session.commit()
                return deleted > 0
        except SQLAlchemyError as exc:
            raise _translate(exc) from exc

    @staticmethod
    def _to_entity(row: WishlistItemModel) -> WishlistItem:
        return WishlistItem.restore(
            id=row.id,
            player_id=row.player_id,
            game_id=row.game_id,
            title=row.title,
            added_at=row.added_at,
        )


class SqlFriendshipRepository:
    def save(self, friendship: Friendship) -> None:
        try:
            with get_session_factory()() as session:
                session.merge(
                    FriendshipModel(
                        id=friendship.id,
                        player_id=friendship.player_id,
                        friend_id=friendship.friend_id,
                        created_at=friendship.created_at,
                    )
                )
                session.commit()
        except SQLAlchemyError as exc:
            raise _translate(exc) from exc

    def list_by_player(self, player_id: str) -> list[Friendship]:
        try:
            with get_session_factory()() as session:
                rows = (
                    session.query(FriendshipModel)
                    .filter(
                        or_(
                            FriendshipModel.player_id == player_id,
                            FriendshipModel.friend_id == player_id,
                        )
                    )
                    .order_by(FriendshipModel.created_at.desc())
                    .all()
                )
                return [self._to_entity(row) for row in rows]
        except SQLAlchemyError as exc:
            raise _translate(exc) from exc

    def exists(self, player_id: str, friend_id: str) -> bool:
        try:
            with get_session_factory()() as session:
                return self._pair_query(session, player_id, friend_id).first() is not None
        except SQLAlchemyError as exc:
            raise _translate(exc) from exc

    def remove(self, player_id: str, friend_id: str) -> bool:
        try:
            with get_session_factory()() as session:
                deleted = self._pair_query(session, player_id, friend_id).delete(
                    synchronize_session=False
                )
                session.commit()
                return deleted > 0
        except SQLAlchemyError as exc:
            raise _translate(exc) from exc

    @staticmethod
    def _pair_query(session, a: str, b: str):
        return session.query(FriendshipModel).filter(
            or_(
                (FriendshipModel.player_id == a) & (FriendshipModel.friend_id == b),
                (FriendshipModel.player_id == b) & (FriendshipModel.friend_id == a),
            )
        )

    @staticmethod
    def _to_entity(row: FriendshipModel) -> Friendship:
        return Friendship.restore(
            id=row.id,
            player_id=row.player_id,
            friend_id=row.friend_id,
            created_at=row.created_at,
        )
