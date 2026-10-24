"""Fetch ECMWF's archived real-time AIFS Single forecasts (open data, AWS bucket ecmwf-forecasts) — only the
fields we need, via byte ranges from each step's .index file.

  points mode : 2t at each city station's nearest 0.25° grid point -> data/aifs_archive/points/<init>.json
  field mode  : msl/10u/10v over a lat/lon box (hurricanes)         -> data/aifs_archive/fields/<init>_<box>.npz

Run with the model env (needs eccodes): uv --project model/aifs run python fetch/aifs_archive.py ...
Safe to re-run: skips outputs that exist.
"""
import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "aifs_archive"
BUCKET = "https://ecmwf-forecasts.s3.eu-central-1.amazonaws.com"
S = requests.Session()


def model_dir(init):
    # 'aifs-single' since 2025-02-25 (operational); before that the experimental stream was 'aifs'
    return "aifs-single" if init >= dt.datetime(2025, 2, 25) else "aifs"


def step_url(init, step):
    return f"{BUCKET}/{init:%Y%m%d}/{init:%H}z/{model_dir(init)}/0p25/oper/{init:%Y%m%d%H}0000-{step}h-oper-fc"


def get(url, **kw):
    for i in range(5):
        try:
            r = S.get(url, timeout=60, **kw)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r
        except requests.RequestException:
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"failed: {url}")


def fetch_fields(init, step, params):
    """Return {param: 721x1440 array (lat 90..-90, lon -180..179.75)} for surface params."""
    import eccodes
    base = step_url(init, step)
    idx = get(base + ".index")
    if idx is None:
        return None
    want = {}
    for line in idx.text.splitlines():
        d = json.loads(line)
        if d.get("levtype") == "sfc" and d["param"] in params:
            want[d["param"]] = (d["_offset"], d["_offset"] + d["_length"] - 1)
    out = {}
    for p, (a, b) in want.items():
        msg = get(base + ".grib2", headers={"Range": f"bytes={a}-{b}"}).content
        h = eccodes.codes_new_from_message(msg)
        try:
            ni, nj = eccodes.codes_get(h, "Ni"), eccodes.codes_get(h, "Nj")
            lon0 = eccodes.codes_get(h, "longitudeOfFirstGridPointInDegrees")
            v = eccodes.codes_get_values(h).reshape(nj, ni).astype(np.float32)
        finally:
            eccodes.codes_release(h)
        if abs(lon0) < 1e-6:  # grid starts at 0°: 0..359.75 -> -180..179.75 (open data normally starts at 180° = -180°)
            v = np.roll(v, -ni // 2, axis=1)
        out[p] = v
    return out


def grid_index(lat, lon):
    i = int(round((90 - lat) / 0.25))
    j = int(round((((lon + 180) % 360) - 180 + 180) / 0.25)) % 1440
    return i, j


def points(init, steps):
    f = OUT / "points" / f"{init:%Y%m%d%H}.json"
    if f.exists():
        return "cached"
    cities = json.loads((ROOT / "results" / "cities.json").read_text())
    res = {"init": init.isoformat(), "model": model_dir(init), "steps": [], "grid": {}, "t2m_K": {}}
    for c in cities:
        i, j = grid_index(c["lat"], c["lon"])
        res["grid"][c["station"]] = [90 - i * 0.25, -180 + j * 0.25]
        res["t2m_K"][c["station"]] = []
    for s in steps:
        flds = fetch_fields(init, s, {"2t"})
        if not flds:
            return f"missing step {s}"
        res["steps"].append(s)
        for c in cities:
            i, j = grid_index(c["lat"], c["lon"])
            res["t2m_K"][c["station"]].append(round(float(flds["2t"][i, j]), 3))
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(res))
    return "ok"


def field(init, steps, box, params=("msl", "10u", "10v")):
    """box = (lat_min, lat_max, lon_min, lon_max)."""
    name = "_".join(str(int(x)) for x in box)
    f = OUT / "fields" / f"{init:%Y%m%d%H}_{name}.npz"
    if f.exists():
        return "cached"
    la0, la1, lo0, lo1 = box
    i0, i1 = int((90 - la1) / 0.25), int((90 - la0) / 0.25) + 1
    j0, j1 = int((lo0 + 180) / 0.25), int((lo1 + 180) / 0.25) + 1
    data = {p: [] for p in params}
    got = []
    for s in steps:
        flds = fetch_fields(init, s, set(params))
        if not flds:
            break  # keep what we have (some archives stop early)
        got.append(s)
        for p in params:
            data[p].append(flds[p][i0:i1, j0:j1])
    if not got:
        return "missing"
    f.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(f, steps=np.array(got), lat=90 - np.arange(i0, i1) * 0.25, lon=-180 + np.arange(j0, j1) * 0.25,
                        model=model_dir(init), **{p: np.stack(v) for p, v in data.items()})
    return "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["points", "field"])
    ap.add_argument("--init", required=True, help="YYYY-MM-DDTHH")
    ap.add_argument("--steps", default="24-60", help="a-b (every 6 h) or comma list")
    ap.add_argument("--box", default="5,45,-100,-50")
    a = ap.parse_args()
    init = dt.datetime.strptime(a.init, "%Y-%m-%dT%H")
    if "-" in a.steps and "," not in a.steps:
        lo, hi = map(int, a.steps.split("-"))
        steps = list(range(lo, hi + 1, 6))
    else:
        steps = [int(x) for x in a.steps.split(",")]
    if a.mode == "points":
        print(a.init, points(init, steps))
    else:
        print(a.init, field(init, steps, tuple(float(x) for x in a.box.split(","))))


if __name__ == "__main__":
    sys.exit(main())
