from py42195.utils import parse_interval
from py42195.types import Duration

import pytest
from datetime import timedelta


class TestParseInterval:
    @pytest.mark.parametrize(
        ("source", "expected"),
        [
            ("1", 1),
            ("1:12", 72),
            ("1:12:12", 4332),
            ("0.1", 0.1),
            ("999:59:59", 3599999),
        ],
    )
    def test_valid_string(self, source, expected):
        assert parse_interval(source) == timedelta(seconds=expected)

    @pytest.mark.parametrize(
        "source",
        [
            "2:",
            "1:74",
            "1:1:74",
            "1.2.5",
            "12km",
            "abc 1:12:12",
            "1:20pm",
        ],
    )
    def test_invalid_string(self, source):
        with pytest.raises(ValueError):
            parse_interval(source)

    @pytest.mark.parametrize("source", [Duration(1), 12])
    def test_invalid_type(self, source):
        with pytest.raises(TypeError):
            parse_interval(source)
