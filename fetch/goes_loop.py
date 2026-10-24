"""2.4 — real NOAA GOES-19 ABI imagery for the cold open: Level-2 Cloud & Moisture Imagery, mesoscale sector that
was tracking each storm, band 13 (clean longwave IR), one frame per minute for the 3 h before the storm's reference
time. Frames are rendered straight from the data (grayscale, cold cloud tops bright), with a small source label.
Downloads: data/goes/<storm>/ ; frames + mp4: results/final_footage/goes_<storm>.mp4 (git-ignored).
Source: NOAA Open Data Dissemination (noaa-goes19 bucket on AWS). Safe to re-run."""
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "model"))
BUCKET = "https://noaa-goes19.s3.amazonaws.com"
HOURS_BEFORE = 3
BAND = 13


def keys(prefix):
    out, token = [], None
    while True:
        p = {"list-type": 2, "prefix": prefix}
        if token:
            p["continuation-token"] = token
        t = requests.get(BUCKET, params=p, timeout=60).text
        import re
        out += re.findall(r"<Key>([^<]+)</Key>", t)
        m = re.search(r"<NextContinuationToken>([^<]+)</NextContinuationToken>", t)
        if not m:
            return out
        token = m.group(1)


def start_time(key):
    s = key.split("_s")[1][:13]  # YYYYJJJHHMMSS
    return dt.datetime.strptime(s[:7], "%Y%j") + dt.timedelta(hours=int(s[7:9]), minutes=int(s[9:11]), seconds=int(s[11:13]))


def pick_sector(t, lat, lon):
    import h5netcdf
    for m in (1, 2):
        ks = [k for k in keys(f"ABI-L2-CMIPM/{t:%Y}/{t:%j}/{t:%H}/OR_ABI-L2-CMIPM{m}-M6C{BAND:02d}") if k]
        if not ks:
            continue
        f = ROOT / "data" / "goes" / "probe.nc"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(requests.get(f"{BUCKET}/{ks[0]}", timeout=60).content)
        with h5netcdf.File(f, "r") as h:
            g = h.variables["geospatial_lat_lon_extent"].attrs
            clat, clon = float(g["geospatial_lat_center"]), float(g["geospatial_lon_center"])
        if abs(clat - lat) < 6 and abs(clon - lon) < 6:
            return m
    return None


def render(nc, png, label):
    import h5netcdf
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    with h5netcdf.File(nc, "r") as h:
        var = h.variables["CMI"]
        raw = var[:]
        a = var.attrs
        v = raw.astype(float) * float(a.get("scale_factor", 1.0)) + float(a.get("add_offset", 0.0))  # brightness temp, K
        if "_FillValue" in a:
            v[raw == a["_FillValue"]] = np.nan
    img = np.clip((300 - v) / (300 - 190), 0, 1)  # 190 K (cold tops) -> white, 300 K -> black
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100, facecolor="black")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor("black")
    ax.imshow(img, cmap="gray", vmin=0, vmax=1, extent=None, aspect="equal")
    ax.axis("off")
    fig.text(0.985, 0.02, label, color="white", ha="right", va="bottom", fontsize=16, family="monospace", alpha=0.85)
    fig.savefig(png, facecolor="black")
    plt.close(fig)


def main():
    from hurricanes import best_track, bt_at
    storms = json.loads((ROOT / "results" / "storms.json").read_text())
    outdir = ROOT / "results" / "final_footage"
    outdir.mkdir(parents=True, exist_ok=True)
    made = []
    for s in storms:
        mp4 = outdir / f"goes_{s['name'].lower()}.mp4"
        if mp4.exists():
            made.append(mp4.name)
            continue
        ref = dt.datetime.fromisoformat(s["ref_time"])
        bt = best_track(s["sid"])
        lat, lon = bt_at(bt, ref)
        sector = pick_sector(ref, lat, lon)
        if not sector:
            print(s["name"], "no mesoscale sector on the storm; skipped")
            continue
        d = ROOT / "data" / "goes" / s["name"].lower()
        fr = d / "frames"
        fr.mkdir(parents=True, exist_ok=True)
        t0 = ref - dt.timedelta(hours=HOURS_BEFORE)
        ks = []
        for h in range(HOURS_BEFORE + 1):
            t = t0 + dt.timedelta(hours=h)
            ks += keys(f"ABI-L2-CMIPM/{t:%Y}/{t:%j}/{t:%H}/OR_ABI-L2-CMIPM{sector}-M6C{BAND:02d}")
        ks = sorted(k for k in ks if t0 <= start_time(k) <= ref)
        for i, k in enumerate(ks):
            nc = d / Path(k).name
            if not nc.exists():
                nc.write_bytes(requests.get(f"{BUCKET}/{k}", timeout=60).content)
            png = fr / f"{i:04d}.png"
            if not png.exists():
                render(nc, png, f"NOAA GOES-19 ABI · band 13 IR · {start_time(k):%Y-%m-%d %H:%M} UTC")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30", "-i", str(fr / "%04d.png"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", str(mp4)], check=True)
        print(s["name"], f"sector M{sector}", len(ks), "frames ->", mp4.name)
        made.append(mp4.name)
    (ROOT / "results" / "goes_loops.json").write_text(json.dumps(dict(files=made, band=BAND, source=BUCKET,
                                                                        hours_before_ref=HOURS_BEFORE), indent=1))


if __name__ == "__main__":
    main()
