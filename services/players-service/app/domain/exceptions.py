"""Exceções do domínio dos jogadores."""


class DomainError(Exception):
    """Violação de uma regra de negócio. Vira HTTP 422 com mensagem amigável."""


class NotFoundError(Exception):
    """Recurso inexistente. Vira HTTP 404 com mensagem amigável."""


class ConflictError(Exception):
    """Operação conflita com o estado atual (ex.: já é dono do jogo). Vira HTTP 409."""


class DatabaseUnavailable(Exception):
    """Banco de dados indisponível. Vira HTTP 503 amigável, sem detalhe técnico."""
