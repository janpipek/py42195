import re
from datetime import timedelta
from functools import total_ordering
from typing import Any, Self

from typing_extensions import ClassVar, Optional

from py42195.constants import (
    FEET_IN_KM,
    HALF_MARATHON_IN_KM,
    M_IN_KM,
    MARATHON_IN_KM,
    MILES_IN_KM,
    YARDS_IN_KM,
)
from py42195.utils import format_interval, parse_interval


@total_ordering
class Distance:
    km: float

    MARATHON: ClassVar["Distance"]
    HALF_MARATHON: ClassVar["Distance"]

    ALLOWED_UNITS = ["km", "mi", "m", "yd", "ft"]
    PARSE_PATTERN: re.Pattern = re.compile(
        r"^(?P<value>\d+(\.\d+)?)\s*(?P<unit>km|mi|m|yd|ft)?$"
    )

    def __init__(
        self,
        km: Optional[float] = None,
        *,
        m: Optional[float] = None,
        mi: Optional[float] = None,
        yd: Optional[float] = None,
        ft: Optional[float] = None,
    ):
        if (
            len(
                args_given := [
                    unit for unit in self.ALLOWED_UNITS if locals().get(unit)
                ]
            )
            != 1
        ):
            raise ValueError(
                f"Exactly one of the following arguments should be provided: {', '.join(self.ALLOWED_UNITS)}, "
                f"got {len(args_given)}: {', '.join(args_given)}"
            )

        if km is not None:
            self.km = km
        elif m is not None:
            self.km = m * M_IN_KM
        elif yd is not None:
            self.km = yd * YARDS_IN_KM
        elif mi is not None:
            self.km = mi * MILES_IN_KM
        elif ft is not None:
            self.km = ft * FEET_IN_KM

        if not isinstance(self.km, (int, float)):
            raise TypeError(f"Expected a number, got {type(self.km)}")

    @property
    def mi(self) -> float:
        return self.km / MILES_IN_KM

    @classmethod
    def parse(cls, s: str) -> Self:
        # split into unit and value
        match = cls.PARSE_PATTERN.match(s)
        if match is None:
            raise ValueError(f"Cannot parse as distance: {s}")
        value = float(match.group("value"))
        unit = match.group("unit") or "km"
        return cls(**{unit: value})

    def __str__(self) -> str:
        return f"{self.km} km"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.km})"

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

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Distance(self.km / other)
        if isinstance(other, Distance):
            return self.km / other.km
        return NotImplemented

    def __eq__(self, other: object, /) -> bool:
        if isinstance(other, Distance):
            return self.km == other.km
        return NotImplemented

    def __lt__(self, other: object, /) -> bool:
        if isinstance(other, Distance):
            return self.km < other.km
        return NotImplemented


Distance.MARATHON = Distance(km=MARATHON_IN_KM)
Distance.HALF_MARATHON = Distance(km=HALF_MARATHON_IN_KM)


@total_ordering
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
        if isinstance(other, Pace):
            return Distance(self.seconds / other.seconds_per_km)
        if isinstance(other, Duration):
            return self.seconds / other.seconds
        return NotImplemented

    def __eq__(self, other: object, /) -> bool:
        if isinstance(other, Duration):
            return self.seconds == other.seconds
        if isinstance(other, timedelta):
            return self.seconds == other.total_seconds()
        return NotImplemented

    def __lt__(self, other: object, /) -> bool:
        if isinstance(other, Duration):
            return self.seconds < other.seconds
        if isinstance(other, timedelta):
            return self.seconds < other.total_seconds()
        return NotImplemented


@total_ordering
class Pace:
    seconds_per_km: float

    def __init__(
        self,
        seconds_per_km: Optional[float] = None,
        *,
        seconds_per_mile: Optional[float] = None,
    ):
        if (seconds_per_mile is not None) and (seconds_per_km is not None):
            raise ValueError(
                "Either seconds_per_mile or seconds_per_km should be provided"
            )
        elif seconds_per_km is not None:
            self.seconds_per_km = seconds_per_km
        elif seconds_per_mile is not None:
            self.seconds_per_km = seconds_per_mile / MILES_IN_KM
        else:
            raise ValueError(
                "Either seconds_per_mile or seconds_per_km should be provided"
            )

    @property
    def seconds_per_mile(self) -> float:
        return self.seconds_per_km * MILES_IN_KM

    def __str__(self):
        return format_interval(self.seconds_per_km)

    def __repr__(self) -> str:
        return f"pace('{self!s}')"

    def __add__(self, other):
        if isinstance(other, Pace):
            return Pace(self.seconds_per_km + other.seconds_per_km)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Pace):
            return Pace(self.seconds_per_km - other.seconds_per_km)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Pace(self.seconds_per_km * other)
        if isinstance(other, Distance):
            return Duration(self.seconds_per_km * other.km)
        else:
            return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Pace(self.seconds_per_km / other)
        if isinstance(other, Pace):
            return self.seconds_per_km / other.seconds_per_km
        return NotImplemented

    def __eq__(self, other: object, /) -> bool:
        if isinstance(other, Pace):
            return self.seconds_per_km == other.seconds_per_km
        return NotImplemented

    def __lt__(self, other: object, /) -> bool:
        if isinstance(other, Pace):
            return self.seconds_per_km < other.seconds_per_km
        return NotImplemented

    @classmethod
    def parse(cls, s: str, /) -> Self:
        # TODO: Allow imperial units
        if (delta := parse_interval(s)) is None:
            raise ValueError(f"Cannot parse as pace: {s}")
        return cls(delta.total_seconds())


def pace(value: Any, **kwargs) -> Pace:
    if isinstance(value, str):
        if kwargs:
            raise ValueError("Cannot provide kwargs when parsing from string")
        return Pace.parse(value)
    else:
        return Pace(value, **kwargs)


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
