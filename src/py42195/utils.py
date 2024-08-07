import math
from datetime import timedelta
from typing import Optional


def parse_interval(s: Optional[str], /) -> Optional[timedelta]:
    """Parse various intervals that can represent duration.

    :param s: Interval in the "[hh]:[mm]:ss[.sss]" format
    :return:
    """
    if not s:
        return None
    elif s in ["-", "nan", "np.nan"]:
        return None
    elif not isinstance(s, str):
        return TypeError(f"Expected string, got {type(s)}")

    try:
        frags = s.split(":")
        frags = [float(frag) for frag in frags]
        if len(frags) == 1:
            interval = timedelta(seconds=float(frags[0]))
        else:
            interval = timedelta(
                hours=frags[-3] if len(frags) == 3 else 0,
                minutes=frags[-2],
                seconds=frags[-1],
            )
        if not interval.total_seconds():
            return None
        else:
            return interval
    except ValueError:
        raise ValueError(f"Cannot parse as time: {s}")


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
