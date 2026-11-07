# STATE.md — running log (newest at the bottom)


**2026-10-23 — 0.1** ([x])
- Repo skeleton created and pushed; .pem and GO_LIVE confirmed ignored by git check-ignore.
- Next: 0.2 environment.

**2026-10-23 — 0.2** (⚠️)
- uv env created (Python 3.12; numpy/pandas/scipy/requests/cryptography/pytest).
- CPU: 12th Gen Intel i9-12900HK (x86_64, 20 threads), RAM 15 GB, free disk 386 GB (>200 GB OK).
- nvidia-smi: command not found — this machine has no NVIDIA GPU (not the DGX Spark). CHECK can't pass here; continuing on CPU (see DECISIONS.md).
- Next: 0.3 (print H1), then 1.1.

**2026-10-23 — 0.3** (⏸)
- H1 printed. Status: Kalshi prod key works (read-only balance call OK); account has ≥ $10; git push works.
- Still needed from the user: ElevenLabs key + voice ID in the environment (not found). Demo key optional (none found).
- Next: 1.1.

**2026-10-24 — 3.1** ([x])
- results/cities.json: 6 cities by 30-day volume → station (from market rules) → series, with station lat/lon from api.weather.gov.
- Settlement source in rules is The Weather Company for the NWS climate station (logged in DECISIONS.md).

**2026-10-24 — 3.4** ([x])
- backtest/fees.py implements Kalshi's taker fee round_up(0.07·C·P·(1−P)); tests/test_fees.py checks the doc's worked examples (5¢×100 → $0.34; 50¢ → $0.02 / $1.75 per 100) plus the table rows. 3 tests pass.
- Next: 1.1 (AIFS CPU test run in progress).

**2026-10-24 — 2.1** ([x])
- results/storms.json: MELISSA (Jamaica landfall 2025-10-28 17:25Z), IMELDA (Bermuda 11 km, 2025-10-02 03Z), ERIN (Outer Banks closest approach 322 km, 2025-08-21 09Z), from IBTrACS NA v04r01. Choice logged in DECISIONS.md.

**2026-10-24 — 4.2** ([x])
- results/gfs_highs.csv: GFS (Open-Meteo single-run API, gfs_global) run D-1 00Z, hourly 2 m temp at station, max over the local-standard-time day; 720 rows.
- Hand check LA 2026-06-25: 24 hourly values, max 71.5°F at 19Z = csv value (Kalshi settled 72).

**2026-10-24 — 3.2** ([x])
- results/markets.csv: 4,320 bracket markets (720 events = 6 cities × 120 dates), settled values, ask/bid at bet time (16:00 UTC day before) from hourly candles; raw cache in data/kalshi/.
- Kalshi markets usually open 14:00 UTC the day before (median 2 h before bet time); 7 events (42 markets) opened after bet time → no quote, excluded.
- CHECK: KXHIGHLAX-26JUN25-B72.5 ours ask 0.30/bid 0.29 = Kalshi candle 0.30/0.29; KXHIGHNY-26OCT15-B68.5 0.04/0.03 = 0.04/0.03.

**2026-10-24 — 3.3** ([x])
- NWS Daily Climate Report highs (IEM archive) vs Kalshi settled values: 718/720 match (99.72%). Mismatches: Miami 2026-08-29 (Kalshi 90, NWS 85), Phoenix 2026-09-27 (NWS value missing 'M'). results/settlement_check.json, results/nws_cli.csv.
- Backtest settles on Kalshi's own value (what actually paid out).

**2026-10-24 — 4.3** ([x])
- backtest/correct.py: per station actual ≈ a + b·model fitted on TRAIN only (assert_train_only; tests/test_split.py proves fit() raises on TEST dates). results/corrections.json + results/forecasts.csv.
- TEST MAE °F: GFS 3.28, raw AIFS 3.25, corrected AIFS 2.42 (TRAIN 3.83 / 2.89 / 1.58). Correction hurts LA (3.22→4.08) and NYC (1.24→1.90) on TEST — reported, not hidden.

