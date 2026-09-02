# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`py42195` is a tiny, dependency-free Python library for arithmetic over running-pace quantities: `Distance`, `Duration`, `Pace`, and `Speed`. It supports parsing from strings, metric/imperial unit systems, and cross-type arithmetic (e.g. `Distance * Pace -> Duration`, `Distance / Duration -> Speed`).

## Commands

Uses `just` as the task runner and `uv` for Python execution/dependency management.

```bash
just test        # uv run pytest
just mypy         # uv run mypy src/ tests/
just pyright      # optional, not yet a target of correctness (uv run --with pyright pyright)
just pre-commit   # uvx pre-commit run --all
just build        # uv build (cleans dist/ first)
just publish      # build + uv publish
```

Run a single test: `uv run pytest tests/test_types.py::TestDistance::test_parse -v`

Per user's global Python rules, always invoke Python via `uv run` in this project.

## Architecture

- `src/py42195/constants.py` — raw conversion factors (marathon distance in km, miles/yards/feet/meters per km). No logic.
- `src/py42195/config.py` — unit-system state. `_unit_system` is a `ContextVar`, defaulting to the `PY42195_UNIT_SYSTEM` env var, then `METRIC`. `set_unit_system()` returns a context manager for scoped overrides. `get_default_unit(quantity_type)` maps a class name to the kwarg name used when constructing that type without an explicit unit (used by the `pace()`, `distance()`, `speed()` factory functions in `types.py`).
- `src/py42195/utils.py` — the `[hh:]mm:ss[.sss]` interval mini-parser/formatter (`INTERVAL_PATTERN`, `parse_interval`, `format_interval`) shared by `Duration` and `Pace` string parsing.
- `src/py42195/types.py` — the four value types plus module-level factory functions (`distance()`, `duration()`, `pace()`, `speed()`) that accept either a string (parsed) or a numeric value in the current default unit.
- `src/py42195/__init__.py` — the public API surface; everything importable from `py42195` is re-exported here explicitly via `__all__`. When adding a new public name, export it here too.

### Cross-type arithmetic

Each type's `__mul__`/`__truediv__` (and `__rtruediv__` for `timedelta`) implements the physically meaningful conversions between the four types, e.g.:

- `Distance * Pace -> Duration`, `Distance / Duration -> Speed`, `Distance / Speed -> Duration`
- `Duration / Distance -> Pace`, `Duration / Pace -> Distance`, `Duration * Speed -> Distance`
- `Pace * Distance -> Duration`, `Pace.to_speed() -> Speed`
- `Speed * Duration -> Distance`, `Speed.to_pace() -> Pace`

When adding a new cross-type operation, implement it symmetrically (both operand orders via `__r*__` where applicable) and add it to this list.

### Unit system

`str()`/`repr()` output and the unit used by the `pace()`/`distance()`/`speed()` factories when given a bare number are both driven by `get_unit_system()` (metric or imperial), not by how the value was originally constructed — a `Distance` built with `km=` will still print in miles if `IMPERIAL` is active. Tests toggle this with the `use_imperial_units` fixture (see `tests/test_types.py`) wrapping `set_unit_system(IMPERIAL)`.

### Parsing

Each type has a `PARSE_PATTERN` regex and a `parse(cls, s)` classmethod. `Duration`/`Pace` reuse `INTERVAL_PATTERN` from `utils.py` for the `[hh:]mm:ss` portion; `Distance`/`Speed` use their own `ALLOWED_UNITS`-driven pattern. Unit suffixes are optional in all patterns, defaulting to the current unit system's default unit.
