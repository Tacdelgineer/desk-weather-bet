"""Our DGX AIFS runs vs ECMWF's archived real-time AIFS Single v2 runs (same model weights, same D-1 00Z start).
Differences come from the start data (we start from 0.25° open data, ECMWF from its full-resolution analysis), the
grids (we read the nearest N320 point, the archive is regridded to 0.25°) and GPU arithmetic.

1. every station-day: 6-hourly 2 m temps and daily highs, local - archive, and each one's error vs Kalshi's settled high
2. a few runs, whole field: 2 m temperature over the continental US box, local (regridded to 0.25°) - archive
Writes results/aifs_local_vs_archive.json. Run in the model env (needs eccodes + earthkit-regrid):
  uv run --project model/aifs python backtest/local_vs_archive.py
"""
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backtest.window import is_test  # noqa: E402
from fetch.aifs_archive import fetch_fields  # noqa: E402

FIELD_INITS = ["2026-06-22T00", "2026-08-21T00", "2026-10-19T00"]  # first, middle, last backtest init
FIELD_STEPS = [24, 36, 48, 60]
CONUS = (24.0, 50.0, -125.0, -66.0)  # lat_min, lat_max, lon_min, lon_max


def k_to_f(k):
    return (np.asarray(k) - 273.15) * 9 / 5 + 32


def stats(d):
    d = np.asarray(d, float)
    return dict(n=int(d.size), mean=round(float(d.mean()), 3), mae=round(float(np.abs(d).mean()), 3),
                rms=round(float(np.sqrt((d ** 2).mean())), 3), max_abs=round(float(np.abs(d).max()), 3))


def samples():
    rows = []
    for f in sorted((ROOT / "data" / "aifs_local" / "points").glob("*.json")):
        loc = json.loads(f.read_text())
        arc_f = ROOT / "data" / "aifs_archive" / "points" / f.name
        if not arc_f.exists():
            continue
        arc = json.loads(arc_f.read_text())
        for st, vals in loc["t2m_K"].items():
            a = dict(zip(arc["steps"], arc["t2m_K"][st]))
            for s, v in zip(loc["steps"], vals):
                if s in a:
                    rows.append(dict(init=loc["init"], station=st, step=s, local_F=float(k_to_f(v)),
                                     archive_F=float(k_to_f(a[s]))))
    return pd.DataFrame(rows)


def field_diffs():
    import earthkit.regrid as ekr
    la0, la1, lo0, lo1 = CONUS
    i0, i1 = int((90 - la1) / 0.25), int((90 - la0) / 0.25) + 1
    j0, j1 = int((lo0 + 180) / 0.25), int((lo1 + 180) / 0.25) + 1
    out = []
    for s_init in FIELD_INITS:
        init = dt.datetime.strptime(s_init, "%Y-%m-%dT%H")
        run = ROOT / "data" / "aifs_runs" / f"{init:%Y%m%d%H}_60h.npz"
        if not run.exists():
            continue
        z = np.load(run)
        for s in FIELD_STEPS:
            k = list(z["steps"]).index(s)
            loc = ekr.interpolate(z["2t"][k].astype(np.float64), {"grid": "N320"}, {"grid": (0.25, 0.25)})
            loc = np.roll(loc.reshape(721, 1440), 720, axis=1)[i0:i1, j0:j1]
            arc = fetch_fields(init, s, {"2t"})["2t"][i0:i1, j0:j1]
            d = (loc - arc) * 9 / 5  # K difference -> °F difference
            out.append(dict(init=s_init, step=s, **{f"{k2}_F": v for k2, v in stats(d.ravel()).items() if k2 != "n"},
                            n_points=int(d.size)))
    return out


def main():
    df = samples()
    df["diff_F"] = df.local_F - df.archive_F
    hl = pd.read_csv(ROOT / "results" / "aifs_highs.csv")
    ha = pd.read_csv(ROOT / "results" / "aifs_highs_archive.csv")
    mk = pd.read_csv(ROOT / "results" / "markets.csv").groupby(["station", "date"], as_index=False).settled_high.first()
    h = hl[["station", "date", "aifs_high"]].merge(ha[["station", "date", "aifs_high"]], on=["station", "date"],
                                                    suffixes=("_local", "_archive")).merge(mk, on=["station", "date"])
    h = h.dropna()
    h["diff_F"] = h.aifs_high_local - h.aifs_high_archive
    h["split"] = np.where(h.date.map(is_test), "TEST", "TRAIN")
    out = dict(
        what=__doc__.strip().splitlines()[0],
        why_different=" ".join(l.strip() for l in __doc__.strip().splitlines()[1:3]),
        n_inits=int(df.init.nunique()),
        t2m_6hourly_local_minus_archive_F=stats(df.diff_F),
        t2m_6hourly_by_station_F={st: stats(g.diff_F) for st, g in df.groupby("station")},
        daily_high_local_minus_archive_F=stats(h.diff_F),
        daily_high_by_station_F={st: stats(g.diff_F) for st, g in h.groupby("station")},
        daily_high_mae_vs_settled_F={sp: dict(local=round(float((g.aifs_high_local - g.settled_high).abs().mean()), 3),
                                              archive=round(float((g.aifs_high_archive - g.settled_high).abs().mean()), 3),
                                              n=int(len(g))) for sp, g in h.groupby("split")},
        field_2t_conus_local_minus_archive=field_diffs(),
    )
    (ROOT / "results" / "aifs_local_vs_archive.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("n_inits", "t2m_6hourly_local_minus_archive_F", "daily_high_local_minus_archive_F",
                                          "daily_high_mae_vs_settled_F")}, indent=1))
    for r in out["field_2t_conus_local_minus_archive"]:
        print(r)


if __name__ == "__main__":
    main()