**2026-10-24 — 5.1** ([x])
- backtest/sim.py bracket_prob(): Normal(mu, sigma) around each player's high with ±0.5°F integer continuity (between / greater / less brackets). Sigma = station's TRAIN error spread.

**2026-10-24 — 5.2** ([x])
- Same rule for all players: buy YES/NO at the ask if p − price − fee/contract > threshold, ≤ $1 incl. fee per market, threshold tuned on TRAIN (grid 0–0.30), reported on TEST. Assumes full fill at the quoted ask.
- CHECK: logs/handcheck.md traces 5 random bets end to end, recomputed independently from raw files — all match.

**2026-10-24 — 5.3** ([x])
- results/backtest.json, backtest_summary.csv, backtest_bets.csv, candidates.csv (PAPER MONEY, TEST window).
- TEST P&L: GFS −$167.40 (410 bets), raw AIFS −$150.50 (261), corrected AIFS + rule −$284.14 (1,148; TRAIN was +$127). Market mid-price Brier 0.105 beats every model (0.136–0.150).
- CHECK: per-bet P&L sums equal totals (asserted in sim.py).

**2026-10-24 — 5.4** ([x])
- results/robustness.csv/.json: fees ×1.5 and TRAIN threshold shifted −0.02/+0.02/+0.05. No player is profitable on TEST in any case (best: GFS/raw AIFS ≈ −$126 at +0.05). Conclusion holds.

**2026-10-24 — 1.3** ([x])
- Measured on this CPU: ~528 s per 6-h AIFS step (step 1 incl. model load 498 s), input download 168 s. results/timing.json.
- Estimates if run locally: backtest 120×10 steps ≈ 176 h, hurricanes 9×24 ≈ 32 h, live week ≈ 10 h, one 10-day forecast ≈ 5.9 h. Total > 24 h → backtest + hurricanes use ECMWF's archived real-time AIFS (same v2 weights for the backtest); live runs locally. Logged in DECISIONS.md.

**2026-10-24 — 4.1** ([x])
- results/aifs_highs.csv: 720 station-days; D-1 00Z AIFS run (ECMWF archived real-time AIFS Single v2, see DECISIONS.md), nearest 0.25° grid point, max of the 4 six-hourly 2 m temps inside the local-standard-time day (open data has no max-temp field).
- Hand check LA 2026-06-25: samples 61.2/68.8/71.8/63.9°F → high 71.8°F (Kalshi settled 72).

**2026-10-24 — 6.1** ([x])
- Strands Decider 2B (official package, CPU; Ollama build needs MLX) answers bet/skip per candidate from a small JSON (city, forecast, sd, probability, price, fee, edge, station TRAIN error, spread, volume traded before bet time).
- Hand call KXHIGHLAX-26JUN23-T69 → {bet 0.81, skip 0.19}; 2.47 s/call. Full run (3,262 candidates) in background → data/judge/calls.jsonl.

**2026-10-24 — 2.2** ([x])
- 9 runs (5/3/1 days before each reference time) from ECMWF's archived real-time AIFS Single (2025 = v1.x; see DECISIONS.md), msl over 5–50°N, 100–30°W, 6-hourly to +144 h. Tracker: lowest msl within 250 km of the extrapolated last centre (model/hurricanes.py).

**2026-10-24 — 2.3** ([x])
- Errors vs IBTrACS at 24/48/72/120 h + reference-time error, in results/hurricanes.json. Big miss reported: IMELDA 5-day run stalls the storm near GA/SC instead of turning to Bermuda (1,236 km at 120 h).
- CHECK: MELISSA 3-day run +24 h: AIFS 16.00N 76.25W vs IBTrACS row 2025-10-26 12:00 16.3N 76.4W → hand haversine 37.0 km = scorer 37.0 km. (AIFS centre pressure 986 vs observed 952 hPa — model too weak.)

**2026-10-24 — 7.3** ([x])
- No demo keys in ~/.kalshi, so per CLAUDE.md only a read-only authenticated balance call on prod: OK (logs/live/order_test.json; no amounts logged). bot/order_test.py would place+cancel a 1¢ demo order via the same order_body() if demo keys are added.
- Order shape follows Kalshi Create Order V2 (/portfolio/events/orders; NO buys = ask side at the YES price) — unit-tested, not yet exercised against an exchange.

