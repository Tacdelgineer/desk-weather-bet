"""Unit tests for every hard cap in bot/live.py and for DRY_RUN."""
import datetime as dt
import json
from types import SimpleNamespace

import pytest

import bot.live as live

NOW = dt.datetime(2026, 10, 24, 16, 0, tzinfo=dt.timezone.utc)
DAY = dt.date(2026, 10, 24)


class FakeKalshi:
    def __init__(self):
        self.calls = []

    def request(self, method, path, json=None, **kw):
        self.calls.append((method, path, json))
        return {"order": {"order_id": f"o{len(self.calls)}", "status": "resting"}}

    def get(self, path, **kw):
        self.calls.append(("GET", path, kw))
        return {"order": {"status": "resting", "fill_count_fp": "0"}}


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(live, "ROOT", tmp_path)
    monkeypatch.setattr(live, "LEDGER", tmp_path / "ledger.json")
    monkeypatch.setattr(live, "LOGDIR", tmp_path / "logs")
    monkeypatch.setattr(live, "RULES", tmp_path / "RULES.json")
    return tmp_path


def pick(ticker="KXHIGHNY-26OCT25-B60.5", price=0.30, side="yes"):
    n = live.size_for(price, live.MAX_PER_MARKET)
    f = live.fee(price, n)
    return dict(ticker=ticker, side=side, price=price, contracts=n, fee=f, max_cost=round(n * price + f, 4), edge=0.1,
                p_side=0.45, mu=60.0, sigma=2.0)


def test_constants():
    assert live.MAX_PER_MARKET == 1.00
    assert live.MAX_NEW_ORDERS_PER_DAY == 2
    assert live.ORDER_TYPE == "limit"
    assert live.CANCEL_AFTER_HOURS == 3
    assert live.DEFAULT_BUDGET == 10.0


def test_budget_from_go_live(sandbox):
    assert live.budget() == 0.0                        # no GO_LIVE -> nothing to spend
    (sandbox / "GO_LIVE").write_text("10\n")
    assert live.budget() == 10.0
    (sandbox / "GO_LIVE").write_text("")
    assert live.budget() == live.DEFAULT_BUDGET
    (sandbox / "GO_LIVE").write_text("500")
    assert live.budget() == live.MAX_BUDGET            # can't be raised above the cap


def test_total_spend_cap(sandbox):
    led = {"orders": [dict(ticker=f"T{i}", max_cost=1.0, placed_day=f"2026-10-{10 + i}", status="filled")
                      for i in range(10)], "picks": []}
    with pytest.raises(live.CapError, match="budget"):
        live.check_caps(led, str(DAY), dict(pick(), type="limit"), 10.0)
    led["orders"] = led["orders"][:9]
    live.check_caps(led, str(DAY), dict(pick(), type="limit"), 10.0)  # 9 + ~1 fits


def test_per_market_cap(sandbox):
    p = dict(pick(), type="limit")
    assert p["max_cost"] <= 1.0
    with pytest.raises(live.CapError, match="per market"):
        live.check_caps({"orders": []}, str(DAY), dict(p, max_cost=1.01), 10.0)
    with pytest.raises(live.CapError, match="already"):
        live.check_caps({"orders": [dict(p, placed_day="2026-10-01", status="filled")]}, str(DAY), p, 10.0)
    for price in (0.01, 0.05, 0.33, 0.5, 0.97):          # sizing never exceeds $1 incl. fee
        n = live.size_for(price, 1.0)
        assert n * price + live.fee(price, n) <= 1.0 + 1e-9


def test_two_orders_per_day(sandbox):
    led = {"orders": [dict(ticker=f"T{i}", max_cost=0.9, placed_day=str(DAY), status="resting") for i in range(2)]}
    with pytest.raises(live.CapError, match="per day"):
        live.check_caps(led, str(DAY), dict(pick(), type="limit"), 10.0)
    picks = live.choose([dict(pick(f"M{i}"), edge=0.2 + i / 100) for i in range(5)], {"threshold": 0.04})
    assert len(picks) == 2


