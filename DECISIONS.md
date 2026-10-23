# DECISIONS.md — one line per decision: date · choice · why

- Key paths (outside the repo): `~/.kalshi/prod.pem` + `~/.kalshi/prod_key_id`; optional `~/.kalshi/demo.pem` + `~/.kalshi/demo_key_id`.
- 2026-10-23 · This session runs on an x86_64 machine (Intel i9-12900HK, 20 threads, 15 GB RAM, Intel iGPU, no NVIDIA GPU, 386 GB free disk), not the DGX Spark. · Proceed on CPU: try AIFS CPU inference first; if it OOMs or is too slow, use ECMWF's archived real-time AIFS forecasts (PLAN 1.2's documented fallback). Flagged to the user.
- 2026-10-23 · Kalshi prod key is Ed25519; the read-only balance call accepted an Ed25519 signature. · Sign requests with Ed25519 when the key is Ed25519, RSA-PSS otherwise.
