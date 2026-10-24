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
