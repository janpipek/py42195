import math

import pytest

from py42195.types import Distance, Pace, duration, pace


class TestDistance:
    def test_marathon_distances(self):
        assert pytest.approx(Distance.MARATHON.km, abs=0.01) == 42.195
        assert pytest.approx(Distance.HALF_MARATHON.mi, abs=0.01) == 13.11


class TestPace:
    class TestParse:
        @pytest.mark.parametrize(
            ("string", "seconds"),
            [
                ("4:00", 240),
                ("4:00.0", 240),
                ("3:14.5", 194.5),
                ("1:00:01", 3601),
            ],
        )
        def test_valid(self, string, seconds):
            pace = Pace.parse(string)
            assert pace.seconds_per_km == seconds

    @pytest.mark.parametrize(
        ("seconds_per_km", "seconds_per_mile"), [(240, 386.24), (math.inf, math.inf)]
    )
    def test_units_equivalence(self, seconds_per_km, seconds_per_mile):
        pace_km = Pace(seconds_per_km)
        pace_mi = Pace(seconds_per_mile=seconds_per_mile)
        assert pace_km.seconds_per_km == pytest.approx(pace_mi.seconds_per_km, abs=0.01)


class TestArithmetics:
    def test_marathon_record_pace(self):
        pace = duration("2:00:35") / Distance.MARATHON
        assert str(pace) == "2:51.5"

    def test_marathon_at_4_min_pace(self):
        duration = Distance.MARATHON * pace("4:00")
        assert str(duration) == "2:48:46.8"
