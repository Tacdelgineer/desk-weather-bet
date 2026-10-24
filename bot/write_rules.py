"""7.1 — write RULES.md (plain English) + RULES.json (what bot/live.py reads) from the TEST results.
Picks the best player on TEST; if nothing made money on TEST, uses corrected AIFS + rule and says so."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backtest.window import END, SPLIT  # noqa: E402
from bot import live  # noqa: E402


def main():
    bt = json.loads((ROOT / "results" / "backtest.json").read_text())
    jd = json.loads((ROOT / "results" / "judge.json").read_text())
    players = {k: v["test"]["pnl"] for k, v in bt["players"].items() if "test" in v}
    players["aifs_cor_judge"] = jd["test"]["judge"]["pnl"]
    best = max(players, key=players.get)
    if players[best] > 0:
        chosen, why = best, f"it had the best TEST P&L (${players[best]:+.2f})"
    else:
        chosen = "aifs_cor"
        why = ("no player made money on TEST (best was " + best + f" at ${players[best]:+.2f}), so per PLAN.md the "
               "live player is corrected AIFS + one-line rule")
    rules = dict(player=chosen, threshold=bt["players"]["aifs_cor"]["threshold_used"],
                 judge_cutoff=jd["judge_cutoff_train"] if chosen == "aifs_cor_judge" else None,
                 test_pnl=players, caps=dict(total_budget_max=live.MAX_BUDGET, per_market=live.MAX_PER_MARKET,
                                             new_orders_per_day=live.MAX_NEW_ORDERS_PER_DAY, order_type=live.ORDER_TYPE,
                                             cancel_unfilled_after_hours=live.CANCEL_AFTER_HOURS))
    corr = json.loads((ROOT / "results" / "corrections.json").read_text())  # frozen into the lock with the rules
    rules["corrections"] = {st: {k: corr[st]["aifs_high"][k] for k in ("a", "b", "sigma")} for st in corr
                            if not st.startswith("_")}
    live.RULES.write_text(json.dumps(rules, indent=1))
    label = {"aifs_cor": "corrected AIFS + one-line rule", "aifs_cor_judge": "corrected AIFS + decision-model judge",
             "gfs": "free GFS forecast", "aifs_raw": "raw AIFS"}[chosen]
    md = f"""# RULES.md — the locked live test (REAL MONEY · $10 TEST)

Written before any real-money order. Committed, tagged `rules-locked`, and its SHA-256 posted as the first comment
of the public "Live picks log" issue, so nothing below can be changed after the fact without it showing.

## Who plays
**{label}.** Chosen because {why}.

TEST-window results (PAPER MONEY, {SPLIT} → {END}), P&L per player:
{chr(10).join(f"- {k}: ${v:+.2f}" for k, v in players.items())}

## The rule
- Forecast: AIFS Single v2 run on this desk computer (DGX Spark) from that day's 00Z ECMWF open data — the same
  pipeline as the backtest; station high = max of
  the 6-hourly 2 m temperatures in the station's local-standard-time day, corrected per station with the TRAIN fit
  (results/corrections.json, copied into RULES.json); spread = that station's TRAIN error spread.
- Each morning at 16:00 UTC the bot looks at the **next day's** markets for the 6 cities (Los Angeles, NYC, Miami,
  Chicago Midway, Phoenix, San Francisco) — the earliest market for each date, never same-day.
- Buy YES or NO at the current ask only if model probability − price − fee per contract > **{rules['threshold']:.2f}**
  (threshold tuned on TRAIN){f" and the decision model's P(bet) > {rules['judge_cutoff']:.2f}" if rules['judge_cutoff'] is not None else ""}.
- Best edges first, at most 2 picks a day.

## Caps (constants in bot/live.py, each unit-tested)
- Total spend ≤ the number in GO_LIVE, never more than ${live.MAX_BUDGET:.0f}.
- At most ${live.MAX_PER_MARKET:.2f} per market, fee included.
- At most {live.MAX_NEW_ORDERS_PER_DAY} new orders per day.
- Limit orders only; anything unfilled is cancelled after {live.CANCEL_AFTER_HOURS} hours.
- A `STOP` file in the repo stops all orders.

## Dates
The live week is 7 consecutive daily runs, starting with the first 16:00 UTC run after the user creates `GO_LIVE`.
Until then the bot runs every day in DRY_RUN and posts the picks it *would* make. Day 8: settle everything and
write results/live.json, unfilled orders included.

## Reporting
Every pick is posted to the issue before its market settles. Wins, losses, unfilled orders and bugs all get
reported. Settlement is Kalshi's own settled value. Not financial advice. It's an experiment.
"""
    (ROOT / "RULES.md").write_text(md)
    print("player:", chosen, "|", why)


if __name__ == "__main__":
    main()
