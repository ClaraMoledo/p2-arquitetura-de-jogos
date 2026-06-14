"""Passos BDD da loja (behave)."""
from behave import given, then, when

from app.domain.entities import Player
from app.domain.exceptions import ConflictError, DomainError
from app.infra.memory import (
    InMemoryLibraryRepository,
    InMemoryPlayerRepository,
    InMemoryWishlistRepository,
)
from app.use_cases.list_library import ListLibrary
from app.use_cases.purchase_game import PurchaseGame


def _game_id(title: str) -> str:
    # No teste, o título identifica o jogo (mesmo título = mesmo jogo).
    return title.strip().lower()


@given('um jogador chamado "{name}" com {wallet:d} centavos na carteira')
def step_jogador(context, name, wallet):
    context.players = InMemoryPlayerRepository()
    context.library = InMemoryLibraryRepository()
    context.wishlist = InMemoryWishlistRepository()
    # Cria o jogador com o saldo desejado (bônus inicial + ajuste por depósito).
    player = Player.create(name)
    diff = wallet - player.wallet_cents
    if diff > 0:
        player = player.deposit(diff)
    elif diff < 0:
        player = player.charge(-diff)
    context.players.save(player)
    context.player = player
    context.error = None


def _purchase(context, title, price):
    PurchaseGame(context.players, context.library, context.wishlist).execute(
        player_id=context.player.id,
        game_id=_game_id(title),
        title=title,
        base_price_cents=price,
    )


@when('ele compra o jogo "{title}" por {price:d} centavos')
def step_compra(context, title, price):
    _purchase(context, title, price)


@when('ele tenta comprar o jogo "{title}" por {price:d} centavos')
def step_tenta_comprar(context, title, price):
    try:
        _purchase(context, title, price)
    except (DomainError, ConflictError) as exc:
        context.error = exc


@then("a compra deve ser concluída")
def step_compra_ok(context):
    assert context.error is None, f"esperava sucesso, veio: {context.error}"


@then("a compra deve ser recusada")
def step_compra_recusada(context):
    assert context.error is not None, "esperava que a compra fosse recusada"


@then("a biblioteca dele deve conter {count:d} jogo")
def step_lib_singular(context, count):
    _assert_lib(context, count)


@then("a biblioteca dele deve conter {count:d} jogos")
def step_lib_plural(context, count):
    _assert_lib(context, count)


def _assert_lib(context, count):
    entries = ListLibrary(context.library).execute(context.player.id)
    assert len(entries) == count, f"esperava {count}, obteve {len(entries)}"
