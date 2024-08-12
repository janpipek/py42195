import os
from contextvars import ContextVar

from typing_extensions import ContextManager

METRIC = "metric"
IMPERIAL = "imperial"


_unit_system: ContextVar[str] = ContextVar("unit_system", default=METRIC)


def get_unit_system() -> str:
    return _unit_system.get()


def set_unit_system(system: str) -> ContextManager:
    if system not in [METRIC, IMPERIAL]:
        raise ValueError(f"Invalid unit system: {system}")

    class _UnitSystem:
        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_val, exc_tb):
            _unit_system.reset(_reset_token)

    _reset_token = _unit_system.set(system)
    return _UnitSystem()


set_unit_system(os.environ.get("PY42195_UNIT_SYSTEM", METRIC))
