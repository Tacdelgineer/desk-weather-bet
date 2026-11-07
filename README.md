# desk-weather-bet

Can a weather AI running on a desk computer beat Kalshi's daily temperature markets after fees?

Video: "My Desk AI vs the Weather Betting Market". Every number comes from a file in `results/`.

Not financial advice. It's an experiment.

## Results (every number from `results/`)

- **Hurricanes** (`results/hurricanes.json`): AIFS's forecast from 3 days before MELISSA's landfall missed by 50.3 km.
- **Backtest, PAPER MONEY**, TEST window only (`results/backtest.json`, `results/judge.json`): free GFS −$66.03,
  raw AIFS −$12.41, corrected AIFS + rule −$106.46, corrected AIFS + judge +$2.94 on 310 bets.
  The market's own price was the most accurate forecast (Brier 0.1054 vs 0.122 for the best model).
- **The bug** (`results/evidence/v1-bug/`): v1 turned Phoenix's raw 76.31 °F into 85.49 °F; the NWS said
  79 °F. Caught in a dry run; rules v2 locked before any real money.
- **Live week, REAL MONEY · $10 TEST** (`results/live.json`, settled from Kalshi's records): 4 orders, 2 won,
  2 lost, P&L −$0.50. The bot crashed from day 3: 2 of 7 days traded.
- Settlement check: Kalshi's settled high matched the NWS climate report on 718 of 720 station-days.

Rules: RULES.md (tag `rules-locked-v2`). Picks log: issue #1. Credits: CREDITS.md.

Not financial advice. It's an experiment.