def test_limit_only(sandbox):
    with pytest.raises(live.CapError, match="limit"):
        live.check_caps({"orders": []}, str(DAY), dict(pick(), type="market"), 10.0)
    body = live.order_body(dict(pick(), client_order_id="x", count=3), NOW)
    assert body["time_in_force"] == "good_till_canceled" and "price" in body


def test_order_body_sides():
    b = live.order_body(dict(ticker="T", side="no", price=0.70, count=1, client_order_id="c"), NOW)
    assert b["side"] == "ask" and b["price"] == "0.3000"      # buy NO at 70c == ask on YES book at 30c
    b = live.order_body(dict(ticker="T", side="yes", price=0.25, count=4, client_order_id="c"), NOW)
    assert b["side"] == "bid" and b["price"] == "0.2500" and b["count"] == "4.00"


def test_expiry_three_hours():
    b = live.order_body(dict(ticker="T", side="yes", price=0.25, count=4, client_order_id="c"), NOW)
    assert b["expiration_time"] == int((NOW + dt.timedelta(hours=3)).timestamp())


def test_cancel_unfilled_after_3h(sandbox):
    led = {"orders": [dict(pick(), type="limit", count=3, placed_day=str(DAY), order_id="o1", status="resting",
                           placed_at=NOW.isoformat())], "picks": []}
    live.save_ledger(led)
    k = FakeKalshi()
    assert live.job_cancel(DAY, kalshi=k, now=NOW + dt.timedelta(hours=2))["canceled"] == []   # too early
    res = live.job_cancel(DAY, kalshi=k, now=NOW + dt.timedelta(hours=3, minutes=1))
    assert res["canceled"][0]["status"] == "canceled_unfilled"
    assert ("DELETE", "/portfolio/events/orders/o1", None) in k.calls
    assert live.committed_spend(live.load_ledger()) == 0.0


def test_dry_run_without_go_live(sandbox, monkeypatch):
    monkeypatch.setattr(live, "rules_locked", lambda: True)
    ok, why = live.live_mode()
    assert not ok and "no GO_LIVE file" in why
    (sandbox / "GO_LIVE").write_text("10")
    assert live.live_mode()[0]
    (sandbox / "STOP").write_text("")
    assert not live.live_mode()[0]


def test_dry_run_requires_rules_locked(sandbox, monkeypatch):
    (sandbox / "GO_LIVE").write_text("10")
    monkeypatch.setattr(live, "rules_locked", lambda: False)
    ok, why = live.live_mode()
    assert not ok and any("rules-locked" in w for w in why)


def test_dry_run_places_no_orders(sandbox, monkeypatch):
    """Full picks job in DRY_RUN: logs would-be orders, never calls the order API."""
    monkeypatch.setattr(live, "forecast_path", lambda init: sandbox / "f.npz")
    (sandbox / "f.npz").write_text("x")
    monkeypatch.setattr(live, "station_highs", lambda init, d: {})
    monkeypatch.setattr(live, "candidates_for", lambda d, h, r, k: [pick(), pick("OTHER", 0.2, "no")])
    monkeypatch.setattr(live, "post_issue", lambda text: "posted")
    monkeypatch.setattr("bot.kalshi.Kalshi", lambda *a, **k: FakeKalshi())
    (sandbox / "RULES.json").write_text(json.dumps({"threshold": 0.04, "judge_cutoff": None, "player": "x"}))
    k = FakeKalshi()
    res = live.job_picks(DAY, kalshi=k, now=NOW)
    assert res["mode"] == "DRY_RUN" and len(res["would_order"]) == 2
    assert not any(c[0] == "POST" for c in k.calls)
    assert live.load_ledger()["orders"] == []


def test_issue_posts_only_as_channel_account(sandbox, monkeypatch, tmp_path):
    monkeypatch.setattr(live, "ISSUE_FILE", tmp_path / "LIVE_ISSUE")
    assert live.post_issue("x").startswith("no issue configured")
    (tmp_path / "LIVE_ISSUE").write_text("1\n")
    calls = []

    def fake_run(cmd, **kw):
        calls.append(cmd)
        return SimpleNamespace(stdout="SomeoneElse\n", stderr="", returncode=0)
    monkeypatch.setattr(live.subprocess, "run", fake_run)
    assert live.post_issue("x").startswith("not posted")
    assert not any("comment" in c for c in calls)
