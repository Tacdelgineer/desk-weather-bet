"""Live bot — the ONLY code allowed to place orders (see CLAUDE.md "Money and safety rules").

Daily jobs (UTC):
  forecast  ~08:30  run AIFS locally from today's 00Z ECMWF open data, lead 60 h  -> data/aifs_runs/
  picks     ~16:00  settle older picks, read live asks for tomorrow's markets, choose picks with the locked rule,
                    post them to the "Live picks log" issue, and place limit orders ONLY if every gate is open
  cancel    ~19:05  cancel any of today's orders still resting (unfilled after 3 h)

Default is DRY_RUN: without GO_LIVE (or with STOP, or without the current lock tag RULES_TAG) it logs exactly what it
would have ordered and orders nothing.

v2 (RULES.md at tag rules-locked-v2): station correction = rolling 30-day bias from past data only, plus two guards
(corrected high within 4 °F of GFS, edge ≤ 0.30) — backtest/rolling.py, shared with the backtest. v1 (tag
rules-locked) used a TRAIN-fit line that extrapolated badly in October (video/JOURNAL.md 2026-10-24).

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
from backtest.judge_inputs import judge_state  # noqa: E402
from backtest.rolling import guard, rolling_correction, window  # noqa: E402
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
RULES_TAG = "rules-locked-v2"  # current lock; rules-locked = v1, superseded (kept)
HISTORY = ROOT / "results" / "live_history.csv"  # station-days after the backtest window: settled high + raw AIFS


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
    """RULES.md committed, tagged RULES_TAG, and unchanged since the tag."""
    try:
        subprocess.run(["git", "rev-parse", "-q", "--verify", f"refs/tags/{RULES_TAG}"], cwd=ROOT, check=True,
                       capture_output=True)
        for f in ("RULES.md", "RULES.json"):
            subprocess.run(["git", "diff", "--quiet", RULES_TAG, "--", f], cwd=ROOT, check=True)
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
        why.append(f"RULES.md not committed+tagged {RULES_TAG} (or changed since)")
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


# ---------------- correction history + GFS ----------------
def settled_high(kalshi, series, d):
    """Kalshi's settled high for one station-day (any finalized market in the event), or None."""
    for m in kalshi.get("/markets", event_ticker=event_ticker(series, d), limit=100).get("markets", []):
        if m.get("status") in ("finalized", "settled") and m.get("expiration_value") not in (None, ""):
            return float(m["expiration_value"])
    return None


def station_history(run_date, kalshi):
    """{station: [(date, settled high, raw AIFS high), ...]} for the 30 days before run_date. Backtest days come from
    results/forecasts.csv; later days from results/live_history.csv, filled in from our own AIFS runs and Kalshi's
    settled values (cached once both are known)."""
    import pandas as pd
    a, b = window(run_date)
    days = [a + dt.timedelta(days=i) for i in range((b - a).days + 1)]
    cities = json.loads((ROOT / "results" / "cities.json").read_text())
    fc = pd.read_csv(ROOT / "results" / "forecasts.csv")
    known = {(r.station, r.date): (r.actual, r.aifs_raw_mu) for r in fc.itertuples()}
    cache = {}
    if HISTORY.exists():
        cache = {(r.station, r.date): (r.actual, r.raw) for r in pd.read_csv(HISTORY).itertuples()}
    out = {c["station"]: [] for c in cities}
    for d in days:
        need = [c for c in cities if (c["station"], str(d)) not in known and (c["station"], str(d)) not in cache]
        init = dt.datetime(d.year, d.month, d.day) - dt.timedelta(days=1)
        highs = station_highs(init, d) if need and forecast_path(init).exists() else {}
        for c in need:
            raw = highs.get(c["station"], {}).get("raw_high_F")
            act = settled_high(kalshi, c["series"], d)
            if raw is not None and act is not None:
                cache[(c["station"], str(d))] = (act, raw)
        for c in cities:
            v = known.get((c["station"], str(d))) or cache.get((c["station"], str(d)))
            if v:
                out[c["station"]].append((d, *v))
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text("station,date,actual,raw\n" + "".join(f"{k[0]},{k[1]},{v[0]},{v[1]}\n"
                                                             for k, v in sorted(cache.items())))
    return out


def gfs_highs(market_day):
    """GFS high per station for market_day, from the run of the day before at 00Z (same as the backtest baseline)."""
    from fetch.gfs import day_max, run_series
    out = {}
    run = dt.datetime(market_day.year, market_day.month, market_day.day) - dt.timedelta(days=1)
    for c in json.loads((ROOT / "results" / "cities.json").read_text()):
        try:
            out[c["station"]] = day_max(run_series(c, run), market_day, c["tz"])[0]
        except Exception:  # noqa: BLE001 — a missing GFS value makes guard (a) skip that station's picks
            out[c["station"]] = None
    return out


# ---------------- picks ----------------
MON = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()


def event_ticker(series, d):
    return f"{series}-{d:%y}{MON[d.month - 1]}{d:%d}"


def choose(cands, rules):
    """Locked rule: candidates with edge > threshold (and judge P(bet) > cut-off if the judge player is live) that
    pass both guards (backtest/rolling.guard), best edge first, one per market, at most MAX_NEW_ORDERS_PER_DAY."""
    ok = [c for c in cands if c["edge"] > rules["threshold"] and not guard(c["mu"], c.get("gfs_F"), c["edge"])]
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


def corrections_for(run_date, kalshi):
    """{station: dict(bias, sigma, n) or None} — v2 rolling correction, past data only."""
    return {st: rolling_correction(h, run_date) for st, h in station_history(run_date, kalshi).items()}


