"""4.1 — run AIFS locally on the DGX for every backtest init (D-1 00Z for each market date D, lead 60 h), then
extract each station's 2 m temperature at its nearest N320 grid point, in the same JSON shape as the archive points:
  data/aifs_runs/<init>_60h.npz  ->  data/aifs_local/points/<init>.json

Run in the model env:  uv run --project model/aifs python model/backtest_runs.py [--limit N] [--points-only]
Safe to re-run: run_aifs.py skips runs that exist, and points files that exist are skipped. Writes the done-marker
results/.done/aifs_local_backtest when every init has a points file. Per-run wall times -> logs/aifs_local_times.csv.
"""
import argparse
import datetime as dt
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backtest.window import DAYS  # noqa: E402

RUNS = ROOT / "data" / "aifs_runs"
PTS = ROOT / "data" / "aifs_local" / "points"
TIMES = ROOT / "logs" / "aifs_local_times.csv"
LEAD = 60


def nearest(lat, lon, plat, plon):
    d = np.radians
    return int(np.argmax(np.sin(d(lat)) * np.sin(d(plat)) + np.cos(d(lat)) * np.cos(d(plat)) * np.cos(d(lon - plon % 360))))


def points(init):
    f = PTS / f"{init:%Y%m%d%H}.json"
    if f.exists():
        return "cached"
    run = RUNS / f"{init:%Y%m%d%H}_{LEAD}h.npz"
    if not run.exists():
        return "no run"
    z = np.load(run)
    cities = json.loads((ROOT / "results" / "cities.json").read_text())
    res = {"init": init.isoformat(), "model": "aifs-single-v2 local (DGX)", "steps": [int(s) for s in z["steps"]],
           "grid": {}, "t2m_K": {}}
    for c in cities:
        k = nearest(z["lat"], z["lon"], c["lat"], c["lon"])
        res["grid"][c["station"]] = [float(z["lat"][k]), float(z["lon"][k])]
        res["t2m_K"][c["station"]] = [round(float(v), 3) for v in z["2t"][:, k]]
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(res))
    return "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--points-only", action="store_true")
    a = ap.parse_args()
    inits = [dt.datetime(d.year, d.month, d.day) - dt.timedelta(days=1) for d in DAYS]
    if a.limit:
        inits = inits[:a.limit]
    for init in inits:
        if not a.points_only and not (RUNS / f"{init:%Y%m%d%H}_{LEAD}h.npz").exists():
            t0 = time.time()
            r = subprocess.run([sys.executable, str(ROOT / "model" / "run_aifs.py"), "--date", f"{init:%Y-%m-%dT%H}",
                                "--lead", str(LEAD), "--no-input-cache"], cwd=ROOT, capture_output=True, text=True)
            wall = time.time() - t0
            if r.returncode != 0:
                print(f"{init:%Y-%m-%dT%H} FAILED rc={r.returncode}: {r.stderr.strip().splitlines()[-1:]}", flush=True)
                continue
            new = not TIMES.exists()
            with TIMES.open("a") as f:
                f.write(("init,wall_s\n" if new else "") + f"{init:%Y-%m-%dT%H},{wall:.1f}\n")
        print(f"{init:%Y-%m-%dT%H}", points(init), flush=True)
    if not a.limit and all((PTS / f"{i:%Y%m%d%H}.json").exists() for i in inits):
        (ROOT / "results" / ".done").mkdir(parents=True, exist_ok=True)
        (ROOT / "results" / ".done" / "aifs_local_backtest").touch()
        print("all done")


if __name__ == "__main__":
    sys.exit(main())
