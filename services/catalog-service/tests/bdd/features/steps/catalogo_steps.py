"""Passos BDD do catálogo (behave)."""
from behave import given, then, when

from app.domain.exceptions import DomainError
from app.infra.memory import InMemoryGameRepository
from app.use_cases.create_game import CreateGame
from app.use_cases.list_games import ListGames


@given("que o catálogo está vazio")
def step_catalogo_vazio(context):
    context.repository = InMemoryGameRepository()
    context.error = None


@when('eu cadastro o jogo "{title}" do gênero "{genre}" por {reais:d} reais lançado em {year:d}')
def step_cadastra_jogo(context, title, genre, reais, year):
    CreateGame(context.repository).execute(
        title=title,
        genre=genre,
        platform="PC",
        price_cents=reais * 100,
        release_year=year,
    )


@when('eu tento cadastrar o jogo "{title}" lançado em {year:d}')
def step_tenta_cadastrar(context, title, year):
    try:
        CreateGame(context.repository).execute(
            title=title,
            genre="RPG",
            platform="PC",
            price_cents=1000,
            release_year=year,
        )
    except DomainError as exc:
        context.error = exc


@then("o catálogo deve conter {count:d} jogo")
def step_conta_jogo_singular(context, count):
    _assert_count(context, count)


@then("o catálogo deve conter {count:d} jogos")
def step_conta_jogo_plural(context, count):
    _assert_count(context, count)


def _assert_count(context, count):
    games = ListGames(context.repository).execute()
    assert len(games) == count, f"esperava {count}, obteve {len(games)}"


@then('o jogo "{title}" deve estar disponível')
def step_jogo_disponivel(context, title):
    games = ListGames(context.repository).execute()
    match = next((game for game in games if game.title == title), None)
    assert match is not None, "jogo não encontrado"
    assert match.available is True


@then("o cadastro deve ser recusado")
def step_cadastro_recusado(context):
    assert isinstance(context.error, DomainError), "esperava uma violação de regra de negócio"