def candidates_for(market_day, highs, corr, gfs, kalshi):
    out = []
    for st, h in highs.items():
        c = corr.get(st)
        if c is None:
            continue  # fewer than MIN_DAYS of the 30 days: skip this station
        mu, sigma = h["raw_high_F"] + c["bias"], c["sigma"]
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
                e = pw - price - f / n
                edge = round(e, 4)
                state = judge_state(h["city"], st, m["strike_type"], m.get("floor_strike"), m.get("cap_strike"),
                                    str(market_day), side, mu, sigma, pw, price, f / n, e, -c["bias"], c["n"], ya - yb,
                                    float(m.get("volume_fp") or 0))
                out.append(dict(ticker=m["ticker"], city=h["city"], station=st, side=side, price=price, contracts=n,
                                fee=f, max_cost=round(n * price + f, 4), p_side=round(pw, 4), edge=edge,
                                mu=round(mu, 2), sigma=round(sigma, 2), raw_high_F=h["raw_high_F"],
                                bias_30d=round(c["bias"], 2), days_30d=c["n"], gfs_F=gfs.get(st),
                                guard=guard(mu, gfs.get(st), edge), yes_sub_title=m.get("yes_sub_title"),
                                judge_state=json.dumps(state)))
    return out


REPO = "Tacdelgineer/desk-weather-bet"
ISSUE_FILE = ROOT / "LIVE_ISSUE"   # issue number of the "Live picks log"; kept outside RULES.* so adding it can't break the lock
POST_AS = "Tacdelgineer"            # only the channel account posts (never a personal account; CLAUDE.md: no usernames)


def post_issue(text):
    issue = ISSUE_FILE.read_text().strip() if ISSUE_FILE.exists() else ""
    if not issue:
        return "no issue configured (LIVE_ISSUE missing)"
    who = subprocess.run(["gh", "api", "user", "--jq", ".login"], capture_output=True, text=True).stdout.strip()
    if who != POST_AS:
        return f"not posted: gh is not logged in as {POST_AS}"
    r = subprocess.run(["gh", "issue", "comment", issue, "--repo", REPO, "--body", text], cwd=ROOT,
                       capture_output=True, text=True)
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
    rules = json.loads(RULES.read_text())
    is_live, why = live_mode()
    total_budget = budget() if is_live else 0.0
    led = load_ledger()
    res = {"day": str(day), "market_day": str(market_day), "mode": "LIVE" if is_live else "DRY_RUN",
           "dry_run_reasons": why, "rules": rules.get("version", "v1"), "player": rules.get("player"),
           "threshold": rules["threshold"]}
    init = dt.datetime(day.year, day.month, day.day, 0)
    if not forecast_path(init).exists():
        res["picks"] = []
        res["note"] = "no AIFS forecast for today — no picks"
        return res
    public = Kalshi(auth=False)
    highs = station_highs(init, market_day)
    corr = corrections_for(day, public)
    gfs = gfs_highs(market_day)
    for st, h in highs.items():
        c = corr.get(st)
        h.update(gfs_F=gfs.get(st), bias_30d=round(c["bias"], 2) if c else None, sigma_30d=round(c["sigma"], 2) if c
                 else None, days_30d=c["n"] if c else 0, mu=round(h["raw_high_F"] + c["bias"], 2) if c else None)
    cands = candidates_for(market_day, highs, corr, gfs, public)
    if rules.get("judge_cutoff") is not None:
        cands = judge_annotate(cands)
    picks = choose(cands, rules)
    over = [c for c in cands if c["edge"] > rules["threshold"]]
    res.update(highs=highs, n_candidates=len(cands), n_over_threshold=len(over),
               guarded=[dict({k: c.get(k) for k in ("ticker", "side", "price", "edge", "mu", "gfs_F")}, guard=guard(c["mu"], c.get("gfs_F"), c["edge"]))
                        for c in over if guard(c["mu"], c.get("gfs_F"), c["edge"])], picks=picks)
    for p in picks:
        led["picks"].append(dict(p, day=str(day), market_day=str(market_day), mode=res["mode"], at=now.isoformat(),
                                 rules=res["rules"]))
    save_ledger(led)
    lines = [f"**{market_day} picks** ({res['mode']}{' — ' + ', '.join(why) if why else ''}) · rules {res['rules']} · run at {now:%Y-%m-%d %H:%M} UTC · AIFS init {init:%Y-%m-%d %H}Z"]
    lines += [f"- {p['ticker']} **{p['side'].upper()}** @ ${p['price']:.2f} × {p['contracts']} (max ${p['max_cost']:.2f}) · "
              f"model P={p['p_side']:.2f}, edge {p['edge']:+.3f}" + (f", judge P(bet)={p['p_bet']:.2f}" if "p_bet" in p else "") + f" · forecast {p['mu']}°F ± {p['sigma']} (GFS {p['gfs_F']}°F)" for p in picks] or ["- no pick passes the locked rule today"]
    if res["guarded"]:
        lines.append(f"- {len(res['guarded'])} candidate(s) over the threshold skipped by the guards (GFS gap > 4 °F or edge > 0.30)")
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
    """Ask the decision model about each candidate (only used if RULES picked the judge player). The input JSON is
    built by backtest.judge_inputs.judge_state, the same function the backtest used."""
    import tempfile
    import csv
    rows = [dict(ticker=c["ticker"] + ":" + c["side"], date="", split="LIVE", side=c["side"], edge=c["edge"], pnl=0,
                 won="", state=c["judge_state"]) for c in cands if c["edge"] > 0 and not c["guard"]]
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
