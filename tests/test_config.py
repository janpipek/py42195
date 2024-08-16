import pytest

from py42195.config import IMPERIAL, METRIC, get_unit_system, set_unit_system


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    monkeypatch.delenv("PY42195_UNIT_SYSTEM", raising=False)
    yield


def test_default_is_metric():
    assert get_unit_system() == METRIC


def test_os_env_overrides_default(monkeypatch):
    monkeypatch.setenv("PY42195_UNIT_SYSTEM", IMPERIAL)
    assert get_unit_system() == IMPERIAL


def test_context_manager():
    assert get_unit_system() == METRIC
    with set_unit_system(IMPERIAL):
        assert get_unit_system() == IMPERIAL
    assert get_unit_system() == METRIC
