# JOURNAL.md — surprises, bugs and failures, as they happened

One dated entry per surprise: the numbers, the file each one comes from, and one line on how to show it on screen.

---

## 2026-10-24 — The v1 station correction blew up on the first dry run

**What the DRY_RUN showed.** The by-hand DRY_RUN for market day 2026-10-24 (run 2026-10-24 04:51 UTC, v1 rules,
tag `rules-locked`) picked two long shots with huge "edges":

| pick | price | model P | edge | source |
|---|---|---|---|---|
| KXHIGHTPHX-26OCT24-T82 YES ("83° or above") | $0.06 | 0.9093 | 0.8453 | results/evidence/v1-bug/2026-10-23_picks.json |
| KXHIGHMIA-26OCT24-T87 YES ("88° or above") | $0.01 | 0.7204 | 0.7097 | same |

An edge of 0.70–0.85 at 1–6¢ means the bot thinks the market is wrong by 70–85 cents on the dollar. Real edges
are a few cents. That's a bug, not an edge.

**The numbers** (all from results/evidence/v1-bug/summary.json, built by backtest/v1_bug.py from the files below):

| station | raw AIFS high | v1 corrected | GFS | NWS forecast max | NWS high (prelim.) | TRAIN raw range | v1 fit (a, b) |
|---|---|---|---|---|---|---|---|
| Phoenix KPHX | 76.31 °F | **85.49 °F** | 77.3 °F | 79 °F (4:01 PM MST 10-23 issue; 78 °F at 4:01 AM) | 77 °F | 90.42–116.79 °F | 27.175, 0.7641 |
| Miami KMIA | 82.39 °F | **88.26 °F** | 84.1 °F | 84 °F (both 10-23 issues) | 84 °F | 84.52–95.36 °F | 37.148, 0.6204 |
| NYC KNYC | 61.86 | 64.75 | 61.5 | — | — | 70.03–99.07 | 10.988, 0.8691 |
| Chicago KMDW | 69.28 | 71.07 | 69.8 | — | — | 70.98–94.58 | 2.240, 0.9935 |
| Los Angeles KLAX | 73.08 | 77.64 | 74.6 | — | — | 66.37–78.45 | 12.635, 0.8895 |
| San Francisco KSFO | 68.28 | 72.68 | 72.3 | — | — | 61.43–79.80 | 3.454, 1.0138 |

Sources per column:
- raw and corrected highs, prices, edges: results/evidence/v1-bug/2026-10-23_picks.json;
- fit: RULES.json at tag `rules-locked` (= results/corrections.json, `aifs_high`);
- TRAIN raw range: results/forecasts.csv, TRAIN rows;
- GFS: Open-Meteo, gfs_global run 2026-10-23 00Z;
- NWS forecast: results/evidence/v1-bug/nws_pfm_PSR_2026-10-23.txt and nws_pfm_MFL_2026-10-23.txt;
- NWS high: results/evidence/v1-bug/nws_cli_prelim_*_2026-10-24.json. These are preliminary same-day reports,
  issued before Kalshi settles. On them, both picks lose.

The task note said "85.2 °F" for Phoenix. The file says 85.49 °F = 27.175 + 0.7641 × 76.31.

**Why it happened.** The correction `actual ≈ a + b × raw` was fit on 60 summer TRAIN days (2026-06-23 → 08-21).
Phoenix's TRAIN raw highs were all 90–117 °F, and Miami's were all 85–95 °F. With so little spread, the fitted slope
comes out shallow (b = 0.76 and 0.62) and the intercept large (a = 27 and 37). That works inside the summer range.
At a late-October 76 °F, though, the line is far outside the range it was fit on. It adds 9.2 °F in Phoenix and
5.9 °F in Miami. The station error spread (sigma 2.23 / 1.30 °F) was also fit in summer, so the bot was sure of
a number nobody else forecast. 4 of the 6 stations were outside their TRAIN range that day.

**On screen:** Phoenix's 60 TRAIN dots bunched at 90–117 °F, the fitted line drawn on past them down to 76 °F,
landing at 85.5 °F, next to the NWS sheet with "79" highlighted.

---

## 2026-10-24 — The v1 backtest: no player made money on TEST

**What happened.** Every player lost on the 60 TEST days (2026-08-22 → 2026-10-20), PAPER MONEY:

| player | TEST P&L | bets | win rate | threshold (TRAIN) | TRAIN P&L | source |
|---|---|---|---|---|---|---|
| free GFS forecast | −$167.40 | 410 | 0.273 | 0.22 | −$13.37 | results/v1/backtest_summary.csv |
| raw AIFS | −$130.65 | 254 | 0.201 | 0.30 | +$10.55 | same |
| corrected AIFS + rule | −$129.11 | 687 | 0.399 | 0.09 | +$121.36 | same |
| corrected AIFS + judge | −$93.15 | 1,176 | 0.615 | P(bet) > 0.62 | — | results/v1/judge.json |

- The market's own prices were the best forecast: Brier score 0.105 vs 0.130–0.150 for every model
  (results/v1/backtest.json, `accuracy_brier_test`).
- No player turned a profit with fees ×1.5 or with the threshold moved up or down (results/v1/robustness.json).
- The corrected player made +$121.36 on TRAIN and −$129.11 on TEST. The same summer-only fit was carried into
  autumn, which, looking back, was the first sign of the bug above.

**On screen:** four equity curves on a PAPER MONEY board, all ending below zero, with the market's Brier bar
standing above the models.
