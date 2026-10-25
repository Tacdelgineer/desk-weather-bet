"""7.1 — write RULES.md (plain English) + RULES.json (what bot/live.py reads) from the TEST results.
Picks the best player on TEST; if nothing made money on TEST, uses corrected AIFS + rule and says so.
v2 (tag rules-locked-v2): rolling 30-day correction + guards; v1 (tag rules-locked) is superseded."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backtest.window import END, SPLIT  # noqa: E402
from bot import live  # noqa: E402
from backtest import rolling  # noqa: E402


def main():
    bt = json.loads((ROOT / "results" / "backtest.json").read_text())
    jd = json.loads((ROOT / "results" / "judge.json").read_text())
    players = {k: v["test"]["pnl"] for k, v in bt["players"].items() if "test" in v}
    players["aifs_cor_judge"] = jd["test"]["judge"]["pnl"]
    best = max(players, key=players.get)
    if players[best] > 0:
        chosen, why = best, f"it had the best TEST P&L (${players[best]:+.2f}), and PLAN.md's rule (written before any results) is to take the best player on TEST"
    else:
        chosen = "aifs_cor"
        why = ("no player made money on TEST (best was " + best + f" at ${players[best]:+.2f}), so per PLAN.md the "
               "live player is corrected AIFS + one-line rule")
    # the judge player bets on candidates with edge > 0 and P(bet) > cut-off (backtest/judge_eval.py)
    rules = dict(player=chosen, threshold=0.0 if chosen == "aifs_cor_judge" else bt["players"]["aifs_cor"]["threshold_used"],
                 judge_cutoff=jd["judge_cutoff_train"] if chosen == "aifs_cor_judge" else None,
                 test_pnl=players, caps=dict(total_budget_max=live.MAX_BUDGET, per_market=live.MAX_PER_MARKET,
                                             new_orders_per_day=live.MAX_NEW_ORDERS_PER_DAY, order_type=live.ORDER_TYPE,
                                             cancel_unfilled_after_hours=live.CANCEL_AFTER_HOURS))
    rules = dict(version="v2", **rules)
    rules["correction"] = dict(method="rolling bias: raw AIFS + mean(actual - raw) over the 30 days before the run date",
                               window_days=rolling.WINDOW_DAYS, min_days=rolling.MIN_DAYS)
    rules["guards"] = dict(max_gap_vs_gfs_F=rolling.GFS_MAX_GAP_F, max_edge=rolling.MAX_EDGE)
    v1 = json.loads((ROOT / "results" / "v1_vs_v2.json").read_text())["v1"]["players"]
    live.RULES.write_text(json.dumps(rules, indent=1))
    label = {"aifs_cor": "corrected AIFS + one-line rule", "aifs_cor_judge": "corrected AIFS + decision-model judge",
             "gfs": "free GFS forecast", "aifs_raw": "raw AIFS"}[chosen]
    judge_note = ""
    if chosen == "aifs_cor_judge":
        t = jd["test"]["judge"]
        judge_note = (f"That is ${t['pnl']:+.2f} on ${t['staked']:.2f} staked over {t['bets']} bets (return {t['roi']:+.1%}): "
                      "about break-even, on a TEST window v2 was designed after seeing. Read it as \"not clearly losing\", "
                      "not as proof of an edge.\n")
    md = f"""# RULES.md — the locked live test (REAL MONEY · $10 TEST)

**Version 2.** Written before any real-money order. Committed, tagged `rules-locked-v2`, and its SHA-256 posted in the
first comment of the public "Live picks log" issue, so nothing below can be changed after the fact without it showing.
Version 1 (tag `rules-locked`) is superseded: its dry run found a bug (see below and video/JOURNAL.md).

## What changed and why (v1 → v2)
- **The bug.** v1 corrected each station with a straight line fit on summer TRAIN days (actual ≈ a + b × raw AIFS).
  On the first dry run (market day 2026-10-24) Phoenix's raw 76.31 °F became 85.49 °F, while GFS said 77.3 °F and
  the NWS 79 °F. Phoenix's summer raw highs were all 90–117 °F, so the line was used far outside the range it was fit on.
  Miami (fit a = 37.1, b = 0.62) went 82.39 → 88.26 °F. The bot then saw "edges" of 0.70–0.85 on 1–6¢ long shots.
  Numbers: results/evidence/v1-bug/summary.json.
- **New correction.** Each station's bias is the average of (actual − raw AIFS) over the 30 days before the run date,
  and its spread is the standard deviation of the same 30 days. Past data only. A station with fewer than 20 of the
  30 days gets no forecast that day. Nothing is fitted, so there's no line to stretch when the season changes.
- **Two guards.** Skip any pick whose corrected high is more than 4 °F from the GFS forecast, and any pick with an
  edge above 0.30.
- **Caveat.** v2 was designed after seeing v1's TEST results, so the v2 TEST numbers below aren't an unseen test.
  The live week is the only truly unseen test.

## Who plays
**{label}.** Chosen because {why}.
{judge_note}
TEST-window results (PAPER MONEY, {SPLIT} → {END}), P&L per player, v2 (v1 in brackets):
{chr(10).join(f"- {k}: ${v:+.2f} (v1 ${v1[k]['pnl']:+.2f})" for k, v in players.items())}

## The rule
- Forecast: AIFS Single v2 run on this desk computer (DGX Spark) from that day's 00Z ECMWF open data — the same
  pipeline as the backtest; station high = max of
  the 6-hourly 2 m temperatures in the station's local-standard-time day, plus that station's average error
  (actual − raw) over the {rolling.WINDOW_DAYS} days before the run date; spread = the standard deviation of those
  errors. Fewer than {rolling.MIN_DAYS} of the {rolling.WINDOW_DAYS} days → no picks for that station.
  Actuals = Kalshi's settled values.
- Each morning at 16:00 UTC the bot looks at the **next day's** markets for the 6 cities (Los Angeles, NYC, Miami,
  Chicago Midway, Phoenix, San Francisco) — the earliest market for each date, never same-day.
- Buy YES or NO at the current ask only if model probability − price − fee per contract > **{rules['threshold']:.2f}**
  {f"and the decision model (Strands Decider 2B, run here) gives P(bet) > **{rules['judge_cutoff']:.2f}** (cut-off tuned on TRAIN; it sees the same input fields as in the backtest)" if rules['judge_cutoff'] is not None else "(threshold tuned on TRAIN)"}.
- Skip the pick if the corrected high is more than {rolling.GFS_MAX_GAP_F:g} °F from the GFS forecast for that
  station and day (GFS run of the same morning, 00Z; no GFS value → skip), or if the edge is above {rolling.MAX_EDGE:.2f}.
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