**2026-10-24 — 2.4** ([x])
- results/hurricanes.json saved (tracks + errors). Real NOAA GOES-19 band-13 IR loops rendered from the raw ABI L2 files (mesoscale sector on each storm, 1 frame/min, 3 h before reference time): results/final_footage/goes_{melissa,imelda,erin}.mp4, 6 s each (git-ignored); results/goes_loops.json.
- Credit line added to CREDITS.md.

---
## MOVED TO DGX (2026-10-24)

Work so far ran on a GPU-less x86 mini PC (i9-12900HK, 15 GB RAM), not the DGX Spark. Stopped here on the user's
instruction: all background jobs killed (judge run at 835/3,262 calls in data/judge/calls.jsonl — partial; 1.2
input download), no systemd timers or cron installed (bot/systemd/ holds unit drafts only).

**Where each forecast came from**
- **Local AIFS v2 run (this mini PC, CPU, flash-attn stand-in model/cpu_flash):** only the 1.1 smoke test,
  init 2026-10-23 12Z, 12 h lead (data/aifs_runs/2026102312_12h.npz) and its LA sanity check
  (results/aifs_la_sanity.json). Not a 10-day run; 1.1 is NOT done.
- **ECMWF archive (real-time open data on AWS, ecmwf-forecasts bucket):** all backtest AIFS forecasts
  (D-1 00Z runs, AIFS Single v2 operational) and all hurricane forecasts (2025 runs, AIFS Single v1.x).
- **Other:** GFS baseline = Open-Meteo single-run API (gfs_global, D-1 00Z). No weather model ran for Kalshi,
  NWS, IBTrACS or GOES data.

**Per completed task — does its output depend on where the weather AI ran?**
- 0.1 repo skeleton — no.
- 0.2 env (⚠️) — yes: machine-specific (no NVIDIA GPU, x86). Redo on DGX (ARM64 + GPU, real flash-attn).
- 1.3 timing — YES: measured CPU speed (~528 s/step) on this mini PC. Redo on DGX; the decision to use the
  archive for the backtest/hurricanes should be revisited with DGX timings.
- 2.1 storm choice — no (IBTrACS).
- 2.2/2.3 hurricane tracks + scores — no local run: ECMWF archive (AIFS v1.x real-time). Would change only if
  hurricanes are rerun locally on DGX (note: v2 on 2025 storms may be in-sample, see DECISIONS.md).
- 2.4 GOES loops + hurricanes.json — no (NOAA data; hurricanes.json from archive).
- 3.1–3.4 cities, Kalshi history, NWS check, fees — no.
- 4.1 AIFS daily highs — no local run: ECMWF archive (AIFS Single v2, D-1 00Z). Would change if the backtest
  is rerun locally on DGX.
- 4.2 GFS baseline — no (Open-Meteo).
- 4.3 station correction — depends on 4.1's source (archive), not on this machine.
- 5.1–5.4 backtest + robustness — depend on 4.1/4.3 (archive AIFS) and GFS; not on this machine.
- 6.1 judge hand call — model ran on this CPU (official strands-decider package; Ollama build needed MLX).
  Probabilities shouldn't depend on hardware beyond last digits; try Ollama on DGX. Full run incomplete.
- 7.3 order test — no (read-only balance call; no demo keys).

**Next on DGX:** redo 0.2, 1.1 (10-day local run + LA check), 1.2, 1.3 timing; finish 6.1 full judge run
(resumes from data/judge/calls.jsonl if copied), then 6.2, 6.3, 7.1, 7.2, 7.4, 7.5.

---
## ON THE DGX SPARK (from 2026-10-24)
Kalshi key re-checked with one read-only call: OK. Tasks that depend on the weather AI or the hardware re-opened (see DECISIONS.md).

**2026-10-24 — 0.2** ([x])
- DGX Spark: aarch64 (10× Cortex-X925 + 10× Cortex-A725), NVIDIA GB10, nvidia-smi works (driver 580, CUDA 13.0), 2.0 TB free disk.
- Envs rebuilt with uv for aarch64: main (uv.lock), model/aifs (torch 2.14.1+cu130 — 2.7 has CVEs), model/judge (torch 2.14.1+cu130). OSV: 0 known vulns in all three locks.
- Next: 0.3.

