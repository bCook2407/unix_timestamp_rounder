import datetime as dt
import unittest

from unix_timestamp_rounder import round_timestamp, round_datetime


class TestRoundTimestamp(unittest.TestCase):

    def test_second_boundary_exact(self):
        self.assertEqual(round_timestamp(0), 0)

    def test_second_drops_fraction(self):
        self.assertEqual(round_timestamp(1.9), 1)

    def test_minute_boundary(self):
        # 12:34:56 -> 12:34:00
        ts = int((dt.datetime(2024, 1, 1, 12, 34, 56, tzinfo=dt.timezone.utc)
                  - dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)).total_seconds())
        floored = round_timestamp(ts, "minute")
        back = dt.datetime.fromtimestamp(floored, tz=dt.timezone.utc)
        self.assertEqual(back, dt.datetime(2024, 1, 1, 12, 34, 0, tzinfo=dt.timezone.utc))

    def test_minute_drops_seconds(self):
        ts = 61  # 1970-01-01T00:01:01Z
        self.assertEqual(round_timestamp(ts, "minute"), 60)

    def test_hour_boundary(self):
        # 12:34:56 -> 12:00:00
        ts = int((dt.datetime(2024, 1, 1, 12, 34, 56, tzinfo=dt.timezone.utc)
                  - dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)).total_seconds())
        floored = round_timestamp(ts, "hour")
        back = dt.datetime.fromtimestamp(floored, tz=dt.timezone.utc)
        self.assertEqual(back, dt.datetime(2024, 1, 1, 12, 0, 0, tzinfo=dt.timezone.utc))

    def test_returns_int(self):
        result = round_timestamp(1.5, "second")
        self.assertIsInstance(result, int)

    def test_invalid_unit(self):
        with self.assertRaises(ValueError):
            round_timestamp(100, "day")

    def test_negative_rejected(self):
        with self.assertRaises(ValueError):
            round_timestamp(-1, "second")

    def test_default_unit_is_second(self):
        self.assertEqual(round_timestamp(1.9), 1)


class TestRoundDatetime(unittest.TestCase):

    def test_naive_treated_as_utc(self):
        naive = dt.datetime(2024, 1, 1, 12, 34, 56)
        result = round_datetime(naive, "minute")
        self.assertEqual(result, dt.datetime(2024, 1, 1, 12, 34, 0, tzinfo=dt.timezone.utc))

    def test_aware_converted_to_utc(self):
        # 2024-01-01T07:34:56-05:00 == 2024-01-01T12:34:56Z
        tz = dt.timezone(dt.timedelta(hours=-5))
        aware = dt.datetime(2024, 1, 1, 7, 34, 56, tzinfo=tz)
        result = round_datetime(aware, "minute")
        self.assertEqual(result, dt.datetime(2024, 1, 1, 12, 34, 0, tzinfo=dt.timezone.utc))

    def test_already_on_minute_boundary(self):
        on_boundary = dt.datetime(2024, 1, 1, 12, 34, 0, tzinfo=dt.timezone.utc)
        result = round_datetime(on_boundary, "minute")
        self.assertEqual(result, on_boundary)

    def test_hour_with_minutes_and_seconds(self):
        d = dt.datetime(2024, 6, 15, 23, 59, 59, tzinfo=dt.timezone.utc)
        result = round_datetime(d, "hour")
        self.assertEqual(result, dt.datetime(2024, 6, 15, 23, 0, 0, tzinfo=dt.timezone.utc))

    def test_result_is_utc(self):
        naive = dt.datetime(2024, 1, 1, 0, 0, 0)
        result = round_datetime(naive, "hour")
        self.assertEqual(result.tzinfo, dt.timezone.utc)

    def test_invalid_unit(self):
        with self.assertRaises(ValueError):
            round_datetime(dt.datetime(2024, 1, 1), "week")


if __name__ == "__main__":
    unittest.main()
