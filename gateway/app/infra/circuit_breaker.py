"""Circuit Breaker (padrão de resiliência) — versão Python."""
from __future__ import annotations

import time
from typing import Callable, TypeVar

T = TypeVar("T")


class CircuitOpenError(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"Circuito aberto para '{name}'")
        self.name = name


class CircuitBreaker:
    """
    Quando um serviço para de responder, o circuito abre e as próximas
    chamadas falham na hora (em vez de travar). Depois de um intervalo,
    testa de novo (HALF_OPEN) e fecha se o serviço voltou.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 3,
        open_timeout: float = 8.0,
        now: Callable[[], float] = time.monotonic,
    ) -> None:
        self.name = name
        self._failure_threshold = failure_threshold
        self._open_timeout = open_timeout
        self._now = now
        self._state = "CLOSED"
        self._failures = 0
        self._next_try = 0.0

    @property
    def state(self) -> str:
        return self._state

    def call(self, action: Callable[[], T]) -> T:
        if self._state == "OPEN":
            if self._now() < self._next_try:
                raise CircuitOpenError(self.name)
            self._state = "HALF_OPEN"

        try:
            result = action()
        except Exception:
            self._on_failure()
            raise
        self._on_success()
        return result

    def _on_success(self) -> None:
        self._failures = 0
        self._state = "CLOSED"

    def _on_failure(self) -> None:
        self._failures += 1
        if self._state == "HALF_OPEN" or self._failures >= self._failure_threshold:
            self._state = "OPEN"
            self._next_try = self._now() + self._open_timeout
