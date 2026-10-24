"""2.2 (local) — turn our own AIFS run (N320 grid) into the same 0.25° lat/lon box file the tracker reads for the archive:
  data/aifs_runs/<init>_<lead>h.npz (+ step 0 from data/aifs_inputs/<init>.npz) -> data/aifs_local/fields/<init>_<box>.npz
Regridding N320 -> 0.25° uses earthkit-regrid (the same library the input step uses the other way round).

usage (model env): python model/local_fields.py 2026-10-05T00 [--lead 144] [--box 5,50,-100,-30]
Safe to re-run: skips outputs that exist.
"""
import argparse
import datetime as dt
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PARAMS = ("msl", "10u", "10v")


def to_box(v, i0, i1, j0, j1):
    import earthkit.regrid as ekr
    g = ekr.interpolate(np.asarray(v, dtype=np.float64), {"grid": "N320"}, {"grid": (0.25, 0.25)})  # 721x1440, lon 0..359.75
    g = np.roll(g.reshape(721, 1440), 720, axis=1)  # -> lon -180..179.75, like the archive files
    return g[i0:i1, j0:j1].astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("init")
    ap.add_argument("--lead", type=int, default=144)
    ap.add_argument("--box", default="5,50,-100,-30")
    a = ap.parse_args()
    init = dt.datetime.strptime(a.init, "%Y-%m-%dT%H")
    box = tuple(float(x) for x in a.box.split(","))
    out = ROOT / "data" / "aifs_local" / "fields" / f"{init:%Y%m%d%H}_{'_'.join(str(int(x)) for x in box)}.npz"
    if out.exists():
        print("exists, skipping:", out.name)
        return
    la0, la1, lo0, lo1 = box
    i0, i1 = int((90 - la1) / 0.25), int((90 - la0) / 0.25) + 1
    j0, j1 = int((lo0 + 180) / 0.25), int((lo1 + 180) / 0.25) + 1
    run = np.load(ROOT / "data" / "aifs_runs" / f"{init:%Y%m%d%H}_{a.lead}h.npz")
    inp = np.load(ROOT / "data" / "aifs_inputs" / f"{init:%Y%m%d%H}.npz")
    data = {p: [to_box(inp[p][-1], i0, i1, j0, j1)] + [to_box(v, i0, i1, j0, j1) for v in run[p]] for p in PARAMS}
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, steps=np.concatenate([[0], run["steps"]]), lat=90 - np.arange(i0, i1) * 0.25,
                        lon=-180 + np.arange(j0, j1) * 0.25, model="aifs-single-v2 local (DGX)",
                        **{p: np.stack(v) for p, v in data.items()})
    print("saved", out.name)


if __name__ == "__main__":
    main()
