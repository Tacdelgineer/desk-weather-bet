"""1.1 CHECK — local AIFS 2 m temperature at Los Angeles (KLAX nearest N320 point) vs NWS observations at KLAX.
usage: python model/sanity_la.py data/aifs_runs/<file>.npz   -> results/aifs_la_sanity.json"""
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import requests

ROOT = Path(__file__).resolve().parents[1]
LAT, LON = 33.93806, -118.38889


def main(path):
    z = np.load(path)
    lat, lon = z["lat"], z["lon"]
    d = np.radians
    k = int(np.argmin(np.arccos(np.clip(np.sin(d(lat)) * np.sin(d(LAT)) + np.cos(d(lat)) * np.cos(d(LAT))
                                        * np.cos(d(lon - LON % 360)), -1, 1))))
    init = dt.datetime.fromisoformat(str(z["init"]))
    obs = requests.get("https://api.weather.gov/stations/KLAX/observations", timeout=30,
                       params={"start": (init - dt.timedelta(hours=1)).isoformat() + "Z"},
                       headers={"User-Agent": "desk-weather-bet (research)"}).json()["features"]
    obs = {o["properties"]["timestamp"][:13]: o["properties"]["temperature"]["value"] for o in obs
           if o["properties"]["temperature"]["value"] is not None}
    rows = []
    for i, s in enumerate(z["steps"]):
        t = init + dt.timedelta(hours=int(s))
        f = float(z["2t"][i, k]) - 273.15
        o = obs.get(t.strftime("%Y-%m-%dT%H"))
        if o is not None:
            rows.append(dict(valid=t.isoformat() + "Z", aifs_C=round(f, 1), nws_obs_C=round(o, 1), diff_C=round(f - o, 1)))
    out = dict(run=Path(path).name, grid_point=[float(lat[k]), float(lon[k])], comparisons=rows)
    (ROOT / "results" / "aifs_la_sanity.json").write_text(json.dumps(out, indent=1))
    for r in rows:
        print(r)


if __name__ == "__main__":
    main(sys.argv[1])
