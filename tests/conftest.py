import importlib
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _purge_app_modules() -> None:
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]


def prepare_activity_import(activity: str, monkeypatch: pytest.MonkeyPatch) -> Path:
    _purge_app_modules()
    backend = ROOT / activity / "backend"
    frontend = ROOT / activity / "frontend"
    monkeypatch.setenv("FRONTEND_DIR", str(frontend))
    monkeypatch.syspath_prepend(str(backend))
    return backend


def import_activity_module(
    activity: str, module: str, monkeypatch: pytest.MonkeyPatch
) -> ModuleType:
    prepare_activity_import(activity, monkeypatch)
    return importlib.import_module(module)


class FakeRPC:
    def __init__(self, responses: dict[str, Any] | None = None) -> None:
        self.responses = responses or {}
        self.calls: list[tuple[str, tuple[Any, ...]]] = []

    def call(self, method: str, *params: Any) -> Any:
        self.calls.append((method, params))
        result = self.responses[method]
        if isinstance(result, Exception):
            raise result
        return result
