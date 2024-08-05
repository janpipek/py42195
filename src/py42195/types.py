from datetime import timedelta
from typing import Any, Self

from py42195.utils import format_interval, parse_interval


class Distance:
    km: float

    def __init__(self, km: float, /):
        # TODO: Allow other units
        self.km = km

    @classmethod
    def parse(cls, s: str) -> Self:
        value = float(s.split(" ")[0])
        return cls(value)

    def __str__(self) -> str:
        return f"{self.km} km"

    def __add__(self, other: "Distance") -> "Distance":
        if isinstance(other, Distance):
            return Distance(self.km + other.km)
        return NotImplemented

    def __sub__(self, other: "Distance") -> "Distance":
        if isinstance(other, Distance):
            return Distance(self.km - other.km)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Distance(self.km * other)
        if isinstance(other, Pace):
            return Duration(self.km * other.seconds_per_km)
        else:
            return NotImplemented


class Duration:
    seconds: float

    def __init__(self, seconds: float | timedelta, /):
        if isinstance(seconds, timedelta):
            self.seconds = seconds.total_seconds()
        else:
            self.seconds = seconds

    @classmethod
    def parse(cls, s: str, /) -> Self:
        if (delta := parse_interval(s)) is None:
            raise ValueError(f"Cannot parse as time: {s}")
        return cls(delta.total_seconds())

    def __str__(self) -> str:
        return format_interval(self.seconds)

    def __repr__(self) -> str:
        return f"duration('{self!s}')"

    def __add__(self, other: "Duration") -> "Duration":
        if isinstance(other, Duration):
            return Duration(self.seconds + other.seconds)
        return NotImplemented

    def __sub__(self, other: "Duration") -> "Duration":
        if isinstance(other, Duration):
            return Duration(self.seconds - other.seconds)
        return NotImplemented

    def __mul__(self, other: Any) -> Any:
        if isinstance(other, (int, float)):
            return Duration(self.seconds * other)
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Duration(self.seconds / other)
        if isinstance(other, Distance):
            return Pace(self.seconds / other.km)
        if isinstance(other, Duration):
            return self.seconds / other.seconds
        return NotImplemented


class Pace:
    seconds_per_km: float

    # TODO: Include imperial metrics
    def __init__(self, seconds_per_km: float, /):
        self.seconds_per_km = seconds_per_km

    def __str__(self):
        return format_interval(self.seconds_per_km)

    def __repr__(self) -> str:
        return f"pace('{self!s}')"

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Pace(self.seconds_per_km * other)
        if isinstance(other, Distance):
            return Duration(self.seconds_per_km * other.km)
        else:
            return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Pace(self.seconds_per_km / other)
        return NotImplemented

    @classmethod
    def parse(cls, s: str, /) -> Self:
        # TODO: Allow imperial units
        if (delta := parse_interval(s)) is None:
            raise ValueError(f"Cannot parse as pace: {s}")
        return cls(delta.total_seconds())


def pace(value: Any) -> Pace:
    if isinstance(value, str):
        return Pace.parse(value)
    else:
        return Pace(value)


def duration(value: Any) -> Duration:
    if isinstance(value, str):
        return Duration.parse(value)
    else:
        return Duration(value)


def distance(value: Any) -> Distance:
    if isinstance(value, str):
        return Distance.parse(value)
    else:
        return Distance(value)
