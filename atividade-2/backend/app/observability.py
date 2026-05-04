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
_path_counters: dict[str, int] = {}
_last_latency_ms: float = 0.0


def get_correlation_id() -> str | None:
    return _correlation_id.get()


async def correlation_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    global _last_latency_ms
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    token = _correlation_id.set(correlation_id)
    _metrics["requests_total"] += 1
    path = request.scope.get("path", "")
    _path_counters[path] = _path_counters.get(path, 0) + 1
    t0 = time.perf_counter()
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
        _last_latency_ms = (time.perf_counter() - t0) * 1000
        _correlation_id.reset(token)


def health_payload() -> JsonDict:
    return {"status": "ok", "service": SERVICE_NAME}


def metrics_text(zmq_blocks: int = 0, zmq_txs: int = 0) -> str:
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
        "# HELP corecraft_last_request_latency_ms Last HTTP request duration in milliseconds.",
        "# TYPE corecraft_last_request_latency_ms gauge",
        f'corecraft_last_request_latency_ms{{service="{SERVICE_NAME}"}} {_last_latency_ms:.3f}',
        "# HELP corecraft_zmq_blocks_total Total ZMQ rawblock events received.",
        "# TYPE corecraft_zmq_blocks_total counter",
        f'corecraft_zmq_blocks_total{{service="{SERVICE_NAME}"}} {zmq_blocks}',
        "# HELP corecraft_zmq_tx_total Total ZMQ rawtx events received.",
        "# TYPE corecraft_zmq_tx_total counter",
        f'corecraft_zmq_tx_total{{service="{SERVICE_NAME}"}} {zmq_txs}',
        "# HELP corecraft_requests_by_path_total HTTP requests broken down by path.",
        "# TYPE corecraft_requests_by_path_total counter",
    ]
    for path, count in sorted(_path_counters.items()):
        lines.append(
            f'corecraft_requests_by_path_total{{service="{SERVICE_NAME}",path="{path}"}} {count}'
        )
    return "\n".join(lines) + "\n"
