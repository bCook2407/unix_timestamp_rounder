"""Rounding helpers for UNIX timestamps and datetime objects.

We round to the boundary of the *current* unit, not the next one. That means
a timestamp at 12:34:56.7 rounded to the minute becomes 12:34:00 — the
floor of the minute bucket. This matches how "bucketing" is usually meant in
log aggregation and sampling: each sample is assigned to the window it falls
into. Half-up rounding (00:30 → 01:00) would split a contiguous period across
two buckets and is a different problem.

The boundary is computed in the UTC timezone. A tz-aware datetime with a
non-UTC offset may cross an hour boundary locally that doesn't exist in UTC,
or vice-versa. Rounding in UTC keeps the bucket assignment stable regardless
of the caller's local time. Naive datetimes are treated as UTC for the same
reason — "naive means UTC" is the least surprising choice for a library whose
unit is the UNIX second.
"""

from __future__ import annotations

import datetime as _dt

__all__ = ["round_timestamp", "round_datetime"]

_EPOCH = _dt.datetime(1970, 1, 1, tzinfo=_dt.timezone.utc)

# Bucket size in seconds for each supported unit.
_UNITS = {
    "second": 1,
    "minute": 60,
    "hour": 3600,
}


def round_timestamp(ts: float, unit: str = "second") -> int:
    """Floor a UNIX timestamp to the start of its bucket.

    Args:
        ts: Seconds since the UTC epoch. Fractional seconds are dropped — the
            return value is always an integer number of seconds.
        unit: One of "second", "minute", "hour".

    Returns:
        The floored UNIX timestamp as an int.

    Raises:
        ValueError: If *unit* is not recognised or *ts* is negative.

    Negative timestamps are rejected. UNIX time is defined relative to the
    1970 epoch, and negative values refer to dates before 1970. Rounding
    those is a different problem with its own edge cases (e.g. the year 0
    not existing in the proleptic Gregorian calendar) and we choose not to
    pretend to handle it.
    """
    if unit not in _UNITS:
        raise ValueError(
            f"unit must be one of {sorted(_UNITS)!r}, got {unit!r}"
        )
    if not isinstance(ts, (int, float)):
        raise TypeError(f"ts must be int or float, got {type(ts).__name__}")
    if ts < 0:
        raise ValueError(f"ts must be non-negative, got {ts!r}")

    size = _UNITS[unit]
    return int(ts) - (int(ts) % size)


def round_datetime(dt: _dt.datetime, unit: str = "second") -> _dt.datetime:
    """Floor a datetime to the start of its bucket, returned in UTC.

    Args:
        dt: The datetime to round. A tz-aware datetime is converted to UTC
            first. A naive datetime is assumed to already be UTC.
        unit: One of "second", "minute", "hour".

    Returns:
        A tz-aware datetime in UTC at the start of the bucket containing
        *dt*.

    Raises:
        ValueError: If *unit* is not recognised.

    See the module docstring for why rounding happens in UTC.
    """
    if unit not in _UNITS:
        raise ValueError(
            f"unit must be one of {sorted(_UNITS)!r}, got {unit!r}"
        )
    if not isinstance(dt, _dt.datetime):
        raise TypeError(
            f"dt must be a datetime.datetime, got {type(dt).__name__}"
        )

    if dt.tzinfo is None:
        aware = dt.replace(tzinfo=_dt.timezone.utc)
    else:
        aware = dt.astimezone(_dt.timezone.utc)

    ts = (aware - _EPOCH).total_seconds()
    floored = round_timestamp(ts, unit=unit)
    return _dt.datetime.fromtimestamp(floored, tz=_dt.timezone.utc)
