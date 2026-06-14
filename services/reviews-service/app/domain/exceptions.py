"""Exceções do domínio de avaliações."""


class DomainError(Exception):
    """Violação de regra de negócio. Vira HTTP 422 com mensagem amigável."""


class DatabaseUnavailable(Exception):
    """Banco indisponível. Vira HTTP 503 amigável, sem detalhe técnico."""
