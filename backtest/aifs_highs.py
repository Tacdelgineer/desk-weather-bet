"""4.1 — AIFS daily high per station and market date: max of the 6-hourly 2 m temperatures (nearest grid point)
that fall inside the station's local-standard-time day, from the D-1 00Z run (available before bet time).
Neither our runs nor the open-data AIFS output have a max-temperature field (only 6-hourly 2t), so the max is over
those samples.
  --source local   (default) our own DGX runs, data/aifs_local/points/   -> results/aifs_highs.csv (backtest input)
  --source archive ECMWF's archived real-time AIFS, data/aifs_archive/points/ -> results/aifs_highs_archive.csv"""
import datetime as dt
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backtest.window import DAYS  # noqa: E402
from fetch.gfs import LST_OFFSET  # noqa: E402

PTS = {"local": ROOT / "data" / "aifs_local" / "points", "archive": ROOT / "data" / "aifs_archive" / "points"}
OUTCSV = {"local": ROOT / "results" / "aifs_highs.csv", "archive": ROOT / "results" / "aifs_highs_archive.csv"}


def k_to_f(k):
    return (k - 273.15) * 9 / 5 + 32


def day_samples(run, station, date, tz):
    init = dt.datetime.fromisoformat(run["init"])
    a = dt.datetime(date.year, date.month, date.day) - dt.timedelta(hours=LST_OFFSET[tz])
    b = a + dt.timedelta(days=1)
    out = []
    for s, v in zip(run["steps"], run["t2m_K"][station]):
        t = init + dt.timedelta(hours=s)
        if a <= t < b:
            out.append((t.isoformat(), round(k_to_f(v), 2)))
    return out


def main(only=None, source="local"):
    cities = json.loads((ROOT / "results" / "cities.json").read_text())
    rows = []
    for d in DAYS:
        init = dt.datetime(d.year, d.month, d.day) - dt.timedelta(days=1)
        f = PTS[source] / f"{init:%Y%m%d%H}.json"
        if not f.exists():
            continue
        run = json.loads(f.read_text())
        for c in cities:
            if only and c["station"] != only:
                continue
            smp = day_samples(run, c["station"], d, c["tz"])
            rows.append(dict(city=c["city"], station=c["station"], date=str(d), init=run["init"], model=run["model"],
                             aifs_high=max(v for _, v in smp) if smp else None, n_samples=len(smp),
                             samples=";".join(f"{t[5:13]}Z={v}" for t, v in smp)))
    df = pd.DataFrame(rows)
    if not only:
        df.to_csv(OUTCSV[source], index=False)
    return df


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("station", nargs="?", help="only this station (hand check; writes nothing)")
    ap.add_argument("--source", choices=["local", "archive"], default="local")
    a = ap.parse_args()
    print(main(a.station, a.source).head(3).to_string())
