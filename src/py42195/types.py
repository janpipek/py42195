import re
from datetime import timedelta
from functools import total_ordering
from typing import Any, Self

from typing_extensions import ClassVar, Optional

from py42195.config import get_default_unit, get_unit_system
from py42195.constants import (
    FEET_IN_KM,
    HALF_MARATHON_IN_KM,
    M_IN_KM,
    MARATHON_IN_KM,
    MILES_IN_KM,
    YARDS_IN_KM,
)
from py42195.utils import INTERVAL_PATTERN, format_interval, parse_interval


@total_ordering
class Distance:
    km: float

    MARATHON: ClassVar["Distance"]
    HALF_MARATHON: ClassVar["Distance"]

    ALLOWED_UNITS = ["km", "mi", "m", "yd", "ft"]
    PARSE_PATTERN: re.Pattern = re.compile(
        r"^(?P<value>\d+(\.\d+)?)\s*(?P<unit>" + "|".join(ALLOWED_UNITS) + ")?$"
    )

    def __init__(
        self,
        *,
        km: Optional[float] = None,
        m: Optional[float] = None,
        mi: Optional[float] = None,
        yd: Optional[float] = None,
        ft: Optional[float] = None,
    ):
        args_given = [
            unit
            for unit, val in locals().items()
            if unit in self.ALLOWED_UNITS and val is not None
        ]
        if len(args_given) != 1:
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
        if get_unit_system() == "imperial":
            return f"{self.mi:.2f} mi"
        return f"{self.km:.2f} km"

    def __repr__(self) -> str:
        if get_unit_system() == "imperial":
            return f"Distance(mi={self.mi})"
        return f"Distance(km={self.km})"

    def __add__(self, other: "Distance") -> "Distance":
        if isinstance(other, Distance):
            return Distance(km=self.km + other.km)
        return NotImplemented

    def __radd__(self, other: Any) -> "Distance":
        if other == 0:
            # Support sum
            return self
        return other + self

    def __sub__(self, other: "Distance") -> "Distance":
        if isinstance(other, Distance):
            return Distance(km=self.km - other.km)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Distance(km=self.km * other)
        if isinstance(other, Pace):
            return Duration(self.km * other.seconds_per_km)
        else:
            return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Distance(km=self.km / other)
        if isinstance(other, Distance):
            return self.km / other.km
        if isinstance(other, Duration):
            return Speed(km_h=self.km / (other.seconds * 3600))
        if isinstance(other, Speed):
            return Duration(self.km / other.km_h * 3600)
        return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, timedelta):
            return Duration(other) / self
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

    def __radd__(self, other: Any) -> "Duration":
        if other == 0:
            # Support sum
            return self
        return other + self

    def __sub__(self, other: "Duration") -> "Duration":
        if isinstance(other, Duration):
            return Duration(self.seconds - other.seconds)
        return NotImplemented

    def __mul__(self, other: Any) -> Any:
        if isinstance(other, (int, float)):
            return Duration(self.seconds * other)
        if isinstance(other, Speed):
            return Distance(km=self.seconds * other.km_h / 3600)
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Duration(self.seconds / other)
        if isinstance(other, Distance):
            return Pace(seconds_per_km=self.seconds / other.km)
        if isinstance(other, Pace):
            return Distance(km=self.seconds / other.seconds_per_km)
        if isinstance(other, Duration):
            return self.seconds / other.seconds
        if isinstance(other, timedelta):
            return self.seconds / other.total_seconds()
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

    ALLOWED_UNITS = {
        "/km": "seconds_per_km",
        "/mi": "seconds_per_mile",
    }
    PARSE_PATTERN: re.Pattern = re.compile(
        f"^(?P<interval>{INTERVAL_PATTERN})\\s*(?P<unit>"
        + "|".join(ALLOWED_UNITS)
        + ")?$"
    )

    def __init__(
        self,
        *,
        seconds_per_km: Optional[float] = None,
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

    def __str__(self) -> str:
        if get_unit_system() == "imperial":
            return format_interval(self.seconds_per_mile) + "/mi"
        return format_interval(self.seconds_per_km) + "/km"

    def __repr__(self) -> str:
        if get_unit_system() == "imperial":
            return f"Pace(seconds_per_mile={self.seconds_per_mile})"
        return f"Pace(seconds_per_km={self.seconds_per_km})"

    def __add__(self, other):
        if isinstance(other, Pace):
            return Pace(seconds_per_km=self.seconds_per_km + other.seconds_per_km)
        return NotImplemented

    def __radd__(self, other: Any) -> "Pace":
        if other == 0:
            # Support sum
            return self
        return other + self

    def __sub__(self, other):
        if isinstance(other, Pace):
            return Pace(seconds_per_km=self.seconds_per_km - other.seconds_per_km)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Pace(seconds_per_km=self.seconds_per_km * other)
        if isinstance(other, Distance):
            return Duration(self.seconds_per_km * other.km)
        else:
            return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Pace(seconds_per_km=self.seconds_per_km / other)
        if isinstance(other, Pace):
            return self.seconds_per_km / other.seconds_per_km
        return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, timedelta):
            return Duration(other) / self
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
        match = re.match(cls.PARSE_PATTERN, s)
        if not match:
            raise ValueError(f"Cannot parse as pace: {s}")
        unit = cls.ALLOWED_UNITS.get(match.group("unit")) or get_default_unit(cls)
        value = parse_interval(match.group("interval")).total_seconds()
        return cls(**{unit: value})

    def to_speed(self) -> "Speed":
        return Speed(km_h=3600 / self.seconds_per_km)