**2026-10-24 — 0.3** ([x])
- ElevenLabs key + voice ID present in this machine's environment; Kalshi prod key OK (read-only), balance ≥ $10 (yes/no check only); git push via SSH remote. No demo key (optional).
- Next: 1.1.

**2026-10-24 — 1.1** ([x])
- AIFS Single v2 on the GB10 GPU (flash-attn stand-in, no aarch64 wheel). 10-day run from 2026-10-23 00Z open data: data/aifs_runs/2026102300_240h.npz, 170 s wall.
- LA check (results/aifs_la_sanity.json): AIFS vs KLAX obs 17.8/16, 16.7/16, 19.3/21, 21.0/21 °C. GPU vs mini-PC CPU from the same input: 2t RMS diff 0.005 K (results/aifs_gpu_vs_cpu.json).
- Next: 1.2.

**2026-10-24 — 1.2** ([x])
- Past start 2026-06-22 00Z (first backtest init) from ECMWF open data: data/aifs_runs/2026062200_60h.npz. Inputs via fetch/ifs_inputs.py (Google Cloud copy; AWS bucket throttled with 503 Slow Down) — identical to the earthkit-built input (max diff 1e-10).
- 2025 start dates (e.g. 2025-10-01) are impossible for v2: open data before ~2026-05-15 lacks its wave/snow inputs (DECISIONS.md).
- Next: 1.3.

**2026-10-24 — 1.3** ([x])
- results/timing.json: 60-h backtest run 69 s wall (28 s inputs, 35 s model), 3.0 s per 6-h step; 10-day run 170 s.
- Estimates: backtest 120 runs 2.3 h (< 12 h → run all locally, archive kept for comparison), Isaias 3 runs 0.1 h, live week 0.13 h.
- Next: 2.2 (hurricanes); 4.1 local backtest running in background (logs/4.1_local.log).

**2026-10-24 — 4.1** ([x])
- Backtest forecasts rerun locally on the DGX (1.3: 2.3 h < 12 h): 120 AIFS v2 runs, D-1 00Z, 60 h (model/backtest_runs.py, 0 failures) → data/aifs_local/points → results/aifs_highs.csv (720 station-days, nearest N320 point, max of 4 six-hourly 2t). Archive version kept: results/aifs_highs_archive.csv.
- Hand check LA 2026-06-25: raw N320 point 33.86N 118.40W, samples 60.75/65.68/67.79/62.56 °F → high 67.79 (archive 71.76, Kalshi 72).
- Next: 4.3.

**2026-10-24 — 4.3** ([x])
- Refit on TRAIN with local forecasts (results/corrections.json, forecasts.csv). TEST MAE °F: GFS 3.28, raw AIFS 3.49, corrected AIFS 2.13 (archive-based run was 3.25 / 2.42). tests/test_split.py passes (fit() refuses TEST dates).
- Correction still hurts NYC on TEST (1.24 → 1.78); LA raw bias −4.6 °F (coastal grid point) fixed to 2.79 MAE.
- Next: 5.1.

**2026-10-24 — 5.1** ([x])
- Rerun on local-AIFS forecasts: backtest/sim.py bracket_prob() unchanged — Normal(mu, sigma) with ±0.5 °F integer continuity; sigma = station TRAIN spread.
- Next: 5.2.

**2026-10-24 — 5.2** ([x])
- Same rule for all players (ask at bet time, taker fee, ≤ $1/market, threshold tuned on TRAIN). logs/handcheck.md regenerated: 5 random TEST bets recomputed from raw files — all match sim.py.
- Next: 5.3.

**2026-10-24 — 5.3** ([x])
- results/backtest.json, backtest_summary.csv, backtest_bets.csv, candidates.csv (PAPER MONEY, TEST). Archive-forecast version kept in results/archive_forecasts/.
- TEST P&L: GFS −$167.40 (410 bets), raw AIFS −$130.65 (254), corrected AIFS + rule −$129.11 (687). Market mid-price Brier 0.105 beats every model (0.130–0.150). Per-bet sums = totals (asserted).
- Next: 5.4.

