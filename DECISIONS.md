# DECISIONS.md — one line per decision: date · choice · why

- Key paths (outside the repo): `~/.kalshi/prod.pem` + `~/.kalshi/prod_key_id`; optional `~/.kalshi/demo.pem` + `~/.kalshi/demo_key_id`.
- 2026-10-23 · This session runs on an x86_64 machine (Intel i9-12900HK, 20 threads, 15 GB RAM, Intel iGPU, no NVIDIA GPU, 386 GB free disk), not the DGX Spark. · Proceed on CPU: try AIFS CPU inference first; if it OOMs or is too slow, use ECMWF's archived real-time AIFS forecasts (PLAN 1.2's documented fallback). Flagged to the user.
- 2026-10-23 · Kalshi prod key is Ed25519; the read-only balance call accepted an Ed25519 signature. · Sign requests with Ed25519 when the key is Ed25519, RSA-PSS otherwise.
- 2026-10-24 · Cities = top 6 US KXHIGH daily series by 30-day volume (to 2026-10-23): LA (KLAX), NYC (KNYC, Central Park), Miami (KMIA), Chicago (KMDW, Midway), Phoenix (KPHX), San Francisco (KSFO). · PLAN rule; stations read from each market's rules (CLIxxx code).
- 2026-10-24 · Market rules now say settlement uses "The Weather Company" value for the named NWS climate station (e.g. CLINYC), not the NWS report itself. · Ground truth = Kalshi's own settled value (expiration_value); NWS Daily Climate Report used as the 3.3 cross-check.
- 2026-10-24 · Fee = Kalshi general (taker) formula round_up(0.07·C·P·(1−P)) to the cent, from the fee schedule PDF (effective Feb 5, 2026; live PDF is behind a bot check, so the 2026-06-12 Wayback copy is saved in results/sources/). Series API confirms fee_type=quadratic, multiplier=1. · Backtest buys at the ask, so taker fee applies.
