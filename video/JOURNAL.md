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

---

## 2026-10-24 — v2 backtest: the judge flips to +$2.94, and the guards remove most of the loss

**What happened.** Same TRAIN/TEST split, re-run with the v2 correction and guards (PAPER MONEY, TEST):

| player | v1 TEST P&L (bets) | v2 TEST P&L (bets) | source |
|---|---|---|---|
| free GFS forecast | −$167.40 (410) | −$66.03 (193) | results/v1_vs_v2.csv |
| raw AIFS | −$130.65 (254) | −$12.41 (19) | same |
| corrected AIFS + rule | −$129.11 (687) | −$106.46 (379) | same |
| corrected AIFS + judge | −$93.15 (1,176) | **+$2.94** (310) | same |

- The judge's +$2.94 comes on $261.06 staked: a return of +1.1%, 83.5% of bets won, cut-off P(bet) > 0.77 tuned on
  TRAIN (results/judge.json). By city: Chicago +$3.62, NYC +$3.08, LA +$2.18, SF +$1.26, Phoenix −$2.83,
  Miami −$4.37 (same file).
- The guards skipped bets that would have lost a lot. For corrected AIFS + rule they skipped 272 bets worth −$71.64
  (227 for the GFS gap, 45 for the edge cap). For GFS they skipped 217 bets worth −$101.37, all on the edge cap.
  Source: results/v1_vs_v2.json, `guard_skips_test`.
- Error and accuracy: the v2 correction's TEST error is 1.928 °F, against 2.133 °F for v1 (results/corrections.json).
  Its Brier score is 0.122, against 0.130 for v1. The market's price is still better at 0.105 (results/v1_vs_v2.json).
- Under PLAN.md's pre-written rule ("pick the best player on TEST"), the judge becomes the live player in RULES.md v2.
  **Caveat:** v2 was designed after seeing TEST, so this +$2.94 isn't an unseen result. It reads as about break-even.
- A second, smaller bug turned up while wiring the judge for live. v1's live.py would have sent the judge different
  input fields than the backtest did (`mu`, `p_side`… instead of `forecast_high_F`, `model_probability_side_wins`…).
  Now both build the input with `backtest.judge_inputs.judge_state`, and a test (tests/test_guards.py) checks the
  fields match. It never ran live, because v1's live player was the rule.

**On screen:** the v1 → v2 P&L bars side by side on a PAPER MONEY board, the judge's bar crossing zero by a hair, with
a "designed after seeing TEST" stamp across it.

---

## 2026-10-25 — v2 dry run (market day 2026-10-25) next to the v1 dry run

By hand, `bot/live.py picks --date 2026-10-24`, run 2026-10-25 04:43 UTC (after the nominal 16:00 UTC bet time,
like the v1 run), DRY_RUN (no GO_LIVE), rules v2, player corrected AIFS + judge. Source:
logs/live/2026-10-24_picks.json; v1: results/evidence/v1-bug/2026-10-23_picks.json.

| | v1 picks (market day 10-24) | v2 picks (market day 10-25) |
|---|---|---|
| pick 1 | Phoenix "83° or above" **YES @ $0.06**, edge 0.8453 | LA "76° to 77°" **NO @ $0.67**, edge 0.1634, judge P(bet) 0.7997 |
| pick 2 | Miami "88° or above" **YES @ $0.01**, edge 0.7097 | Miami "83° to 84°" **NO @ $0.74**, edge 0.0988, judge P(bet) 0.7939 |
| corrected high vs GFS | Phoenix 85.49 vs 77.3 (+8.19 °F), Miami 88.26 vs 84.1 (+4.16 °F) | LA 79.35 vs 75.7 (+3.65 °F), Miami 80.87 vs 84.1 (−3.23 °F) |
| skipped by guards | — (no guards) | 8 of 28 candidates over the threshold: 6 for Chicago (corrected 73.85 vs GFS 69.6, 4.25 °F apart) and 2 for edges above 0.30 (LA 0.3526, Phoenix 0.4635) |

- CHECK passes for the picks: no pick is more than 4 °F from GFS, and no pick has an edge above 0.30. One station's
  corrected high (Chicago) was more than 4 °F from GFS, so all its candidates were skipped. That's the guard working.
- On the same raw highs, the v1 line would have said Phoenix 87.68 °F, 8.38 °F above GFS 79.3. In October it
  still runs hot, which shows the v1 bug wasn't a one-day accident. (results/dryrun_v1_vs_v2.json: v1 coefficients from RULES.json at tag `rules-locked`,
  applied to the raw highs in logs/live/2026-10-24_picks.json.)
- v2 picks cheap-to-moderate favourites (NO at 67–74¢) with edges of 10–16¢, not 1–6¢ long shots with 70–85¢ "edges".
- Still worth watching: two edges above 0.30 got through the correction and were stopped only by the cap. LA's
  30-day spread is wide (sigma 4.38 °F, bias +6.45 °F).

**On screen:** two log cards side by side, v1 (red stamp "BUG") and v2. The Phoenix line on each is highlighted:
85.49 vs 77.3 GFS, then 81.76 vs 79.3 GFS.
