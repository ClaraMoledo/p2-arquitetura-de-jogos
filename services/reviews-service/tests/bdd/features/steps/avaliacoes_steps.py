"""Passos BDD das avaliações (behave)."""
from behave import given, then, when

from app.domain.exceptions import DomainError
from app.infra.memory import InMemoryReviewRepository
from app.use_cases.add_review import AddReview
from app.use_cases.compute_averages import ComputeAverages
from app.use_cases.list_reviews import ListReviews


@given('que não há avaliações para o jogo "{game_id}"')
def step_sem_avaliacoes(context, game_id):
    context.repository = InMemoryReviewRepository()
    context.error = None


@when('eu avalio o jogo "{game_id}" com nota {rating:d} assinando como "{author}"')
def step_avalia(context, game_id, rating, author):
    AddReview(context.repository).execute(game_id=game_id, author=author, rating=rating)


@when('eu tento avaliar o jogo "{game_id}" com nota {rating:d} assinando como "{author}"')
def step_tenta_avaliar(context, game_id, rating, author):
    try:
        AddReview(context.repository).execute(game_id=game_id, author=author, rating=rating)
    except DomainError as exc:
        context.error = exc


@then('o jogo "{game_id}" deve ter {count:d} avaliação')
def step_conta_singular(context, game_id, count):
    reviews = ListReviews(context.repository).execute(game_id)
    assert len(reviews) == count, f"esperava {count}, obteve {len(reviews)}"


@then('o jogo "{game_id}" deve ter {count:d} avaliações')
def step_conta_plural(context, game_id, count):
    reviews = ListReviews(context.repository).execute(game_id)
    assert len(reviews) == count, f"esperava {count}, obteve {len(reviews)}"


@then('a média do jogo "{game_id}" deve ser {expected:f}')
def step_media(context, game_id, expected):
    averages = {item["gameId"]: item for item in ComputeAverages(context.repository).execute()}
    assert averages[game_id]["average"] == expected


@then("a avaliação deve ser recusada")
def step_recusada(context):
    assert isinstance(context.error, DomainError), "esperava uma violação de regra de negócio"
