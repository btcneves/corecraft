import time
import uuid
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from typing import Any

from fastapi import Request, Response

JsonDict = dict[str, Any]

SERVICE_NAME = "atividade-2"
_started_at = time.time()
_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)
_metrics: dict[str, int] = {"requests_total": 0, "errors_total": 0}


def get_correlation_id() -> str | None:
    return _correlation_id.get()


async def correlation_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    token = _correlation_id.set(correlation_id)
    _metrics["requests_total"] += 1
    try:
        response = await call_next(request)
        if response.status_code >= 500:
            _metrics["errors_total"] += 1
        response.headers["X-Correlation-ID"] = correlation_id
        return response
    except Exception:
        _metrics["errors_total"] += 1
        raise
    finally:
        _correlation_id.reset(token)


def health_payload() -> JsonDict:
    return {"status": "ok", "service": SERVICE_NAME}


def metrics_text() -> str:
    uptime = time.time() - _started_at
    lines = [
        "# HELP corecraft_service_up Service health status.",
        "# TYPE corecraft_service_up gauge",
        f'corecraft_service_up{{service="{SERVICE_NAME}"}} 1',
        "# HELP corecraft_service_uptime_seconds Service uptime in seconds.",
        "# TYPE corecraft_service_uptime_seconds gauge",
        f'corecraft_service_uptime_seconds{{service="{SERVICE_NAME}"}} {uptime:.3f}',
        "# HELP corecraft_requests_total Total HTTP requests.",
        "# TYPE corecraft_requests_total counter",
        f'corecraft_requests_total{{service="{SERVICE_NAME}"}} {_metrics["requests_total"]}',
        "# HELP corecraft_errors_total Total HTTP 5xx responses or unhandled errors.",
        "# TYPE corecraft_errors_total counter",
        f'corecraft_errors_total{{service="{SERVICE_NAME}"}} {_metrics["errors_total"]}',
    ]
    return "\n".join(lines) + "\n"
