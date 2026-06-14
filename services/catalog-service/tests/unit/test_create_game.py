"""Teste do caso de uso CreateGame com repositório em memória (TDD)."""
from app.infra.memory import InMemoryGameRepository
from app.use_cases.create_game import CreateGame
from app.use_cases.list_games import ListGames


def test_cria_e_lista_jogo():
    repository = InMemoryGameRepository()

    CreateGame(repository).execute(
        title="Neon Circuit",
        genre="Corrida",
        platform="PC",
        price_cents=12900,
        release_year=2022,
    )

    games = ListGames(repository).execute()
    assert len(games) == 1
    assert games[0].title == "Neon Circuit"
    assert games[0].price_cents == 12900
