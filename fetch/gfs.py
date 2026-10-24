"""4.2 — free GFS forecast baseline from Open-Meteo's single-run API: for each city and market date D, the GFS run
initialised D-1 00Z (same run time as the AIFS player), hourly 2 m temperature at the station point, max over the
station's local-standard-time day (the NWS climate day). Cache: data/gfs/<station>/<run>.json.
Writes results/gfs_highs.csv. Safe to re-run."""
import datetime as dt
import json
import sys
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backtest.window import DAYS  # noqa: E402

CACHE = ROOT / "data" / "gfs"
# NWS climate day = local standard time all year
LST_OFFSET = {"America/Los_Angeles": -8, "America/Phoenix": -7, "America/Denver": -7, "America/Chicago": -6,
              "America/New_York": -5}


def run_series(c, run):
    f = CACHE / c["station"] / f"{run:%Y%m%d%H}.json"
    if f.exists():
        return json.loads(f.read_text())
    for i in range(5):
        r = requests.get("https://single-runs-api.open-meteo.com/v1/forecast", timeout=60, params=dict(
            latitude=c["lat"], longitude=c["lon"], hourly="temperature_2m", models="gfs_global",
            run=f"{run:%Y-%m-%dT%H:%M}", temperature_unit="fahrenheit", forecast_days=4, timezone="GMT"))
        if r.status_code == 200:
            break
        time.sleep(5 * (i + 1))
    r.raise_for_status()
    h = r.json()["hourly"]
    d = {"run": run.isoformat(), "time": h["time"], "t2m_F": h["temperature_2m"]}
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(d))
    return d


def day_max(series, date, tz):
    off = LST_OFFSET[tz]
    a = dt.datetime(date.year, date.month, date.day) - dt.timedelta(hours=off)  # local midnight in UTC
    b = a + dt.timedelta(days=1)
    vals = [v for t, v in zip(series["time"], series["t2m_F"])
            if v is not None and a <= dt.datetime.fromisoformat(t) < b]
    return (max(vals), len(vals)) if vals else (None, 0)


def main():
    cities = json.loads((ROOT / "results" / "cities.json").read_text())
    rows = []
    for c in cities:
        for d in DAYS:
            run = dt.datetime(d.year, d.month, d.day) - dt.timedelta(days=1)
            s = run_series(c, run)
            hi, n = day_max(s, d, c["tz"])
            rows.append(dict(city=c["city"], station=c["station"], date=str(d), run=run.isoformat(),
                             gfs_high=hi, n_hours=n))
        print(c["station"], "done", flush=True)
    pd.DataFrame(rows).to_csv(ROOT / "results" / "gfs_highs.csv", index=False)
    print("rows", len(rows))


if __name__ == "__main__":
    main()
