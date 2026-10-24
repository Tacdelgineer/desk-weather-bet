"""Run AIFS Single v2 on CPU from ECMWF open data, following the model card's demo notebook.

usage: uv --project model/aifs run python model/run_aifs.py --date 2026-10-23T00 --lead 240 [--source ecmwf|aws]
Writes data/aifs_runs/<YYYYMMDDHH>_<lead>h.npz with 2t/msl/10u/10v (+ any max-temp field) per 6-h step on the N320 grid.
Skips if the output already exists (safe to re-run).
"""
import argparse
import datetime as dt
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

os.environ.setdefault("TQDM_DISABLE", "1")
ROOT = Path(__file__).resolve().parents[1]
try:
    import flash_attn  # noqa: F401  (real CUDA build, e.g. on a GPU box)
except ImportError:
    sys.path.insert(0, str(ROOT / "model" / "cpu_flash"))  # exact CPU stand-in, see DECISIONS.md
INPUTS = ROOT / "data" / "aifs_inputs"
OUT = ROOT / "data" / "aifs_runs"
CKPT = ROOT / "data" / "aifs" / "aifs-single-mse-2.0.ckpt"
LSM = ROOT / "data" / "aifs" / "lsm.grib"

PARAM_SFC = ["10u", "10v", "2d", "2t", "msl", "skt", "sp", "tcw", "lsm", "z", "slor", "sdor", "sd"]
PARAM_SOIL = ["vsw", "sot"]
PARAM_WAVE = ["wmb", "h1012", "h1214", "h1417", "h1721", "h2125", "h2530", "mwd", "cdww", "mwp", "swh"]
PARAM_PL = ["gh", "t", "u", "v", "q"]
LEVELS = [1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100, 50, 10]
SOIL_LEVELS = [1, 2]
KEEP = ["2t", "msl", "10u", "10v", "mx2t", "mx2t6", "mn2t", "mn2t6", "tp"]


def get_open_data(date, source, param, levelist=(), **kw):
    import earthkit.data as ekd
    import earthkit.regrid as ekr
    fields = defaultdict(list)
    for d in [date - dt.timedelta(hours=6), date]:
        data = ekd.from_source("ecmwf-open-data", date=d, param=param, levelist=list(levelist), source=source, **kw)
        for f in data:
            v = f.to_numpy()
            assert v.shape == (721, 1440), v.shape
            v = np.roll(v, -v.shape[1] // 2, axis=1)
            v = ekr.interpolate(v, {"grid": (0.25, 0.25)}, {"grid": "N320"})
            name = f"{f.metadata('param')}_{f.metadata('levelist')}" if levelist else f.metadata("param")
            fields[name].append(v)
    return {k: np.stack(v) for k, v in fields.items()}


def build_input(date, source):
    import earthkit.data as ekd
    fields = {}
    fields.update(get_open_data(date, source, PARAM_SFC, levtype="sfc"))
    fields.update(get_open_data(date, source, PARAM_WAVE, stream="wave"))
    soil = get_open_data(date, source, PARAM_SOIL, levelist=SOIL_LEVELS)
    fields.update(get_open_data(date, source, PARAM_PL, levelist=LEVELS))
    missing = [p for p in PARAM_SFC + PARAM_WAVE if p not in fields]
    missing += [f"{p}_{l}" for p in PARAM_PL for l in LEVELS if f"{p}_{l}" not in fields]
    missing += [f"{p}_{l}" for p in PARAM_SOIL for l in SOIL_LEVELS if f"{p}_{l}" not in soil]
    if missing:
        raise SystemExit(f"missing input params: {missing}")
    mwd = np.deg2rad(fields.pop("mwd"))
    fields["cos_mwd"], fields["sin_mwd"] = np.cos(mwd), np.sin(mwd)
    for k, v in {"sot_1": "stl1", "sot_2": "stl2", "vsw_1": "swvl1", "vsw_2": "swvl2"}.items():
        fields[v] = soil[k]
    fields.pop("q_10", None)
    fields.pop("q_50", None)
    mask = np.equal(ekd.from_source("file", str(LSM))[0].to_numpy(flatten=True), 0)
    for p in ["sd", "swvl1", "swvl2"]:
        fields[p][:, mask] = np.nan
    for lev in LEVELS:
        fields[f"z_{lev}"] = fields.pop(f"gh_{lev}") * 9.80665
    return fields


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True, help="init time, e.g. 2026-10-23T00")
    ap.add_argument("--lead", type=int, default=240, help="hours")
    ap.add_argument("--source", default="ecmwf", help="ecmwf (recent days) or aws (archive)")
    a = ap.parse_args()
    date = dt.datetime.strptime(a.date, "%Y-%m-%dT%H")
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"{date:%Y%m%d%H}_{a.lead}h.npz"
    if out.exists():
        print(f"exists, skipping: {out.name}")
        return
    import earthkit.data as ekd
    ekd.config.set({"cache-policy": "temporary"})
    t0 = time.time()
    cache = INPUTS / f"{date:%Y%m%d%H}.npz"
    if cache.exists():
        fields = dict(np.load(cache))
    else:
        fields = build_input(date, a.source)
        INPUTS.mkdir(parents=True, exist_ok=True)
        np.savez(cache.with_suffix(".tmp.npz"), **fields)
        os.replace(cache.with_suffix(".tmp.npz"), cache)
    t_in = time.time() - t0
    print(f"input ready in {t_in:.0f}s", flush=True)

    import faulthandler
    import torch
    torch.set_num_threads(int(os.environ.get("AIFS_THREADS", os.cpu_count() or 4)))
    if os.environ.get("AIFS_STACKS"):
        faulthandler.dump_traceback_later(int(os.environ["AIFS_STACKS"]), repeat=True)
    from anemoi.inference.runners.simple import SimpleRunner
    runner = SimpleRunner(str(CKPT), device="cpu")
    keep = defaultdict(list)
    steps = []
    t1 = time.time()
    for state in runner.run(input_state=dict(date=date, fields=fields), lead_time=a.lead):
        steps.append(int((state["date"] - date).total_seconds() // 3600))
        for k in KEEP:
            if k in state["fields"]:
                keep[k].append(np.asarray(state["fields"][k], dtype=np.float32))
        print(f"step +{steps[-1]}h  {time.time() - t1:.0f}s", flush=True)
    t_run = time.time() - t1
    lat, lon = state["latitudes"], state["longitudes"]
    tmp = out.with_suffix(".tmp.npz")
    np.savez_compressed(tmp, steps=np.array(steps), lat=lat.astype(np.float32), lon=lon.astype(np.float32),
                        init=np.array(date.isoformat()), t_input=t_in, t_run=t_run,
                        **{k: np.stack(v) for k, v in keep.items()})
    os.replace(tmp, out)
    print(f"saved {out.name}: fields={list(keep)} steps={len(steps)} run={t_run:.0f}s")


if __name__ == "__main__":
    sys.exit(main())
