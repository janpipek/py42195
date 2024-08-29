import math
import re
from datetime import timedelta

INTERVAL_PATTERN = r"((?P<hour>\d+:)?(?P<minute>\d?\d:))?(?P<second>\d?\d(\.\d+)?)"


def parse_interval(source: str, /) -> timedelta:
    """Parse various intervals that can represent duration.

    :param s: Interval in the "[hh]:[mm]:ss[.sss]" format
    """
    if not isinstance(source, str):
        raise TypeError(f"Expected string, got {type(source)}")
    if not (match := re.match(f"^{INTERVAL_PATTERN}$", source)):
        raise ValueError(f"Cannot parse as time: {source}")

    h, m = (int(match[i][:-1]) if match[i] else 0 for i in ("hour", "minute"))
    s = float(match["second"])

    if (h or m) and s >= 60:
        raise ValueError(f"Cannot parse as time: {source}")
    if h and m >= 60:
        raise ValueError(f"Cannot parse as time: {source}")

    return timedelta(hours=h, minutes=m, seconds=s)


def format_interval(
    interval: timedelta | float,
    /,
    *,
    # TODO: Change into format?
    int_seconds: bool = False,
) -> str:
    if isinstance(interval, timedelta):
        # TODO: Some other delta type?
        interval = interval.total_seconds()
    if not math.isfinite(interval):
        return "-"
    m, s = divmod(interval, 60)
    sec_text = str(int(s)) if int_seconds else f"{s:.1f}"
    if m >= 60:
        h, m = divmod(m, 60)
        return f"{int(h)}:{'0' if m < 10 else ''}{int(m)}:{'0' if s < 10 else ''}{sec_text}"
    else:
        return f"{int(m)}:{'0' if s < 10 else ''}{sec_text}"
