import os
from contextvars import ContextVar

from typing_extensions import ContextManager

METRIC = "metric"
IMPERIAL = "imperial"


_unit_system: ContextVar[str] = ContextVar("unit_system", default=METRIC)

_default_units = {
    METRIC: {
        "Distance": "km",
        "Duration": "s",
        "Pace": "seconds_per_km",
        "Speed": "km_h",
    },
    IMPERIAL: {
        "Distance": "mi",
        "Duration": "s",
        "Pace": "seconds_per_mile",
        "Speed": "mph",
    },
}


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


def get_default_unit(quantity: type) -> str:
    """Name of the argument that will be used as default unit for the given quantity."""
    return _default_units[get_unit_system()][quantity.__name__]
