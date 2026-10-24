"""3.1 — pick the 6 US daily-high series with the most 30-day volume, read each market's rules for its
settlement station, and look up the station's coordinates from api.weather.gov.
Writes results/cities.json. Safe to re-run (skips if the file exists; --force to redo)."""
import json
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bot.kalshi import Kalshi  # noqa: E402

OUT = ROOT / "results" / "cities.json"
# CLI product code -> ICAO station (CLIxxx is the NWS Daily Climate Report for station Kxxx; NYC = Central Park)
CLI_TO_ICAO = {"CLINYC": "KNYC"}


def main():
    if OUT.exists() and "--force" not in sys.argv:
        print(f"exists: {OUT.relative_to(ROOT)}")
        return
    k = Kalshi(auth=False)
    series = [s for s in k.get("/series", category="Climate and Weather")["series"]
              if s["ticker"].startswith("KXHIGH") and s.get("frequency") == "daily"]
    now = int(time.time())
    rows = []
    for s in series:
        ms = list(k.paged("/markets", "markets", series_ticker=s["ticker"], min_close_ts=now - 30 * 86400, max_close_ts=now))
        if not ms:
            continue
        m = re.search(r"recorded at (.*?) \((CLI\w+)\) for", ms[0]["rules_primary"])
        if not m:
            continue  # non-US series name a different source/station format
        vol = sum(float(x.get("volume_fp") or 0) for x in ms)
        rows.append(dict(series=s["ticker"], city=m.group(1), cli=m.group(2), volume_30d=round(vol),
                         source=s["settlement_sources"][0]["name"], rules_example=ms[0]["rules_primary"]))
    rows.sort(key=lambda r: -r["volume_30d"])
    out = []
    for r in rows[:6]:
        icao = CLI_TO_ICAO.get(r["cli"], "K" + r["cli"][3:])
        st = requests.get(f"https://api.weather.gov/stations/{icao}", timeout=30,
                          headers={"User-Agent": "desk-weather-bet (research)"}).json()
        lon, lat = st["geometry"]["coordinates"][:2]
        r.update(station=icao, station_name=st["properties"]["name"], lat=lat, lon=lon,
                 elevation_m=st["properties"]["elevation"]["value"], tz=st["properties"]["timeZone"],
                 cli_wfo=None)
        out.append(r)
    OUT.write_text(json.dumps(out, indent=1))
    for r in out:
        print(r["city"], r["station"], r["series"], r["volume_30d"], r["lat"], r["lon"], r["tz"])


if __name__ == "__main__":
    main()
