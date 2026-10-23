# STATE.md — running log (newest at the bottom)


**2026-10-23 — 0.1** ([x])
- Repo skeleton created and pushed; .pem and GO_LIVE confirmed ignored by git check-ignore.
- Next: 0.2 environment.

**2026-10-23 — 0.2** (⚠️)
- uv env created (Python 3.12; numpy/pandas/scipy/requests/cryptography/pytest).
- CPU: 12th Gen Intel i9-12900HK (x86_64, 20 threads), RAM 15 GB, free disk 386 GB (>200 GB OK).
- nvidia-smi: command not found — this machine has no NVIDIA GPU (not the DGX Spark). CHECK can't pass here; continuing on CPU (see DECISIONS.md).
- Next: 0.3 (print H1), then 1.1.
