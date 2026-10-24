"""3.3 — NWS Daily Climate Report (CLI) highs for each station in the window, via the Iowa Environmental Mesonet
archive of NWS CLI products. Cross-checks them against Kalshi's settled values.
Writes data/nws_cli/<station>_<year>.json (cache), results/nws_cli.csv and results/settlement_check.json."""
import json
import sys
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backtest.window import DAYS  # noqa: E402

CACHE = ROOT / "data" / "nws_cli"


def cli_year(station, year):
    f = CACHE / f"{station}_{year}.json"
    if f.exists():
        return json.loads(f.read_text())
    r = requests.get("https://mesonet.agron.iastate.edu/json/cli.py",
                     params={"station": station, "year": year, "fmt": "json"}, timeout=60)
    r.raise_for_status()
    res = r.json()["results"]
    CACHE.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(res))
    return res


def main():
    cities = json.loads((ROOT / "results" / "cities.json").read_text())
    days = {str(d) for d in DAYS}
    rows = []
    for c in cities:
        for r in cli_year(c["station"], DAYS[0].year):
            if r["valid"] in days:
                rows.append(dict(city=c["city"], station=c["station"], date=r["valid"], nws_high=r["high"],
                                 product=r["product"]))
    cli = pd.DataFrame(rows)
    cli.to_csv(ROOT / "results" / "nws_cli.csv", index=False)
    mk = pd.read_csv(ROOT / "results" / "markets.csv")
    kal = mk.groupby(["city", "date"], as_index=False).settled_high.first()
    j = kal.merge(cli, on=["city", "date"], how="left")
    j["match"] = j.settled_high == j.nws_high
    mism = j[~j.match]
    out = dict(compared=int(j.nws_high.notna().sum()), total=len(j), matches=int(j.match.sum()),
               match_rate=round(float(j.match.sum()) / len(j), 4),
               mismatches=mism[["city", "date", "settled_high", "nws_high", "product"]].astype(str).to_dict("records"))
    (ROOT / "results" / "settlement_check.json").write_text(json.dumps(out, indent=1))
    print({k: v for k, v in out.items() if k != "mismatches"})
    print(mism[["city", "date", "settled_high", "nws_high"]].to_string(index=False))


if __name__ == "__main__":
    main()
