"""Live bot — the ONLY code allowed to place orders (see CLAUDE.md "Money and safety rules").

Daily jobs (UTC):
  forecast  ~08:30  run AIFS locally from today's 00Z ECMWF open data, lead 60 h  -> data/aifs_runs/
  picks     ~16:00  settle older picks, read live asks for tomorrow's markets, choose picks with the locked rule,
                    post them to the "Live picks log" issue, and place limit orders ONLY if every gate is open
  cancel    ~19:05  cancel any of today's orders still resting (unfilled after 3 h)

Default is DRY_RUN: without GO_LIVE (or with STOP, or without the rules-locked tag) it logs exactly what it would
have ordered and orders nothing.

  uv run python bot/live.py forecast|picks|cancel|settle [--date YYYY-MM-DD]
"""
import argparse
import datetime as dt
import json
import math
import subprocess
import sys
import uuid
from types import SimpleNamespace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backtest.fees import fee  # noqa: E402
from backtest.sim import bracket_prob  # noqa: E402

# ---- hard caps (constants; each has a unit test in tests/test_live.py) ----
DEFAULT_BUDGET = 10.0          # dollars, used when GO_LIVE holds no number
MAX_BUDGET = 10.0              # GO_LIVE can't raise the total above this
MAX_PER_MARKET = 1.00          # dollars incl. fee
MAX_NEW_ORDERS_PER_DAY = 2
ORDER_TYPE = "limit"           # limit orders only
CANCEL_AFTER_HOURS = 3

LEDGER = ROOT / "results" / "live_ledger.json"
LOGDIR = ROOT / "logs" / "live"
RULES = ROOT / "RULES.json"     # machine-readable copy of the locked rules (committed with RULES.md)


class CapError(Exception):
    pass


# ---------------- gates ----------------
def budget():
    f = ROOT / "GO_LIVE"
    if not f.exists():
        return 0.0
    try:
        b = float(f.read_text().strip() or DEFAULT_BUDGET)
    except ValueError:
        b = DEFAULT_BUDGET
    return max(0.0, min(b, MAX_BUDGET))


