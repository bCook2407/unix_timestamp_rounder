# UNIX Timestamp Rounder

Floors a `datetime` or raw UNIX timestamp to the start of its current second, minute, or hour. Returns the bucket the value falls into, not the nearest boundary.

```python
from unix_timestamp_rounder import round_timestamp, round_datetime
import datetime as dt

# Floor a raw timestamp to the top of the minute.
assert round_timestamp(1700001899.7, "minute") == 1700001840

# Floor a datetime to the top of the hour. Naive datetimes are treated as UTC.
d = dt.datetime(2024, 1, 1, 12, 34, 56)
assert round_datetime(d, "hour") == dt.datetime(2024, 1, 1, 12, 0, 0, tzinfo=dt.timezone.utc)
```

## Why this exists

I needed to bucket events into fixed time windows for sampling and rate aggregation. Half-up rounding (00:30 → 01:00) splits a contiguous period across two buckets, which is wrong for that use case — you want every event assigned to the window it landed in. This library does only that: floor to the current bucket's start.

The trade-off: if you actually want nearest-boundary rounding, this is not the library for it. The two problems look similar but produce different results, and trying to support both in one API is where subtle bugs live. One behaviour, tested.

## The edge you will hit

Rounding is done in UTC. A timezone-aware datetime with a non-UTC offset is converted to UTC before the bucket is computed, so an event at `2024-01-01T07:34:56-05:00` rounds to `2024-01-01T12:34:00Z`. Naive datetimes are assumed to already be UTC. If your naive datetimes are actually local time, convert them yourself before calling in.

Negative timestamps (before 1970) are rejected — pre-epoch dates have their own edge cases and this library does not pretend to handle them.

## Exports

- `round_timestamp(ts: float, unit: str = "second") -> int` — floors a non-negative UNIX timestamp. `unit` is `"second"`, `"minute"`, or `"hour"`.
- `round_datetime(dt: datetime, unit: str = "second") -> datetime` — floors a datetime to the start of its bucket, returned as a tz-aware UTC datetime.

## Running the tests

```
PYTHONPATH=src python -m unittest discover -s tests
```

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

