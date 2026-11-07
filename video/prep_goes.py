"""Real GOES-19 band-13 frames of one hurricane (data/goes/<storm>/*.nc, NOAA) as JPGs, plus AIFS's N-days-before
forecast track and the IBTrACS best track (results/hurricanes.json) projected into the same pixels with the GOES
fixed-grid equations (GOES-R PUG vol. 4, 7.1.2.8).

  uv run python video/prep_goes.py STORM [STEP PX DAYS_BEFORE]     (default: MELISSA 2 1000 3)

Writes video/work/goes_<storm>_<px>/*.jpg, video/chapters/tx/goes_<storm>.js (window.GOES[storm]) and
video/chapters/tx/goes_<storm>_frames.js (data URLs: file:// images would taint the canvas). Safe to re-run."""
import base64
import datetime as dt
import json
import sys
from pathlib import Path

import h5netcdf
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
STORM = (sys.argv[1] if len(sys.argv) > 1 else "MELISSA").upper()
STEP = int(sys.argv[2]) if len(sys.argv) > 2 else 2
PX = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
DAYS = int(sys.argv[4]) if len(sys.argv) > 4 else 3
SRC = ROOT / "data" / "goes" / STORM.lower()
OUT = ROOT / "video" / "work" / f"goes_{STORM.lower()}_{PX}"
TX = ROOT / "video" / "chapters" / "tx"
OUT.mkdir(parents=True, exist_ok=True)


def grid(h):
    sx, sy = (h.variables[v] for v in ("x", "y"))
    x = sx[:] * float(sx.attrs["scale_factor"]) + float(sx.attrs["add_offset"])
    y = sy[:] * float(sy.attrs["scale_factor"]) + float(sy.attrs["add_offset"])
    a = h.variables["goes_imager_projection"].attrs
    p = {k: a[k] for k in ("semi_major_axis", "semi_minor_axis", "perspective_point_height", "longitude_of_projection_origin")}
    return np.array(x), np.array(y), p


def to_xy(lat, lon, p):
    req, rpol = float(p["semi_major_axis"]), float(p["semi_minor_axis"])
    H = float(p["perspective_point_height"]) + req
    lon0 = np.radians(float(p["longitude_of_projection_origin"]))
    la, lo = np.radians(lat), np.radians(lon)
    e2 = (req ** 2 - rpol ** 2) / req ** 2
    phic = np.arctan(rpol ** 2 / req ** 2 * np.tan(la))
    rc = rpol / np.sqrt(1 - e2 * np.cos(phic) ** 2)
    sx = H - rc * np.cos(phic) * np.cos(lo - lon0)
    sy = -rc * np.cos(phic) * np.sin(lo - lon0)
    sz = rc * np.sin(phic)
    return np.arcsin(-sy / np.sqrt(sx ** 2 + sy ** 2 + sz ** 2)), np.arctan(sz / sx)


def to_px(lat, lon, x, y, p):
    a, b = to_xy(lat, lon, p)
    k = PX / len(x)
    return round(float((a - x[0]) / (x[1] - x[0]) * k), 1), round(float((b - y[0]) / (y[1] - y[0]) * k), 1)


files = sorted(SRC.glob("*.nc"))[::STEP]
times, centres = [], set()
for i, f in enumerate(files):
    s = f.name.split("_s")[1][:13]
    t = dt.datetime.strptime(s[:7], "%Y%j") + dt.timedelta(hours=int(s[7:9]), minutes=int(s[9:11]))
    times.append(t.strftime("%Y-%m-%d %H:%M"))
    with h5netcdf.File(f, "r") as h:
        x, y, p = grid(h)
        centres.add((round(float(x[0]), 6), round(float(y[0]), 6)))
        jpg = OUT / f"{i:03d}.jpg"
        if not jpg.exists():
            var = h.variables["CMI"]
            raw = var[:]
            a = var.attrs
            v = raw.astype(float) * float(a.get("scale_factor", 1.0)) + float(a.get("add_offset", 0.0))
            if "_FillValue" in a:
                v[raw == a["_FillValue"]] = np.nan
            img = np.nan_to_num(np.clip((300 - v) / (300 - 190), 0, 1))   # same stretch as fetch/goes_loop.py
            Image.fromarray((img * 255).astype(np.uint8)).resize((PX, PX), Image.BICUBIC).save(jpg, quality=85)
assert len(centres) == 1, f"sector moved during the loop: {centres}"

hur = json.loads((ROOT / "results" / "hurricanes.json").read_text())
st = next(s for s in hur["storms"] if s["name"] == STORM)
run = next(r for r in st["runs"] if r["days_before"] == DAYS)
init = dt.datetime.fromisoformat(run["init"])
ai = [dict(h=r["step"], px=to_px(r["lat"], r["lon"], x, y, p)) for r in run["track"]]
t0, t1 = init, init + dt.timedelta(hours=run["track"][-1]["step"])
bt = [dict(t=b["time"][:16], px=to_px(b["lat"], b["lon"], x, y, p)) for b in st["best_track"]
      if t0 <= dt.datetime.fromisoformat(b["time"]) <= t1]
data = dict(storm=st["name"], ref_event=st["ref_event"], ref_kind=st["ref_kind"], ref_time=st["ref_time"],
            ref_px=to_px(*st["ref_pos"], x, y, p), run_init=run["init"], days_before=run["days_before"],
            ref_error_km=run["ref_error_km"], error_km=run["error_km"], ai=ai, best=bt, frames=len(files),
            frame_times=times, px=PX)
TX.mkdir(parents=True, exist_ok=True)
(TX / f"goes_{STORM.lower()}.js").write_text(f"(window.GOES = window.GOES || {{}})[{json.dumps(STORM)}] = " + json.dumps(data) + ";\n")
(TX / f"goes_{STORM.lower()}_frames.js").write_text(f"(window.GOES_IMG = window.GOES_IMG || {{}})[{json.dumps(STORM)}] = " + json.dumps(
    ["data:image/jpeg;base64," + base64.b64encode((OUT / f"{i:03d}.jpg").read_bytes()).decode() for i in range(len(files))]) + ";\n")
print(STORM, len(files), "frames", times[0], "->", times[-1], "| ref px", data["ref_px"], "| AI points in frame:",
      sum(0 <= a["px"][0] <= PX and 0 <= a["px"][1] <= PX for a in ai), "/", len(ai))
