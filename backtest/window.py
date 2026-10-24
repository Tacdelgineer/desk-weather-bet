"""Backtest window and TRAIN/TEST split (see DECISIONS.md). Fitting code must call assert_train_only()."""
import datetime as dt

START = dt.date(2026, 6, 23)
END = dt.date(2026, 10, 20)  # inclusive; 120 market dates
DAYS = [START + dt.timedelta(d) for d in range((END - START).days + 1)]
SPLIT = DAYS[len(DAYS) // 2]  # first TEST date
TRAIN = [d for d in DAYS if d < SPLIT]
TEST = [d for d in DAYS if d >= SPLIT]
BET_HOUR_UTC = 16  # bets placed at 16:00 UTC on the day before the market date


def as_date(d):
    return d if isinstance(d, dt.date) and not isinstance(d, dt.datetime) else dt.date.fromisoformat(str(d)[:10])


def is_test(d):
    return as_date(d) >= SPLIT


def assert_train_only(dates):
    bad = sorted({str(as_date(d)) for d in dates if is_test(d)})
    assert not bad, f"fitting touched TEST dates: {bad[:5]}"


def bet_time(market_date):
    d = as_date(market_date) - dt.timedelta(days=1)
    return dt.datetime(d.year, d.month, d.day, BET_HOUR_UTC, tzinfo=dt.timezone.utc)
