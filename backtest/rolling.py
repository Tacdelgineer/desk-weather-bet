"""v2 station correction + pick guards, shared by the backtest and bot/live.py (see video/JOURNAL.md 2026-10-24).

Correction: for a forecast made on run date R (bet for market date R+1), bias = mean(actual - raw AIFS high) over
that station's market dates in [R-30, R-1], sigma = std of the same 30 differences. Past data only: every date used
is before R, so the high is settled when the bet is made. Fewer than MIN_DAYS of the 30 -> no forecast (skip).
Corrected high = raw + bias. Nothing is fitted, so there is no slope to extrapolate when the season changes.

Guards (skip the pick):
  (a) corrected high more than GFS_MAX_GAP_F from the GFS forecast for that station and day (or GFS missing);
  (b) edge above MAX_EDGE.
"""
import datetime as dt

import numpy as np

WINDOW_DAYS = 30
MIN_DAYS = 20
GFS_MAX_GAP_F = 4.0
MAX_EDGE = 0.30


def as_date(d):
    return d if isinstance(d, dt.date) and not isinstance(d, dt.datetime) else dt.date.fromisoformat(str(d)[:10])


def window(run_date):
    r = as_date(run_date)
    return r - dt.timedelta(days=WINDOW_DAYS), r - dt.timedelta(days=1)


def rolling_correction(history, run_date):
    """history: iterable of (date, actual, raw) for ONE station. Returns dict(bias, sigma, n) or None (< MIN_DAYS)."""
    a, b = window(run_date)
    diffs = []
    for d, actual, raw in history:
        d = as_date(d)
        if a <= d <= b and actual is not None and raw is not None and not (np.isnan(actual) or np.isnan(raw)):
            assert d < as_date(run_date), f"correction used {d}, not before run date {run_date}"
            diffs.append(float(actual) - float(raw))
    if len(diffs) < MIN_DAYS:
        return None
    return dict(bias=float(np.mean(diffs)), sigma=float(np.std(diffs, ddof=1)), n=len(diffs))


def guard(mu, gfs, edge):
    """Reason to skip this pick, or '' if it may go ahead."""
    if gfs is None or (isinstance(gfs, float) and np.isnan(gfs)):
        return "no GFS forecast to check against"
    if abs(mu - gfs) > GFS_MAX_GAP_F:
        return f"corrected high {mu:.1f}F is {abs(mu - gfs):.1f}F from GFS {gfs:.1f}F (> {GFS_MAX_GAP_F:g})"
    if edge > MAX_EDGE:
        return f"edge {edge:.3f} > {MAX_EDGE:g}"
    return ""