def rules_locked():
    """RULES.md committed, tagged rules-locked, and unchanged since the tag."""
    try:
        subprocess.run(["git", "rev-parse", "-q", "--verify", "refs/tags/rules-locked"], cwd=ROOT, check=True,
                       capture_output=True)
        for f in ("RULES.md", "RULES.json"):
            subprocess.run(["git", "diff", "--quiet", "rules-locked", "--", f], cwd=ROOT, check=True)
            subprocess.run(["git", "diff", "--quiet", "--", f], cwd=ROOT, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def live_mode():
    """Return (is_live, reasons_if_not)."""
    why = []
    if not (ROOT / "GO_LIVE").exists():
        why.append("no GO_LIVE file")
    if (ROOT / "STOP").exists():
        why.append("STOP file present")
    if not rules_locked():
        why.append("RULES.md not committed+tagged rules-locked (or changed since)")
    return (not why), why


# ---------------- ledger ----------------
def load_ledger():
    if LEDGER.exists():
        return json.loads(LEDGER.read_text())
    return {"orders": [], "picks": []}


def save_ledger(led):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    tmp = LEDGER.with_suffix(".tmp")
    tmp.write_text(json.dumps(led, indent=1))
    tmp.replace(LEDGER)


def committed_spend(led):
    """Worst-case dollars committed by live orders: filled cost + resting max cost (incl. fees)."""
    return round(sum(o["max_cost"] for o in led["orders"] if o.get("status") != "canceled_unfilled"), 4)


def orders_on(led, day):
    return [o for o in led["orders"] if o["placed_day"] == day]


def size_for(price, budget_left):
    c = int(min(MAX_PER_MARKET, budget_left) // price)
    while c > 0 and c * price + fee(price, c) > min(MAX_PER_MARKET, budget_left) + 1e-9:
        c -= 1
    return c


def check_caps(led, day, order, total_budget):
    """Raise CapError unless this new order respects every cap."""
    if order["type"] != ORDER_TYPE:
        raise CapError("limit orders only")
    if order["max_cost"] > MAX_PER_MARKET + 1e-9:
        raise CapError(f"over ${MAX_PER_MARKET} per market")
    if any(o["ticker"] == order["ticker"] for o in led["orders"]):
        raise CapError("already ordered this market")
    if len(orders_on(led, day)) >= MAX_NEW_ORDERS_PER_DAY:
        raise CapError(f"max {MAX_NEW_ORDERS_PER_DAY} new orders per day")
    if committed_spend(led) + order["max_cost"] > total_budget + 1e-9:
        raise CapError(f"total spend would exceed budget ${total_budget}")


# ---------------- forecast ----------------
def forecast_path(init):
    return ROOT / "data" / "aifs_runs" / f"{init:%Y%m%d%H}_60h.npz"


def job_forecast(day):
    init = dt.datetime(day.year, day.month, day.day, 0)
    if forecast_path(init).exists():
        return {"forecast": "exists", "init": init.isoformat()}
    cmd = [str(Path.home() / ".local/bin/uv"), "run", "--project", "model/aifs", "python", "model/run_aifs.py",
           "--date", f"{init:%Y-%m-%dT%H}", "--lead", "60"]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    tail = [l for l in (r.stdout + r.stderr).splitlines() if "step" in l or "saved" in l or "Error" in l][-4:]
    return {"forecast": "ok" if r.returncode == 0 else f"failed ({r.returncode})", "init": init.isoformat(),
            "tail": tail}


def station_highs(init, market_day):
    """Raw AIFS high per station for market_day from our local run (max of 6-hourly 2t in the LST day)."""
    from fetch.gfs import LST_OFFSET
    z = np.load(forecast_path(init))
    lat, lon = z["lat"], z["lon"]
    cities = json.loads((ROOT / "results" / "cities.json").read_text())
    out = {}
    for c in cities:
        d = np.radians
        dist = np.arccos(np.clip(np.sin(d(lat)) * np.sin(d(c["lat"])) + np.cos(d(lat)) * np.cos(d(c["lat"]))
                                 * np.cos(d(lon - (c["lon"] % 360))), -1, 1))
        k = int(np.argmin(dist))
        a = dt.datetime(market_day.year, market_day.month, market_day.day) - dt.timedelta(hours=LST_OFFSET[c["tz"]])
        vals = [float(z["2t"][i, k]) for i, s in enumerate(z["steps"])
                if a <= init + dt.timedelta(hours=int(s)) < a + dt.timedelta(days=1)]
        out[c["station"]] = dict(city=c["city"], series=c["series"], raw_high_F=round(max((v - 273.15) * 9 / 5 + 32 for v in vals), 2),
                                 n=len(vals), grid=[float(lat[k]), float(lon[k])])
    return out


# ---------------- picks ----------------
MON = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()


def event_ticker(series, d):
    return f"{series}-{d:%y}{MON[d.month - 1]}{d:%d}"


def choose(cands, rules):
    """Locked rule: candidates with edge > threshold (and judge P(bet) > cut-off if the judge player is live),
    best edge first, one per market, at most MAX_NEW_ORDERS_PER_DAY."""
    ok = [c for c in cands if c["edge"] > rules["threshold"]]
    if rules.get("judge_cutoff") is not None:
        ok = [c for c in ok if c.get("p_bet", 0) > rules["judge_cutoff"]]
    ok.sort(key=lambda c: -c["edge"])
    seen, out = set(), []
    for c in ok:
        if c["ticker"] in seen:
            continue
        seen.add(c["ticker"])
        out.append(c)
        if len(out) == MAX_NEW_ORDERS_PER_DAY:
            break
    return out


def candidates_for(market_day, highs, rules, kalshi):
    corr = json.loads((ROOT / "results" / "corrections.json").read_text())
    out = []
    for st, h in highs.items():
        c = corr[st]["aifs_high"]
        mu, sigma = c["a"] + c["b"] * h["raw_high_F"], c["sigma"]
        ms = kalshi.get("/markets", event_ticker=event_ticker(h["series"], market_day), limit=100).get("markets", [])
        for m in ms:
            if m.get("status") not in ("active", "open"):
                continue
            row = SimpleNamespace(strike_type=m["strike_type"], floor=m.get("floor_strike"), cap=m.get("cap_strike"))
            p = float(bracket_prob(row, mu, sigma))
            ya = float(m.get("yes_ask_dollars") or 0)
            yb = float(m.get("yes_bid_dollars") or 0)
            for side, price, pw in (("yes", ya, p), ("no", round(1 - yb, 4), 1 - p)):
                if not (0.01 <= price <= 0.99):
                    continue
                n = size_for(price, MAX_PER_MARKET)
                if n == 0:
                    continue
                f = fee(price, n)
                out.append(dict(ticker=m["ticker"], city=h["city"], station=st, side=side, price=price, contracts=n,
                                fee=f, max_cost=round(n * price + f, 4), p_side=round(pw, 4),
                                edge=round(pw - price - f / n, 4), mu=round(mu, 2), sigma=round(sigma, 2),
                                raw_high_F=h["raw_high_F"], yes_sub_title=m.get("yes_sub_title")))
    return out


def post_issue(text):
    issue = json.loads(RULES.read_text()).get("issue") if RULES.exists() else None
    if not issue:
        return "no issue configured"
    r = subprocess.run(["gh", "issue", "comment", str(issue), "--repo", "Tacdelgineer/desk-weather-bet",
                        "--body", text], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() or r.stderr.strip()[:200]


def order_body(order, now):
    """Kalshi Create Order V2 body: single YES book, price is always the YES price.
    Buy YES at p -> side "bid" at p; buy NO at q -> side "ask" at YES price 1 - q (docs: order_direction).
    A limit order that rests at most CANCEL_AFTER_HOURS (good_till_canceled + expiration_time)."""
    yes_price = order["price"] if order["side"] == "yes" else round(1 - order["price"], 4)
    return {"ticker": order["ticker"], "client_order_id": order["client_order_id"],
            "side": "bid" if order["side"] == "yes" else "ask", "count": f"{order['count']:.2f}",
            "price": f"{yes_price:.4f}", "time_in_force": "good_till_canceled",
            "expiration_time": int((now + dt.timedelta(hours=CANCEL_AFTER_HOURS)).timestamp()),
            "self_trade_prevention_type": "taker_at_cross", "post_only": False, "reduce_only": False}


def place(kalshi, led, day, pick, total_budget, now):
    order = dict(ticker=pick["ticker"], side=pick["side"], type=ORDER_TYPE, count=pick["contracts"],
                 price=pick["price"], max_cost=pick["max_cost"], placed_day=str(day), placed_at=now.isoformat(),
                 client_order_id=str(uuid.uuid4()), status="pending")
    check_caps(led, str(day), order, total_budget)
    body = order_body(order, now)
    led["orders"].append(order)        # record before sending, so a crash can't double-spend
    save_ledger(led)
    r = kalshi.request("POST", "/portfolio/events/orders", json=body)
    o = r.get("order", r)
    order.update(order_id=o.get("order_id"), status=o.get("status", "sent"))
    save_ledger(led)
    return order


def job_picks(day, kalshi=None, now=None):
    from bot.kalshi import Kalshi
    now = now or dt.datetime.now(dt.timezone.utc)
    market_day = day + dt.timedelta(days=1)
    rules = json.loads(RULES.read_text()) if RULES.exists() else {"threshold": 0.04, "judge_cutoff": None,
                                                                  "player": "aifs_cor (rules not written yet)"}
    is_live, why = live_mode()
    total_budget = budget() if is_live else 0.0
    led = load_ledger()
    res = {"day": str(day), "market_day": str(market_day), "mode": "LIVE" if is_live else "DRY_RUN",
           "dry_run_reasons": why, "player": rules.get("player"), "threshold": rules["threshold"]}
    init = dt.datetime(day.year, day.month, day.day, 0)
    if not forecast_path(init).exists():
        res["picks"] = []
        res["note"] = "no AIFS forecast for today — no picks"
        return res
    public = Kalshi(auth=False)
    highs = station_highs(init, market_day)
    cands = candidates_for(market_day, highs, rules, public)
    if rules.get("judge_cutoff") is not None:
        cands = judge_annotate(cands)
    picks = choose(cands, rules)
    res.update(highs=highs, n_candidates=len(cands), picks=picks)
    for p in picks:
        led["picks"].append(dict(p, day=str(day), market_day=str(market_day), mode=res["mode"], at=now.isoformat()))
    save_ledger(led)
    lines = [f"**{market_day} picks** ({res['mode']}{' — ' + ', '.join(why) if why else ''}) · run at {now:%Y-%m-%d %H:%M} UTC · AIFS init {init:%Y-%m-%d %H}Z"]
    lines += [f"- {p['ticker']} **{p['side'].upper()}** @ ${p['price']:.2f} × {p['contracts']} (max ${p['max_cost']:.2f}) · "
              f"model P={p['p_side']:.2f}, edge {p['edge']:+.3f} · forecast {p['mu']}°F ± {p['sigma']}" for p in picks] or ["- no pick passes the locked rule today"]
    res["issue"] = post_issue("\n".join(lines))
    if is_live:
        live = kalshi or Kalshi(env="prod")
        res["orders"] = []
        for p in picks:
            try:
                res["orders"].append(place(live, led, day, p, total_budget, now))
            except CapError as e:
                res["orders"].append({"ticker": p["ticker"], "skipped": str(e)})
    else:
        res["would_order"] = [dict(ticker=p["ticker"], side=p["side"], type=ORDER_TYPE, count=p["contracts"],
                                   limit_price=p["price"], max_cost=p["max_cost"]) for p in picks]
    return res


def judge_annotate(cands):
    """Ask the decision model about each candidate (only used if RULES picked the judge player)."""
    import tempfile
    import csv
    rows = [dict(ticker=c["ticker"] + ":" + c["side"], date="", split="LIVE", side=c["side"], edge=c["edge"], pnl=0,
                 won="", state=json.dumps({k: c[k] for k in ("city", "station", "side", "mu", "sigma", "p_side",
                                                             "price", "fee", "edge", "yes_sub_title")}))
            for c in cands if c["edge"] > 0]
    if not rows:
        return cands
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    out = Path(f.name).with_suffix(".jsonl")
    subprocess.run([str(ROOT / "model/judge/.venv/bin/python"), "-c",
                    "import sys,json;sys.path.insert(0,'model');import judge;e=judge.load();"
                    f"import csv;o=open('{out}','w');"
                    f"[o.write(json.dumps({{'t':r['ticker'],'p':judge.ask(e,r['state'])['bet']}})+'\\n') for r in csv.DictReader(open('{f.name}'))]"],
                   cwd=ROOT, check=True, capture_output=True)
    p = {json.loads(l)["t"]: json.loads(l)["p"] for l in out.read_text().splitlines()}
    for c in cands:
        c["p_bet"] = p.get(c["ticker"] + ":" + c["side"], 0.0)
    return cands


# ---------------- cancel / settle ----------------
def job_cancel(day, kalshi=None, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    led = load_ledger()
    res = {"day": str(day), "canceled": []}
    resting = [o for o in led["orders"] if o.get("order_id") and o["status"] in ("resting", "sent", "pending")
               and now - dt.datetime.fromisoformat(o["placed_at"]) >= dt.timedelta(hours=CANCEL_AFTER_HOURS)]
    if not resting:
        return res
    from bot.kalshi import Kalshi
    k = kalshi or Kalshi(env="prod")
    for o in resting:
        st = k.get(f"/portfolio/orders/{o['order_id']}").get("order", {})
        filled = float(st.get("fill_count_fp") or 0)
        if st.get("status") == "resting":
            k.request("DELETE", f"/portfolio/events/orders/{o['order_id']}")
        o["filled"] = filled
        o["status"] = "filled" if filled >= o["count"] else ("canceled_unfilled" if filled == 0 else "partial_canceled")
        if filled < o["count"]:
            o["max_cost"] = round(filled * o["price"] + fee(o["price"], int(filled)), 4) if filled else 0.0
        res["canceled"].append({k2: o[k2] for k2 in ("ticker", "status", "filled")})
    save_ledger(led)
    return res


def job_settle(day):
    """Settle picks (paper for DRY_RUN, real for LIVE fills) whose markets have finalized."""
    from bot.kalshi import Kalshi
    k = Kalshi(auth=False)
    led = load_ledger()
    done = 0
    for p in led["picks"]:
        if "result" in p:
            continue
        m = k.get(f"/markets/{p['ticker']}").get("market", {})
        if m.get("status") not in ("finalized", "settled"):
            continue
        won = (m["result"] == "yes") == (p["side"] == "yes")
        n = p["contracts"]
        if p["mode"] == "LIVE":
            o = next((o for o in led["orders"] if o["ticker"] == p["ticker"]), None)
            n = int(o.get("filled", 0)) if o else 0
        p.update(result=m["result"], settled_value=m.get("expiration_value"), won=won, filled=n,
                 pnl=round((n if won else 0) - n * p["price"] - fee(p["price"], n), 4))
        done += 1
    save_ledger(led)
    paper = round(sum(p["pnl"] for p in led["picks"] if "pnl" in p and p["mode"] == "DRY_RUN"), 2)
    live = round(sum(p["pnl"] for p in led["picks"] if "pnl" in p and p["mode"] == "LIVE"), 2)
    return {"settled_now": done, "dry_run_paper_pnl": paper, "live_pnl": live}


def log(job, day, res):
    LOGDIR.mkdir(parents=True, exist_ok=True)
    f = LOGDIR / f"{day}_{job}.json"
    f.write_text(json.dumps(res, indent=1, default=str))
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("job", choices=["forecast", "picks", "cancel", "settle"])
    ap.add_argument("--date", help="run date (UTC), default today")
    a = ap.parse_args()
    day = dt.date.fromisoformat(a.date) if a.date else dt.datetime.now(dt.timezone.utc).date()
    if a.job == "forecast":
        res = job_forecast(day)
    elif a.job == "picks":
        res = {"settle": job_settle(day), **job_picks(day)}
    elif a.job == "cancel":
        res = job_cancel(day)
    else:
        res = job_settle(day)
    f = log(a.job, day, res)
    print(json.dumps({k: v for k, v in res.items() if k != "highs"}, indent=1, default=str)[:3000])
    print("log:", f.relative_to(ROOT))


if __name__ == "__main__":
    main()
