"""2.2/2.3 — track storms in AIFS forecasts and score them against IBTrACS best tracks.

Tracker: start at the IBTrACS centre at init time; every 6 h take the lowest mean-sea-level pressure within
SEARCH_KM of the previous centre (first-guess = previous centre + last motion). Stop when the minimum is weaker than
STOP_HPA or the box edge is reached.
Scores: great-circle error (km) at leads 24/48/72/120 h, and position error at the reference time (landfall or
closest approach), with the forecast track interpolated linearly in time.
"""
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SEARCH_KM = 250
STOP_HPA = 1010.0
LEADS_H = [24, 48, 72, 120]
DAYS_BEFORE = [5, 3, 1]


def hav(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 6371.0 * 2 * np.arcsin(np.sqrt(a))


def best_track(sid):
    df = pd.read_csv(ROOT / "data" / "ibtracs" / "ibtracs.NA.csv", skiprows=[1], low_memory=False)
    g = df[df.SID == sid].copy()
    for c in ["LAT", "LON", "USA_WIND", "USA_PRES"]:
        g[c] = pd.to_numeric(g[c], errors="coerce")
    g["time"] = pd.to_datetime(g.ISO_TIME)
    return g[["time", "LAT", "LON", "USA_WIND", "USA_PRES", "USA_RECORD"]].reset_index(drop=True)


def bt_at(bt, t):
    """Best-track position at time t (linear interpolation between fixes)."""
    ts = (bt.time - pd.Timestamp(0)).dt.total_seconds().to_numpy()
    x = (pd.Timestamp(t) - pd.Timestamp(0)).total_seconds()
    if x < ts[0] or x > ts[-1]:
        return None
    return float(np.interp(x, ts, bt.LAT)), float(np.interp(x, ts, bt.LON))


def init_for(ref, days):
    t = ref - dt.timedelta(days=days)
    return t.replace(hour=t.hour - t.hour % 6, minute=0, second=0)


def track(npz, lat0, lon0):
    lat, lon, steps = npz["lat"], npz["lon"], npz["steps"]
    msl = npz["msl"] / 100.0  # Pa -> hPa
    LA, LO = np.meshgrid(lat, lon, indexing="ij")
    out = []
    plat, plon, vlat, vlon = lat0, lon0, 0.0, 0.0
    for k, s in enumerate(steps):
        glat, glon = plat + vlat, plon + vlon
        d = hav(glat, glon, LA, LO)
        m = np.where(d <= SEARCH_KM, msl[k], np.inf)
        i, j = np.unravel_index(np.argmin(m), m.shape)
        p = float(msl[k][i, j])
        if not np.isfinite(m[i, j]) or p > STOP_HPA or i in (0, len(lat) - 1) or j in (0, len(lon) - 1):
            break
        nlat, nlon = float(lat[i]), float(lon[j])
        if k > 0:
            vlat, vlon = nlat - plat, nlon - plon
        plat, plon = nlat, nlon
        out.append(dict(step=int(s), lat=nlat, lon=nlon, msl_hpa=round(p, 1)))
    return out


def interp_track(tr, init, t):
    if not tr:
        return None
    hrs = np.array([p["step"] for p in tr], float)
    x = (t - init).total_seconds() / 3600
    if x < hrs[0] or x > hrs[-1]:
        return None
    return float(np.interp(x, hrs, [p["lat"] for p in tr])), float(np.interp(x, hrs, [p["lon"] for p in tr]))


def score(field_dir, field_suffix, source_label):
    storms = json.loads((ROOT / "results" / "storms.json").read_text())
    res = {"source": source_label, "method": __doc__.strip(), "storms": []}
    for s in storms:
        bt = best_track(s["sid"])
        ref = dt.datetime.fromisoformat(s["ref_time"])
        ref_pos = bt_at(bt, ref)
        srec = dict(s, ref_pos=ref_pos, best_track=[dict(time=str(r.time), lat=r.LAT, lon=r.LON, wind_kt=r.USA_WIND,
                                                         pres_hpa=r.USA_PRES) for r in bt.itertuples()], runs=[])
        for days in DAYS_BEFORE:
            init = init_for(ref, days)
            f = Path(field_dir) / f"{init:%Y%m%d%H}_{field_suffix}.npz"
            if not f.exists():
                srec["runs"].append(dict(days_before=days, init=init.isoformat(), error="no forecast file"))
                continue
            npz = np.load(f)
            p0 = bt_at(bt, init)
            tr = track(npz, *p0)
            errs = {}
            for L in LEADS_H:
                t = init + dt.timedelta(hours=L)
                fp, bp = interp_track(tr, init, t), bt_at(bt, t)
                errs[str(L)] = round(float(hav(*fp, *bp)), 1) if fp and bp else None
            fpr = interp_track(tr, init, ref)
            ref_err = round(float(hav(*fpr, *ref_pos)), 1) if fpr else None
            srec["runs"].append(dict(days_before=days, init=init.isoformat(), model=str(npz["model"]), track=tr,
                                     error_km=errs, ref_error_km=ref_err, ref_kind=s["ref_kind"],
                                     forecast_at_ref=fpr))
        res["storms"].append(srec)
    return res


if __name__ == "__main__":
    out = score(sys.argv[1], sys.argv[2], sys.argv[3])
    Path(sys.argv[4]).write_text(json.dumps(out, indent=1, default=str))
    for s in out["storms"]:
        for r in s["runs"]:
            print(s["name"], r["days_before"], r.get("init"), r.get("error_km"), "ref:", r.get("ref_error_km"), r.get("error", ""))
