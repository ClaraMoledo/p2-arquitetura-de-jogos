"""Testes do caso de uso de compra e das amizades (com repositórios em memória)."""
import pytest

from app.domain.entities import Player
from app.domain.exceptions import ConflictError, DomainError, NotFoundError
from app.infra.memory import (
    InMemoryFriendshipRepository,
    InMemoryLibraryRepository,
    InMemoryPlayerRepository,
    InMemoryWishlistRepository,
)
from app.use_cases.manage_friends import AddFriend, ListFriends, RemoveFriend
from app.use_cases.manage_wishlist import AddToWishlist
from app.use_cases.purchase_game import PurchaseGame


def _setup():
    players = InMemoryPlayerRepository()
    library = InMemoryLibraryRepository()
    wishlist = InMemoryWishlistRepository()
    player = Player.create("Nova").deposit(20000)  # 25000
    players.save(player)
    return players, library, wishlist, player


def test_compra_desconta_da_carteira_e_entra_na_biblioteca():
    players, library, wishlist, player = _setup()
    use_case = PurchaseGame(players, library, wishlist)

    result = use_case.execute(
        player_id=player.id, game_id="g1", title="Aurora Frontier", base_price_cents=10000
    )

    # Primeira compra: 15% de boas-vindas -> paga 8500.
    assert result.pricing.final_cents == 8500
    assert result.player.wallet_cents == 25000 - 8500
    assert library.owns(player.id, "g1") is True


def test_compra_duplicada_e_bloqueada():
    players, library, wishlist, player = _setup()
    use_case = PurchaseGame(players, library, wishlist)
    use_case.execute(player_id=player.id, game_id="g1", title="Aurora", base_price_cents=5000)

    with pytest.raises(ConflictError):
        use_case.execute(player_id=player.id, game_id="g1", title="Aurora", base_price_cents=5000)


def test_compra_sem_saldo_e_recusada():
    players = InMemoryPlayerRepository()
    library = InMemoryLibraryRepository()
    wishlist = InMemoryWishlistRepository()
    player = Player.create("Pobre")  # 5000 de bônus
    players.save(player)
    use_case = PurchaseGame(players, library, wishlist)

    with pytest.raises(DomainError):
        use_case.execute(player_id=player.id, game_id="g1", title="Caro", base_price_cents=100000)


def test_compra_remove_o_jogo_da_lista_de_desejos():
    players, library, wishlist, player = _setup()
    AddToWishlist(players, wishlist, library).execute(
        player_id=player.id, game_id="g1", title="Aurora"
    )
    assert wishlist.exists(player.id, "g1") is True

    PurchaseGame(players, library, wishlist).execute(
        player_id=player.id, game_id="g1", title="Aurora", base_price_cents=5000
    )
    assert wishlist.exists(player.id, "g1") is False


def test_compra_para_jogador_inexistente():
    players, library, wishlist, _ = _setup()
    with pytest.raises(NotFoundError):
        PurchaseGame(players, library, wishlist).execute(
            player_id="nao-existe", game_id="g1", title="X", base_price_cents=1000
        )


def test_amizade_simetrica_adiciona_remove_e_lista():
    players = InMemoryPlayerRepository()
    friendships = InMemoryFriendshipRepository()
    a = Player.create("Nova")
    b = Player.create("Lumen")
    players.save(a)
    players.save(b)

    AddFriend(players, friendships).execute(player_id=a.id, friend_id=b.id)

    # A vê B e B vê A (simetria).
    assert [p.id for p in ListFriends(players, friendships).execute(a.id)] == [b.id]
    assert [p.id for p in ListFriends(players, friendships).execute(b.id)] == [a.id]

    RemoveFriend(friendships).execute(player_id=b.id, friend_id=a.id)
    assert ListFriends(players, friendships).execute(a.id) == []


def test_nao_pode_adicionar_a_si_mesmo():
    players = InMemoryPlayerRepository()
    friendships = InMemoryFriendshipRepository()
    a = Player.create("Nova")
    players.save(a)
    with pytest.raises(DomainError):
        AddFriend(players, friendships).execute(player_id=a.id, friend_id=a.id)
