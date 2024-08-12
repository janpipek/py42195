import math

import pytest

from py42195.config import set_unit_system
from py42195.types import Distance, Pace, Speed, distance, duration, pace, speed


class TestDistance:
    def test_marathon_distances(self):
        assert pytest.approx(Distance.MARATHON.km, abs=0.01) == 42.195
        assert pytest.approx(Distance.HALF_MARATHON.mi, abs=0.01) == 13.11

    @pytest.mark.parametrize(
        ("source", "expected"),
        [
            ("1.4", 1.4),
            ("1 km", 1),
            ("2mi", 3.218),
            ("750 m", 0.75),
            ("-4km", ValueError),
            ("1760yd", 1.609),
            ("10ft", 0.003048),
            ("m48", ValueError),
            ("a lot", ValueError),
        ],
    )
    def test_parse(self, source, expected):
        if isinstance(expected, type) and issubclass(expected, Exception):
            with pytest.raises(expected):
                Distance.parse(source)
        else:
            assert Distance.parse(source).km == pytest.approx(expected, abs=0.001)

    @pytest.mark.parametrize(
        ("kwargs", "error"),
        [
            ({"m": 1, "km": 2}, ValueError),
            ({"aa": 1}, TypeError),
            ({}, ValueError),
            ({"km": "many"}, TypeError),
        ],
    )
    def test_invalid_args(self, kwargs, error):
        with pytest.raises(error):
            Distance(**kwargs)

    @pytest.mark.parametrize(
        ("unit_system", "value", "expected"),
        [
            ("si", "1 km", "1.00 km"),
            ("imperial", "1 km", "0.62 mi"),
            (None, "1 mi", "1.61 km"),
        ],
    )
    def test_str(self, unit_system, value, expected):
        a_distance = distance(value)
        with set_unit_system(unit_system or "si"):
            assert str(a_distance) == expected


class TestPace:
    class TestParse:
        @pytest.mark.parametrize(
            ("source", "expected"),
            [
                ("4:00", 240),
                ("4:00.0", 240),
                ("3:14.5", 194.5),
                ("1:00:01", 3601),
            ],
        )
        def test_valid(self, source, expected):
            pace = Pace.parse(source)
            assert pace.seconds_per_km == expected

    @pytest.mark.parametrize(
        ("seconds_per_km", "seconds_per_mile"), [(240, 386.24), (math.inf, math.inf)]
    )
    def test_units_equivalence(self, seconds_per_km, seconds_per_mile):
        pace_km = Pace(seconds_per_km)
        pace_mi = Pace(seconds_per_mile=seconds_per_mile)
        assert pace_km.seconds_per_km == pytest.approx(pace_mi.seconds_per_km, abs=0.01)

    class TestToSpeed:
        @pytest.mark.parametrize(
            ("a_speed", "a_pace"),
            [
                (10, "6:00"),
                ("10 mph", "3:43.7"),
                ("5 m/s", "3:20"),
            ],
        )
        def test_equivalence(self, a_speed, a_pace):
            assert speed(a_speed).km_h == pytest.approx(
                Pace.parse(a_pace).to_speed().km_h, abs=0.001
            )


class TestSpeed:
    class TestParse:
        @pytest.mark.parametrize(
            ("source", "expected"),
            [("10", 10), ("8 km/h", 8), ("1 mi/h", 1.609), ("2 m/s", 7.2)],
        )
        def test_valid(self, source, expected):
            speed = Speed.parse(source)
            assert speed.km_h == pytest.approx(expected, abs=0.01)

    class TestToPace:
        @pytest.mark.parametrize(
            ("a_speed", "a_pace"),
            [
                (10, "6:00"),
                ("10 mph", "3:43.7"),
                ("5 m/s", "3:20"),
            ],
        )
        def test_equivalence(self, a_speed, a_pace):
            assert speed(a_speed).to_pace().seconds_per_km == pytest.approx(
                Pace.parse(a_pace).seconds_per_km, abs=0.1
            )


class TestArithmetics:
    def test_marathon_record_pace(self):
        pace = duration("2:00:35") / Distance.MARATHON
        assert str(pace) == "2:51.5"

    def test_marathon_at_4_min_pace(self):
        duration = Distance.MARATHON * pace("4:00")
        assert str(duration) == "2:48:46.8"
