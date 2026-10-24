"""AIFS initial conditions (IFS open data, 0.25°) from the Google Cloud copy of ECMWF open data — only the GRIB
messages AIFS needs, via byte ranges from each file's .index. Writes one GRIB file per time and group:
  data/ifs_grib/<YYYYMMDDHH>/<group>.grib2   group = sfc | sol | pl | wave
Why not earthkit's ecmwf-open-data source: the AWS bucket answered with constant "503 Slow Down" from the DGX
(see DECISIONS.md); this does a few merged range requests per file with short retries.
Safe to re-run: skips groups whose file exists.

usage: python fetch/ifs_inputs.py 2026-06-22T00 [more inits...]   (fetches init and init-6h)
"""
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "ifs_grib"
BASE = "https://storage.googleapis.com/ecmwf-open-data"
GAP = 512 * 1024  # merge byte ranges closer than this into one request
S = requests.Session()

PARAM_SFC = ["10u", "10v", "2d", "2t", "msl", "skt", "sp", "tcw", "lsm", "z", "slor", "sdor", "sd"]
PARAM_SOIL = ["vsw", "sot"]
PARAM_WAVE = ["wmb", "h1012", "h1214", "h1417", "h1721", "h2125", "h2530", "mwd", "cdww", "mwp", "swh"]
PARAM_PL = ["gh", "t", "u", "v", "q"]
LEVELS = [1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100, 50, 10]
SOIL_LEVELS = [1, 2]
GROUPS = {  # group -> (stream dir, index filter)
    "sfc": ("oper", lambda d: d["levtype"] == "sfc" and d["param"] in PARAM_SFC),
    "sol": ("oper", lambda d: d["levtype"] == "sol" and d["param"] in PARAM_SOIL and int(d["levelist"]) in SOIL_LEVELS),
    "pl": ("oper", lambda d: d["levtype"] == "pl" and d["param"] in PARAM_PL and int(d["levelist"]) in LEVELS),
    "wave": ("wave", lambda d: d["param"] in PARAM_WAVE),
}
EXPECT = {"sfc": len(PARAM_SFC), "sol": len(PARAM_SOIL) * len(SOIL_LEVELS), "pl": len(PARAM_PL) * len(LEVELS),
          "wave": len(PARAM_WAVE)}


def get(url, **kw):
    for i in range(8):
        try:
            r = S.get(url, timeout=120, **kw)
            if r.status_code in (429, 500, 502, 503):
                raise requests.HTTPError(str(r.status_code))
            r.raise_for_status()
            return r
        except requests.RequestException:
            time.sleep(min(30, 2 ** i))
    raise RuntimeError(f"failed: {url}")


def url(t, stream):
    return f"{BASE}/{t:%Y%m%d}/{t:%H}z/ifs/0p25/{stream}/{t:%Y%m%d%H}0000-0h-{stream}-fc"


def fetch_time(t):
    d = OUT / f"{t:%Y%m%d%H}"
    todo = [g for g in GROUPS if not (d / f"{g}.grib2").exists()]
    if not todo:
        return "cached"
    d.mkdir(parents=True, exist_ok=True)
    idx = {}
    for g in todo:
        stream, keep = GROUPS[g]
        if stream not in idx:
            idx[stream] = [json.loads(l) for l in get(url(t, stream) + ".index").text.splitlines() if l.startswith("{")]
        msgs = sorted({(m["_offset"], m["_length"]) for m in idx[stream] if keep(m)})
        if len(msgs) != EXPECT[g]:
            raise SystemExit(f"{t:%Y-%m-%dT%H} {g}: {len(msgs)} messages in index, expected {EXPECT[g]}")
        blocks, cur = [], None  # merge nearby ranges: [start, end) + member messages
        for off, ln in msgs:
            if cur and off - cur[1] <= GAP:
                cur[1] = max(cur[1], off + ln)
                cur[2].append((off, ln))
            else:
                cur = [off, off + ln, [(off, ln)]]
                blocks.append(cur)
        parts = []
        for a, b, members in blocks:
            data = get(url(t, stream) + ".grib2", headers={"Range": f"bytes={a}-{b - 1}"}).content
            assert len(data) == b - a, (len(data), b - a)
            parts += [data[off - a: off - a + ln] for off, ln in members]
        assert all(p[:4] == b"GRIB" and p[-4:] == b"7777" for p in parts)
        tmp = d / f"{g}.grib2.tmp"
        tmp.write_bytes(b"".join(parts))
        os.replace(tmp, d / f"{g}.grib2")
    return "ok"


def fetch_init(init):
    return [fetch_time(t) for t in (init - dt.timedelta(hours=6), init)]


if __name__ == "__main__":
    for a in sys.argv[1:]:
        init = dt.datetime.strptime(a, "%Y-%m-%dT%H")
        t0 = time.time()
        print(a, fetch_init(init), f"{time.time() - t0:.0f}s", flush=True)
