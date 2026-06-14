"""Exceções do domínio do catálogo."""


class DomainError(Exception):
    """Violação de uma regra de negócio. Vira HTTP 422 com mensagem amigável."""


class DatabaseUnavailable(Exception):
    """Banco de dados indisponível. Vira HTTP 503 amigável, sem detalhe técnico."""
