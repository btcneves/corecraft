import anyio
import pytest
from fastapi import Request, Response

from tests.conftest import import_activity_module


def test_correlation_middleware_adds_header(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observability = import_activity_module("atividade-1", "app.observability", monkeypatch)
    request = Request({"type": "http", "headers": [(b"x-correlation-id", b"corr-1")]})

    async def call_next(request: Request) -> Response:
        assert observability.get_correlation_id() == "corr-1"
        return Response(status_code=204)

    response = anyio.run(observability.correlation_middleware, request, call_next)

    assert response.headers["X-Correlation-ID"] == "corr-1"
    assert observability.get_correlation_id() is None


def test_correlation_middleware_counts_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observability = import_activity_module("atividade-2", "app.observability", monkeypatch)
    request = Request({"type": "http", "headers": []})

    async def call_next(request: Request) -> Response:
        return Response(status_code=503)

    response = anyio.run(observability.correlation_middleware, request, call_next)

    assert response.status_code == 503
    assert "X-Correlation-ID" in response.headers
    assert 'corecraft_errors_total{service="atividade-2"} 1' in observability.metrics_text()


def test_health_and_metrics_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    observability = import_activity_module("atividade-3", "app.observability", monkeypatch)

    assert observability.health_payload() == {"status": "ok", "service": "atividade-3"}
    metrics = observability.metrics_text()
    assert 'corecraft_service_up{service="atividade-3"} 1' in metrics
    assert "corecraft_service_uptime_seconds" in metrics
