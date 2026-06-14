"""Testes do Circuit Breaker (resiliência)."""
import pytest

from app.infra.circuit_breaker import CircuitBreaker, CircuitOpenError


def _boom():
    raise RuntimeError("falha simulada")


def test_abre_apos_falhas_e_falha_rapido():
    clock = {"t": 0.0}
    breaker = CircuitBreaker("teste", failure_threshold=2, open_timeout=1.0, now=lambda: clock["t"])

    with pytest.raises(RuntimeError):
        breaker.call(_boom)
    with pytest.raises(RuntimeError):
        breaker.call(_boom)

    assert breaker.state == "OPEN"

    # Circuito aberto: falha imediatamente, sem executar a ação.
    with pytest.raises(CircuitOpenError):
        breaker.call(_boom)


def test_recupera_em_half_open_e_fecha():
    clock = {"t": 0.0}
    breaker = CircuitBreaker("teste", failure_threshold=1, open_timeout=1.0, now=lambda: clock["t"])

    with pytest.raises(RuntimeError):
        breaker.call(_boom)
    assert breaker.state == "OPEN"

    clock["t"] = 1.5  # tempo de espera passou
    assert breaker.call(lambda: "ok") == "ok"
    assert breaker.state == "CLOSED"
