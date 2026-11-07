"""Day 8 (task 7.6): build results/live.json from Kalshi's own records (data/live_kalshi/, pulled read-only by
tools/kalshi_records.py) plus the bot's ledger and the systemd run history. Safe to re-run."""
import json, subprocess
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
K = ROOT / "data" / "live_kalshi"
orders = json.load(open(K / "orders.json"))
fills = json.load(open(K / "fills.json"))
setts = {s["ticker"]: s for s in json.load(open(K / "settlements.json"))}
ledger = json.load(open(ROOT / "results" / "live_ledger.json"))
picks = {p["ticker"]: p for p in ledger["picks"]}

# GO_LIVE created 2026-10-25 19:50 UTC -> first 16:00 UTC run after it is 2026-10-26; 7 consecutive daily runs.
first = date(2026, 10, 26)
window = [(first + timedelta(d)).isoformat() for d in range(7)]

# per-run outcome from the systemd journal (picks job, 16:00 UTC)
j = subprocess.run(["journalctl", "--user", "-u", "dwb-picks.service", "--since", "2026-10-25", "--no-pager",
                    "-o", "short-iso"], capture_output=True, text=True).stdout
runs = {}
for line in j.splitlines():
    d = line[:10]
    if "Finished dwb-picks" in line:
        runs[d] = "ok"
    elif "Failed with result" in line:
        runs[d] = "crashed"

rows = []
for o in sorted(orders, key=lambda o: o["created_time"]):
    t = o["ticker"]
    s = setts.get(t)
    f = [x for x in fills if x["order_id"] == o["order_id"]]
    n = float(o["fill_count_fp"])
    cost = float(o["taker_fill_cost_dollars"]) + float(o["maker_fill_cost_dollars"])
    fee = float(o["taker_fees_dollars"]) + float(o["maker_fees_dollars"])
    held = "no" if f and f[0]["side"] == "no" else "yes"   # Kalshi lists a NO buy as side=yes action=sell
    rev = (s["revenue"] / 100) if s else None
    placed = o["created_time"][:10]
    rows.append(dict(
        placed_utc=o["created_time"], run_day=placed, market=t, market_day=picks.get(t, {}).get("market_day"),
        city=picks.get(t, {}).get("city"), bracket=picks.get(t, {}).get("yes_sub_title"), side_held=held,
        limit_price=float(o[f"{held}_price_dollars"]), contracts=float(o["initial_count_fp"]), filled=n,
        status=o["status"], fill_cost=round(cost, 4), fee=round(fee, 6),
        market_result=s["market_result"] if s else None, settled_value=picks.get(t, {}).get("settled_value"),
        revenue=rev, pnl=round(rev - cost - fee, 4) if s else None, won=(s["market_result"] == held) if s else None,
        in_window=placed in window, bot_ledger_pnl=picks.get(t, {}).get("pnl")))

settled = [r for r in rows if r["pnl"] is not None]
out = {
    "label": "REAL MONEY · $10 TEST",
    "source": "Kalshi /portfolio/orders, /portfolio/fills, /portfolio/settlements (read-only, pulled 2026-11-07 UTC)",
    "rules": "rules-locked-v2",
    "window_runs": window,
    "budget": 10.0,
    "runs": [{"day": d, "picks_job": runs.get(d, "no record"),
              "real_orders": sum(r["run_day"] == d for r in rows)} for d in window],
    "runs_after_window": [{"day": d, "picks_job": v} for d, v in sorted(runs.items()) if d > window[-1]],
    "orders": rows,
    "totals": {
        "orders": len(rows), "filled": sum(r["filled"] > 0 for r in rows),
        "unfilled": sum(r["filled"] == 0 for r in rows), "settled": len(settled),
        "won": sum(bool(r["won"]) for r in settled), "lost": sum(r["won"] is False for r in settled),
        "staked": round(sum(r["fill_cost"] for r in rows), 4), "fees": round(sum(r["fee"] for r in rows), 4),
        "revenue": round(sum(r["revenue"] or 0 for r in rows), 4),
        "pnl": round(sum(r["pnl"] for r in settled), 4),
        "orders_outside_window": sum(not r["in_window"] for r in rows),
        "runs_completed": sum(runs.get(d) == "ok" for d in window),
        "runs_crashed": sum(runs.get(d) == "crashed" for d in window),
    },
    "crash": "picks job crashed every day from 2026-10-28: live.py settled_high() did float(expiration_value) and "
             "Kalshi returned a bracket string ('70° to 71°') for a history day; no picks, no orders on those days",
    "dry_run_picks_before_go_live": [{k: p.get(k) for k in ("ticker", "side", "price", "market_day", "won", "pnl")}
                                     for p in ledger["picks"] if p["mode"] == "DRY_RUN"],
    "note": "Bot ledger fees were rounded up to whole cents; P&L here uses Kalshi's own fee and revenue records.",
}
(ROOT / "results" / "live.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
print(json.dumps(out["totals"], indent=1)); print(out["runs"]); print(out["runs_after_window"])
for r in rows: print(r["run_day"], r["market"], r["side_held"], r["limit_price"], r["status"], r["market_result"], r["pnl"])