**2026-10-24 — 5.4** ([x])
- results/robustness.csv/.json: fees ×1.5, threshold −0.02/+0.02/+0.05 and combined. No player profitable on TEST in any case (best: raw AIFS −$108.36 at +0.05). Conclusion holds.
- Next: 6.1 (judge on GPU).

**2026-10-24 — 2.2** ([x])
- 2025 storms (MELISSA/IMELDA/ERIN) stay on ECMWF's archived real-time AIFS runs: AIFS v2 can't be started locally before ~2026-05-15 (open data lacks its wave/snow inputs; DECISIONS.md). Local test added: ISAIAS 2026 (only 2026 Atlantic hurricane to reach land), 3 runs (5/3/1 days before landfall, 144 h) on the DGX → data/aifs_local/fields via model/local_fields.py (N320 → 0.25°). Local vs archive msl over the box: MAE 0.03–0.05 hPa to 72 h.
- Next: 2.3.

**2026-10-24 — 2.3** ([x])
- 2025 scores unchanged (results/hurricanes.json; hand check MELISSA 3-day +24 h = 37.0 km still valid). ISAIAS: results/isaias_local.json vs results/isaias_archive.json — landfall error 3-day 97.0 km local / 79.0 km archive, 1-day 32.6 / 32.6 km; 5-day run untrackable in both (pre-genesis disturbance, no low below 1010 hPa). Track is provisional IBTrACS.
- Next: 2.4.

**2026-10-24 — 2.4** ([x])
- results/hurricanes.json (2025, archive) + results/isaias_local.json / isaias_archive.json saved; GOES loops (results/final_footage/goes_*.mp4) and the CREDITS.md line unchanged (NOAA data, hardware-independent).
- Next: 6.1 judge run (GPU, in background).

**2026-10-24 — 6.1** ([x])
- Strands Decider 2B on the GB10 GPU (official package; Ollama's MLX-only builds can't run on Linux arm64, DECISIONS.md). Fresh run on the local-AIFS candidates: 3,225/3,225 inputs answered, 0.07 s/call (mini PC: 2.75 s). Cache keyed by input hash; mini-PC calls set aside in data/judge/.
- Hand call KXHIGHLAX-26JUN23-T76 → {bet 0.487, skip 0.513} = batch answer.
- Next: 6.2.

**2026-10-24 — 6.2** ([x])
- results/judge.json (PAPER MONEY, TEST): judge (P(bet) > 0.62, cut-off tuned on TRAIN) −$93.15 on 1,176 bets (win 61.5%) vs one-line rule (edge > 0.09) −$129.11 on 687 bets. Judge loses less but still loses; corr(P(bet), edge) = 0.35.
- Next: 6.3.

**2026-10-24 — 6.3** ([x])
- results/judge_examples.json: 3 TEST decisions with the judge's probabilities (a judge bet, a skip the rule would take, a close call).
- Next: 7.1.

**2026-10-24 — 7.1** (⏸)
- RULES.md + RULES.json written (corrected AIFS + one-line rule, edge > 0.09; no player made money on TEST, best was the judge at −$93.15 — said so in RULES.md). Station corrections frozen into RULES.json. Committed, tagged rules-locked, pushed; RULES.md SHA-256 84e0aa5e…11ed3.
- Issue NOT opened: gh on this machine is logged in to a personal account, and posting from it would tie a personal username to the channel repo. bot/open_issue.sh does step 3 once gh is logged in as Tacdelgineer (🧑). live.py posts picks only as Tacdelgineer.
- Next: 7.2.

