# RULES.md — the locked live test (REAL MONEY · $10 TEST)

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
**corrected AIFS + decision-model judge.** Chosen because it had the best TEST P&L ($+2.94), and PLAN.md's rule (written before any results) is to take the best player on TEST.
That is $+2.94 on $261.06 staked over 310 bets (return +1.1%): about break-even, on a TEST window v2 was designed after seeing. Read it as "not clearly losing", not as proof of an edge.

TEST-window results (PAPER MONEY, 2026-08-22 → 2026-10-20), P&L per player, v2 (v1 in brackets):
- gfs: $-66.03 (v1 $-167.40)
- aifs_raw: $-12.41 (v1 $-130.65)
- aifs_cor: $-106.46 (v1 $-129.11)
- aifs_cor_judge: $+2.94 (v1 $-93.15)

## The rule
- Forecast: AIFS Single v2 run on this desk computer (DGX Spark) from that day's 00Z ECMWF open data — the same
  pipeline as the backtest; station high = max of
  the 6-hourly 2 m temperatures in the station's local-standard-time day, plus that station's average error
  (actual − raw) over the 30 days before the run date; spread = the standard deviation of those
  errors. Fewer than 20 of the 30 days → no picks for that station.
  Actuals = Kalshi's settled values.
- Each morning at 16:00 UTC the bot looks at the **next day's** markets for the 6 cities (Los Angeles, NYC, Miami,
  Chicago Midway, Phoenix, San Francisco) — the earliest market for each date, never same-day.
- Buy YES or NO at the current ask only if model probability − price − fee per contract > **0.00**
  and the decision model (Strands Decider 2B, run here) gives P(bet) > **0.77** (cut-off tuned on TRAIN; it sees the same input fields as in the backtest).
- Skip the pick if the corrected high is more than 4 °F from the GFS forecast for that
  station and day (GFS run of the same morning, 00Z; no GFS value → skip), or if the edge is above 0.30.
- Best edges first, at most 2 picks a day.

## Caps (constants in bot/live.py, each unit-tested)
- Total spend ≤ the number in GO_LIVE, never more than $10.
- At most $1.00 per market, fee included.
- At most 2 new orders per day.
- Limit orders only; anything unfilled is cancelled after 3 hours.
- A `STOP` file in the repo stops all orders.

## Dates
The live week is 7 consecutive daily runs, starting with the first 16:00 UTC run after the user creates `GO_LIVE`.
Until then the bot runs every day in DRY_RUN and posts the picks it *would* make. Day 8: settle everything and
write results/live.json, unfilled orders included.

## Reporting
Every pick is posted to the issue before its market settles. Wins, losses, unfilled orders and bugs all get
reported. Settlement is Kalshi's own settled value. Not financial advice. It's an experiment.