@total_ordering
class Speed:
    km_h: float

    ALLOWED_UNITS = {
        "kmh": "km_h",
        "km/h": "km_h",
        "mph": "mph",
        "mi/h": "mph",
        "m/s": "m_s",
    }
    PARSE_PATTERN: re.Pattern = re.compile(
        r"^(?P<value>\d+(\.\d+)?)\s*(?P<unit>" + "|".join(ALLOWED_UNITS) + ")?$"
    )

    def __init__(
        self,
        *,
        km_h: Optional[float] = None,
        mph: Optional[float] = None,
        m_s: Optional[float] = None,
    ) -> None:
        args_given = [
            unit
            for unit, val in locals().items()
            if unit in self.ALLOWED_UNITS.values() and val is not None
        ]
        if len(args_given) != 1:
            raise ValueError(
                f"Exactly one of the following arguments should be provided: {', '.join(self.ALLOWED_UNITS)}, "
                f"got {len(args_given)}: {', '.join(args_given)}"
            )

        if km_h is not None:
            self.km_h = km_h
        elif mph is not None:
            self.km_h = mph * MILES_IN_KM
        elif m_s is not None:
            self.km_h = m_s * 3600 / 1000

        if not isinstance(self.km_h, (int, float)):
            raise ValueError("Speed should be a number.")

    def __lt__(self, other: object, /) -> bool:
        if isinstance(other, Speed):
            return self.km_h < other.km_h
        return NotImplemented

    def __eq__(self, other: object, /) -> bool:
        if isinstance(other, Speed):
            return self.km_h == other.km_h
        return NotImplemented

    @classmethod
    def parse(cls, s: str) -> Self:
        # split into unit and value
        match = cls.PARSE_PATTERN.match(s)
        if match is None:
            raise ValueError(f"Cannot parse as speed: {s}")
        value = float(match.group("value"))
        unit = cls.ALLOWED_UNITS.get(match.group("unit")) or "km_h"
        return cls(**{unit: value})

    @property
    def m_s(self) -> float:
        return self.km_h * 1000 / 3600

    @property
    def mph(self) -> float:
        return self.km_h / MILES_IN_KM

    def to_pace(self) -> Pace:
        return Pace(seconds_per_km=3600 / self.km_h)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Speed(km_h=self.km_h * other)
        if isinstance(other, Duration):
            return Distance(km=self.km_h * other.seconds / 3600)
        else:
            return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __add__(self, other, /):
        if isinstance(other, Speed):
            return Speed(km_h=self.km_h + other.km_h)
        return NotImplemented

    def __radd__(self, other: Any) -> "Speed":
        if other == 0:
            # Support sum
            return self
        return other + self

    def __sub__(self, other, /):
        if isinstance(other, Speed):
            return Speed(km_h=self.km_h - other.km_h)
        return NotImplemented

    def __truediv__(self, other, /):
        if isinstance(other, (int, float)):
            return Speed(km_h=self.km_h / other)
        if isinstance(other, Speed):
            return self.km_h / other.km_h
        return NotImplemented

    def __str__(self):
        return f"{self.km_h:.2f} km/h"

    def __repr__(self) -> str:
        return f"speed('{self!s}')"


def pace(value: Any, **kwargs) -> Pace:
    if isinstance(value, str):
        if kwargs:
            raise ValueError("Cannot provide kwargs when parsing from string")
        return Pace.parse(value)
    else:
        default_unit = get_default_unit(Pace)
        return Pace(**(kwargs | {default_unit: value}))


def duration(value: Any) -> Duration:
    """Construct a Duration object from various types."""
    if isinstance(value, str):
        return Duration.parse(value)
    if isinstance(value, Duration):
        return value
    else:
        return Duration(value)


def distance(value: Any, **kwargs) -> Distance:
    if isinstance(value, str):
        return Distance.parse(value)
    if isinstance(value, Distance):
        return value
    else:
        default_unit = get_default_unit(Distance)
        return Distance(**(kwargs | {default_unit: value}))


def speed(value: Any, **kwargs) -> Speed:
    if isinstance(value, str):
        return Speed.parse(value)
    if isinstance(value, Speed):
        return value
    else:
        default_unit = get_default_unit(Speed)
        return Speed(**(kwargs | {default_unit: value}))
