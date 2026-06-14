"""Adaptador HTTP para um microsserviço (Adapter Pattern)."""
from __future__ import annotations

import httpx

from .circuit_breaker import CircuitBreaker


class DownstreamError(Exception):
    def __init__(self, status: int, data: object) -> None:
        super().__init__(f"Falha do serviço a jusante ({status})")
        self.status = status
        self.data = data


class ServiceClient:
    """
    Encapsula httpx + timeout + Circuit Breaker atrás de get/post.
    Respostas 2xx/4xx são repassadas; 5xx, rede e timeout contam como
    falha e podem abrir o circuito.
    """

    def __init__(self, base_url: str, name: str, timeout: float = 4.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._breaker = CircuitBreaker(name)

    @property
    def state(self) -> str:
        return self._breaker.state

    def get(self, path: str, params: dict | None = None) -> dict:
        return self._request("GET", path, params=params)

    def post(self, path: str, json: dict) -> dict:
        return self._request("POST", path, json=json)

    def delete(self, path: str) -> dict:
        return self._request("DELETE", path)

    def _request(
        self,
        method: str,
        path: str,
        params: dict | None = None,
        json: dict | None = None,
    ) -> dict:
        def action() -> dict:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.request(
                    method, f"{self._base_url}{path}", params=params, json=json
                )
            data = _safe_json(response)
            if response.status_code >= 500:
                raise DownstreamError(response.status_code, data)
            return {"status": response.status_code, "data": data}

        return self._breaker.call(action)


def _safe_json(response: httpx.Response) -> object:
    try:
        return response.json()
    except Exception:
        return None
