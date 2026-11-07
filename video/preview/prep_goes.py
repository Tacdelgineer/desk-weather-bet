"""Style preview, shot 1: real GOES-19 band-13 frames of Hurricane MELISSA (data/goes/melissa/*.nc, NOAA) as 1000x1000
JPGs, plus AIFS's 3-days-before forecast track and the IBTrACS best track (results/hurricanes.json) projected into the
same pixels with the GOES fixed-grid equations (GOES-R PUG vol. 4, 7.1.2.8). Writes video/work/goes_melissa/*.jpg and
video/chapters/goes.js. Safe to re-run.  Run: uv run python video/preview/prep_goes.py"""
import datetime as dt
import json
from pathlib import Path

import h5netcdf
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "goes" / "melissa"
OUT = ROOT / "video" / "work" / "goes_melissa"
OUT.mkdir(parents=True, exist_ok=True)
STEP = 2            # every 2nd one-minute frame -> 91 frames
PX = 1000           # 500x500 at 2 km -> 1000x1000


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
    col = (a - x[0]) / (x[1] - x[0])
    row = (b - y[0]) / (y[1] - y[0])
    k = PX / len(x)
    return round(float(col * k), 1), round(float(row * k), 1)


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
            Image.fromarray((img * 255).astype(np.uint8)).resize((PX, PX), Image.BICUBIC).save(jpg, quality=88)
assert len(centres) == 1, f"sector moved during the loop: {centres}"

hur = json.loads((ROOT / "results" / "hurricanes.json").read_text())
st = next(s for s in hur["storms"] if s["name"] == "MELISSA")
run = next(r for r in st["runs"] if r["days_before"] == 3)
init = dt.datetime.fromisoformat(run["init"])
ai = [dict(h=r["step"], t=(init + dt.timedelta(hours=r["step"])).strftime("%Y-%m-%d %H:%M"),
           px=to_px(r["lat"], r["lon"], x, y, p)) for r in run["track"]]
t0, t1 = init, init + dt.timedelta(hours=run["track"][-1]["step"])
bt = [dict(t=b["time"][:16], px=to_px(b["lat"], b["lon"], x, y, p)) for b in st["best_track"]
      if t0 <= dt.datetime.fromisoformat(b["time"]) <= t1]
data = dict(
    storm=st["name"], ref_event=st["ref_event"], ref_time=st["ref_time"], ref_px=to_px(*st["ref_pos"], x, y, p),
    run_init=run["init"], days_before=run["days_before"], ref_error_km=run["ref_error_km"], error_km=run["error_km"],
    ai=ai, best=bt, frames=len(files), frame_times=times, px=PX,
    source="NOAA GOES-19 ABI L2 CMIP, mesoscale sector, band 13 IR (noaa-goes19 on AWS)",
    track_source="results/hurricanes.json: ECMWF real-time AIFS Single (archive) · IBTrACS best track")
(ROOT / "video" / "chapters" / "tx" / "goes.js").write_text("window.GOES = " + json.dumps(data) + ";\n")
import base64
# file:// images would taint the canvas (no frame export), so the frames ship as data URLs
(ROOT / "video" / "chapters" / "tx" / "goes_frames.js").write_text("window.GOES_IMG = " + json.dumps(
    ["data:image/jpeg;base64," + base64.b64encode((OUT / f"{i:03d}.jpg").read_bytes()).decode() for i in range(len(files))]) + ";\n")
print(len(files), "frames", times[0], "->", times[-1], "| ref px", data["ref_px"], "| AI points in frame:",
      sum(0 <= a["px"][0] <= PX and 0 <= a["px"][1] <= PX for a in ai), "/", len(ai))
