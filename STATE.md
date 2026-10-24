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
