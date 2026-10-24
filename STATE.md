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
