"""v2 correction + the two pick guards, in the backtest (backtest/rolling.py, backtest/sim.py) and in bot/live.py."""
import datetime as dt
from types import SimpleNamespace

import pandas as pd
import pytest

import bot.live as live
from backtest import sim
from backtest.rolling import GFS_MAX_GAP_F, MAX_EDGE, MIN_DAYS, guard, rolling_correction

RUN = dt.date(2026, 10, 24)


def hist(n, bias=2.0, start=1):
    """n days of (date, actual, raw) ending `start` days before RUN, actual = raw + bias ± 1."""
    return [(RUN - dt.timedelta(days=start + i), 70 + bias + (1 if i % 2 else -1), 70.0) for i in range(n)]


# ---- correction ----
def test_rolling_bias_and_sigma():
    c = rolling_correction(hist(30), RUN)
    assert c["n"] == 30 and c["bias"] == pytest.approx(2.0) and c["sigma"] == pytest.approx(1.017, abs=1e-3)


def test_rolling_uses_only_the_30_days_before_the_run_date():
    future = [(RUN, 999.0, 0.0), (RUN + dt.timedelta(days=3), 999.0, 0.0)]  # run day itself and later: never used
    old = [(RUN - dt.timedelta(days=31), 999.0, 0.0)]                      # older than 30 days: not used
    assert rolling_correction(hist(30) + future + old, RUN)["bias"] == pytest.approx(2.0)


def test_rolling_skips_station_with_fewer_than_20_days():
    assert MIN_DAYS == 20
    assert rolling_correction(hist(19), RUN) is None
    assert rolling_correction(hist(20), RUN)["n"] == 20


# ---- guard (a): corrected high within 4 °F of GFS ----
def test_guard_gfs_gap():
    assert GFS_MAX_GAP_F == 4.0
    assert guard(85.49, 77.3, 0.10)            # the v1 Phoenix case (JOURNAL 2026-10-24) is skipped
    assert guard(81.4, 77.3, 0.10)             # 4.1 °F away
    assert guard(81.3, 77.3, 0.10) == ""       # 4.0 °F away is allowed
    assert guard(70.0, None, 0.10)             # no GFS -> can't check -> skip


# ---- guard (b): edge above 0.30 ----
def test_guard_edge_cap():
    assert MAX_EDGE == 0.30
    assert guard(70, 70, 0.30) == ""
    assert guard(70, 70, 0.31)
    assert guard(70, 70, 0.8453)               # the v1 Phoenix edge


# ---- both guards are applied by the backtest ----
def test_backtest_candidates_carry_guard():
    markets = pd.DataFrame([dict(city="X", station="KXXX", date="2026-09-01", split="TEST", ticker="T", strike_type="greater",
                                 floor=80.0, cap=None, yes_ask=0.05, no_ask=0.97, yes_bid=0.03, result="no", volume=1,
                                 actual=75.0)])
    fc = pd.DataFrame([dict(city="X", station="KXXX", date="2026-09-01", split="TEST", gfs_mu=75.0, gfs_sigma=2.0,
                            aifs_raw_mu=75.0, aifs_raw_sigma=2.0, aifs_cor_mu=86.0, aifs_cor_sigma=1.0)])
    c = sim.candidates(markets, fc).set_index("player")
    assert "from GFS" in c.loc["aifs_cor", "guard"]   # 11 °F from GFS
    assert c.loc["gfs", "guard"] == ""


# ---- both guards are applied by live.py ----
def cand(**kw):
    c = dict(ticker="KXHIGHTPHX-26OCT24-T82", side="yes", price=0.06, edge=0.12, mu=78.0, gfs_F=77.3)
    c.update(kw)
    return c


def test_live_choose_applies_gfs_guard():
    rules = {"threshold": 0.09, "judge_cutoff": None}
    assert live.choose([cand()], rules)
    assert live.choose([cand(mu=85.49)], rules) == []
    assert live.choose([cand(gfs_F=None)], rules) == []


def test_live_choose_applies_edge_cap():
    rules = {"threshold": 0.09, "judge_cutoff": None}
    assert live.choose([cand(edge=0.8453)], rules) == []
    assert live.choose([cand(edge=0.30)], rules)


def test_live_candidates_use_rolling_correction(monkeypatch):
    class K:
        def get(self, path, **kw):
            return {"markets": [dict(ticker="T", status="active", strike_type="greater", floor_strike=80, cap_strike=None,
                                     yes_ask_dollars="0.05", yes_bid_dollars="0.03", yes_sub_title="81° or above")]}
    highs = {"KPHX": dict(city="Phoenix", series="KXHIGHTPHX", raw_high_F=76.31)}
    out = live.candidates_for(RUN, highs, {"KPHX": dict(bias=1.5, sigma=2.0, n=30)}, {"KPHX": 77.3}, K())
    assert {c["mu"] for c in out} == {77.81} and all(c["guard"] == "" or "edge" in c["guard"] for c in out)
    assert live.candidates_for(RUN, highs, {"KPHX": None}, {"KPHX": 77.3}, K()) == []  # < 20 days -> skipped


def test_live_judge_input_matches_backtest_schema():
    """The judge must see the same JSON fields live as in the backtest (results/judge_inputs.csv)."""
    import json
    from pathlib import Path
    first = pd.read_csv(Path(__file__).resolve().parents[1] / "results" / "judge_inputs.csv", nrows=1).state[0]

    class K:
        def get(self, path, **kw):
            return {"markets": [dict(ticker="T", status="active", strike_type="greater", floor_strike=80, cap_strike=None,
                                     yes_ask_dollars="0.05", yes_bid_dollars="0.03", volume_fp="12.5")]}
    out = live.candidates_for(RUN, {"KPHX": dict(city="Phoenix", series="KXHIGHTPHX", raw_high_F=76.31)},
                              {"KPHX": dict(bias=1.5, sigma=2.0, n=30)}, {"KPHX": 77.3}, K())
    assert list(json.loads(out[0]["judge_state"])) == list(json.loads(first))
