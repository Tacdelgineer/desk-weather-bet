# RULES.md — the locked live test (REAL MONEY · $10 TEST)

Written before any real-money order. Committed, tagged `rules-locked`, and its SHA-256 posted as the first comment
of the public "Live picks log" issue, so nothing below can be changed after the fact without it showing.

## Who plays
**corrected AIFS + one-line rule.** Chosen because no player made money on TEST (best was aifs_cor_judge at $-93.15), so per PLAN.md the live player is corrected AIFS + one-line rule.

TEST-window results (PAPER MONEY, 2026-08-22 → 2026-10-20), P&L per player:
- gfs: $-167.40
- aifs_raw: $-130.65
- aifs_cor: $-129.11
- aifs_cor_judge: $-93.15

## The rule
- Forecast: AIFS Single v2 run on this desk computer (DGX Spark) from that day's 00Z ECMWF open data — the same
  pipeline as the backtest; station high = max of
  the 6-hourly 2 m temperatures in the station's local-standard-time day, corrected per station with the TRAIN fit
  (results/corrections.json, copied into RULES.json); spread = that station's TRAIN error spread.
- Each morning at 16:00 UTC the bot looks at the **next day's** markets for the 6 cities (Los Angeles, NYC, Miami,
  Chicago Midway, Phoenix, San Francisco) — the earliest market for each date, never same-day.
- Buy YES or NO at the current ask only if model probability − price − fee per contract > **0.09**
  (threshold tuned on TRAIN).
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