**2026-10-24 — v1 bug → v2 rules** (user instruction; 7.2 resumed)
- By-hand DRY_RUN (v1) found the station-correction bug: Phoenix raw 76.31 → 85.49 °F vs GFS 77.3 / NWS 79; edges 0.70–0.85 at 1–6¢. Journal + evidence: video/JOURNAL.md, results/evidence/v1-bug/. CLAUDE.md now requires a JOURNAL entry for every surprise.
- v2 = rolling 30-day bias (past data only, ≥ 20 days) + guards (≤ 4 °F from GFS, edge ≤ 0.30), in backtest/rolling.py, used by the backtest and live.py; tests/test_guards.py. Re-ran 4.3, 5.2–5.4, 6.1 inputs/6.2 on the same split: results/v1/ vs results/v2/, results/v1_vs_v2.json/.csv. TEST: GFS −$66.03, raw −$12.41, rule −$106.46, judge +$2.94 (v1: −167.40 / −130.65 / −129.11 / −93.15). handcheck (v2) matches.
- RULES.md v2 (live player = corrected AIFS + judge, PLAN rule), tag rules-locked-v2; v1 tag kept. v2 designed after seeing TEST (DECISIONS.md).
- Next: 7.1 issue (bot/open_issue.sh), then v2 DRY_RUN, then 7.5.

**2026-10-25 — 7.1** ([x])
- Issue: https://github.com/Tacdelgineer/desk-weather-bet/issues/1. First comment: v1 (rules-locked, SHA-256 84e0aa5e5b55e5ab3e5958f14b5031e020f41ba2b186457d0a99e84fb1911ed3) marked superseded; v2 (rules-locked-v2, SHA-256 7e99eac0ced1dae151ff4f71294a307f3d51a107a11047bb398be7f288e0ce7e, commit dbb2499978b155dfe7bc76bf6938a3d409bd480e). LIVE_ISSUE written; bot/live.py posts daily picks there (only as Tacdelgineer).

**2026-10-25 — 7.2** ([x])
- bot/live.py v2: rolling 30-day correction (results/live_history.csv fills days after the backtest window from our AIFS runs + Kalshi settled values), GFS-gap + edge-cap guards, judge input = backtest's judge_state. 28 tests pass.
- By-hand v2 DRY_RUN for 2026-10-25 (logs/live/2026-10-24_picks.json): 2 picks (LA NO @0.67 edge 0.163, Miami NO @0.74 edge 0.099), both within 4 °F of GFS, edges ≤ 0.30; 8 candidates guarded. Posted to issue #1. JOURNAL entry vs v1 picks; results/dryrun_v1_vs_v2.json.
- Next: 7.5 (timers, still DRY_RUN).

**2026-10-25 — 7.5** (⏸)
- systemd user timers enabled (linger on): dwb-forecast 08:30/10:30 UTC, dwb-picks 16:00 UTC (settle + picks + issue post), dwb-cancel 19:05 UTC; all DRY_RUN until GO_LIVE. Listed with systemctl --user list-timers 'dwb-*'. Manual start of dwb-cancel.service under systemd: exit 0, logs/live/2026-10-25_cancel.json.
- Waiting for the first automatic run (forecast 2026-10-25 08:30 UTC → logs/timer_forecast.log; picks 16:00 UTC → logs/timer_picks.log). Next session: confirm both logged, then tick 7.5.

**2026-11-07 — 7.4, 7.5, 7.6** ([x])
- GO_LIVE (10) was created 2026-10-25 19:50 UTC; timers ran automatically from 10-25. Live week = runs 10-26 → 11-01.
- Settled from Kalshi's own records (tools/kalshi_records.py, read-only → data/live_kalshi/; tools/settle_live.py → results/live.json): 4 real orders, all filled, 2 won / 2 lost, P&L −$0.4959, none outside the window, none unfilled.
- Only 2 of 7 days traded: picks job crashed from 10-28 (settled_high() float('70° to 71°')). live.py also has no end-date check. JOURNAL entry. dwb-forecast + dwb-picks timers disabled; dwb-cancel left enabled (only cancels resting orders; none exist). STOP file present (not created by Claude).
- Next: 8.1 outline, style preview.

