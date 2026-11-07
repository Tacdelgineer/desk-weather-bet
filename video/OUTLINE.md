# OUTLINE.md — "My Desk AI vs the Weather Betting Market" (task 8.1)

One question: can a weather AI running on this DGX Spark beat Kalshi's daily temperature markets after fees?
Numbers come only from `results/` (exported to `video/chapters/data.js` by one script). Looks: riso + papercut for
story, CRT terminal for raw output, EVIDENCE for proof (real document, yellow highlighter, source label, paper).
Labels: backtest scenes `PAPER MONEY`; live scenes `REAL MONEY · $10 TEST`. Target ~9–10 min; betting by ~2:30,
twist ~3:00, end on the payoff.

| NN | Chapter | Must show | Must prove | Files | Look |
|---|---|---|---|---|---|
| 00 | cold open | real GOES-19 loop of MELISSA with AIFS's 3-days-before track drawing on top; the result flashed first | the AI is good at weather — and the question is whether that's worth money | results/hurricanes.json, data/goes/melissa, results/live.json | real footage + riso ink |
| 01 | title | title card after the hook | — | — | riso |
| 02 | desk AI | AIFS running on the DGX: run log, nvidia-smi, model card | it really runs here, ~3 min per 10-day forecast | results/timing.json, logs/1.1_dgx_00z.log | CRT + EVIDENCE |
| 03 | hurricanes | 3 storms (MELISSA, IMELDA, ERIN), each miss in km; ISAIAS run locally | track errors at 24/48/72/120 h and at landfall | results/hurricanes.json, results/isaias_local.json | riso + real loops |
| 04 | the market | how a temperature bracket pays; the NWS climate report that settles it; Kalshi odds in the Weather Channel app | settlement = one station's NWS report | results/cities.json, results/settlement_check.json | EVIDENCE + papercut |
| 05 | the trap | the $67 GFS bots, the afternoon peak, the wrong station | free forecast + city centre = wrong number | results/forecasts.csv, results/corrections.json | riso |
| 06 | the fix | before/after error per station | correction cuts TEST error | results/v2/corrections.json, results/v1_vs_v2.json | riso |
| 07 | backtest | four players' P&L lines racing, fees, the market as forecaster | nobody beats the market price on accuracy; best player about break-even | results/backtest.json, results/judge.json, results/robustness.json | riso, PAPER MONEY |
| 08 | the judge | decision models in 60 s; judge vs one-line rule; 3 real decisions | the judge loses less / scrapes +$2.94, not proof of an edge | results/judge.json, results/judge_examples.json | papercut + CRT |
| 09 | the bug | Phoenix TRAIN scatter with the v1 line extended to the October day; NWS PFM vs bot (EVIDENCE); v1 → v2 tags | a straight line fit on summer broke in autumn; caught in DRY_RUN | results/evidence/v1-bug/, results/v1_vs_v2.json | riso + EVIDENCE + CRT |
| 10 | real money | timestamped picks on the issue, the 4 fills, the result; the crash on day 3 | live week result, and that only 2 of 7 days traded | results/live.json, issue #1 | stat card + recording slot, REAL MONEY · $10 TEST |
| 11 | verdict | what it means, the repo, call to action | the AI forecasts well; the market prices it in | all of the above | riso |

Recording slots (owner): the Kalshi account showing the 4 live orders and fills (ch 10); optional 3 s phone clip of
the DGX on the desk (ch 02).

Style preview (approved look before the full render): `results/preview/style_preview.mp4`, built from
`video/chapters/90_scenes.js`.