**2026-11-07 — 8.1** ([x]) + style preview
- video/OUTLINE.md. Chapter kit copied into video/ (styles, tools). Voice: eleven_v4 per ~/ai-dev-skills/FINAL_VOICE.md; PLAN 9.3 updated.
- Style preview (not a final chapter): video/chapters/90_scenes.js, data from video/preview/export.py + prep_goes.py; one v4 take of the hook (12/12 words aligned, 28 ElevenLabs credits). Output results/preview/style_preview.mp4 + contact_sheet.png (gitignored mp4).
- Open: owner approves the look; crash fix in live.py not done (live week is over; fix only if a second live week is wanted).
- Next: 8.2 rooms after approval.
- Rendered: results/preview/style_preview.mp4 (41.0 s, 1920x1080, 30 fps), contact_sheet.png, shot3_vertical.png. Not pushed: repo is PUBLIC, owner to OK the push (scan clean). live_ledger.json + logs/live/*.json left uncommitted (contain Kalshi order ids).
- 2026-11-07: owner approved the preview look and the push; pushed. Next: 8.2 rooms in this style.

**2026-11-07 — 8.2** ([x])
- Owner chose option 1 for the pushed ledger: history left alone; ledger gitignored + untracked; CLAUDE.md now says commit only named files (DECISIONS.md).
- Rooms = footage pages in the approved preview style (riso / EVIDENCE / CRT / papercut), one per chapter 00–11, 2–5 shots each, 5–36 s; built by video/tools/mkroom.py from chapters/chapters.json; all numbers from video/export.py (the one export step) + video/prep_goes.py (real GOES frames for MELISSA, IMELDA, ERIN). Real captures for CRT/evidence in results/evidence/captures/ (git tags, issue #1 first comment, day-3 traceback; home paths cut).
- Chapter 09 has everything 8.2 asks for: scatter, NWS-vs-bot EVIDENCE, tags + public hashes (CRT), both stat cards. Chapter 10 has REC-01 slot (Kalshi account).
- Check: tools/check.cjs = 0 page errors on all 13 pages; contact sheets reviewed (video/work/sheets/, gitignored).
- Not built (no file to back a number): the "$67 bots", the afternoon peak, the Weather Channel app; the AIFS model card and public pages come with 8.3 recordings.
- Next: 8.3 recordings (VHS terminal + Playwright of public pages), then 8.4 render (shots → results/final_footage/{wide,vertical}/ + ORDER.txt).

**2026-11-07 — owner changes + 8.3 → 10.3 (in progress)**
- Pushed 8.2. Ch 00 now opens on the storm + the question only (money result kept for ch 10).
- New beats: afternoon peak (ch 05, actual − raw AIFS per station from results/v2/corrections.json), the weather-app news
  article (ch 04, EVIDENCE, no numbers), a $67 bot listing (ch 05, EVIDENCE, seller name blurred; names kept in the
  gitignored video/rec/blur.local.json).
- 8.3: Playwright captures of 6 public pages → results/evidence/web/*.png/json + results/final_footage/rec/web_*.mp4;
  VHS: real AIFS run (2026-11-06T06, 60 h, 57 s), GPU query, bot cap tests + the real DRY_RUN log
  (results/final_footage/rec/vhs_*.mp4). Kalshi page says it settles "according to The Weather Company" (JOURNAL).
- 9.1/9.2: video/SCRIPT.md (1,026 words), Check lines verified against results files. 9.3: 11 eleven_v4 takes
  (one each, 2,504 credits; all words present — Whisper misses were digits only).
- Assembly: tools/warp.py lines each shot up to its phrase; tools/build_chapters.sh renders; tools/split_footage.py cuts
  shots for 8.4; packaging/make.py writes README results, titles, description, thumbnail prompts.

**2026-11-07 — 8.3–10.3 closed** ([x]; 10.4, 10.5 ⏸ owner)
- dwb-cancel.timer disabled (owner); no dwb timers enabled.
- 8.4: split_footage.py made safe to re-run (an interrupted run had left a broken ch 04 vertical file) and finished: 40 shots wide + vertical, 3 stat cards, results/final_footage/ORDER.txt (398.9 s = full_render.mp4). Every file plays. 8.5 footage locked.
- 10.3: packaging/make.py → packaging/TITLES.md, DESCRIPTION.md, THUMBNAILS.md (prompts for the owner's 3 thumbnails, each number with its results file), README.md results.
- 🧑 Next: 10.4 record REC-01 (Kalshi account, 8 s at 5:53, see video/RECORDINGS.md) and lay it over the slate in CapCut; 10.5 thumbnails + upload.
