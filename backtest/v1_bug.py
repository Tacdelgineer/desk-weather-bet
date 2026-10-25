"""v1 bug evidence — the by-hand DRY_RUN for 2026-10-24 (logs/live/2026-10-23_picks.json) used the v1 linear station
correction (RULES.json at tag rules-locked, fit on summer TRAIN days) far outside the raw highs it was fit on.
Collects, per station: TRAIN raw-high range, the v1 fit, the Oct 24 raw and v1-corrected highs, GFS (D-1 00Z run),
the NWS point forecast max and the preliminary NWS climate-report high. Also writes the TRAIN scatter (raw vs actual)
for the video. Inputs are the files named in each field. Writes results/evidence/v1-bug/summary.json."""
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fetch.gfs import day_max, run_series  # noqa: E402

EV = ROOT / "results" / "evidence" / "v1-bug"
DAY = dt.date(2026, 10, 24)
PFM = {"KPHX": ("nws_pfm_PSR_2026-10-23.txt", "Phoenix-Maricopa AZ"), "KMIA": ("nws_pfm_MFL_2026-10-23.txt",
                                                                              "Miami-Miami Dade FL")}


def pfm_max(fname, point):
    """Sat 10/24 max at one PFM point, for every issuance in the archive file -> {issuance: max °F}.
    Sat columns = the local-hour columns between the first and second midnight wrap after the Fri start."""
    out = {}
    for block in (EV / fname).read_text().split("\x01"):
        hdr = re.search(r"^FOUS\d\d \w{4} \d{6}", block, re.M)
        if not hdr or f"\n{point}\n" not in block:
            continue
        lines = block.split(f"\n{point}\n", 1)[1].splitlines()
        local = next(l for l in lines if re.match(r"^[A-Z]{3} 3hrly", l) and not l.startswith("UTC"))
        hours = [(m.start(), int(m.group())) for m in re.finditer(r"\d\d", local)]
        wraps = [hours[i][0] for i in range(1, len(hours)) if hours[i][1] < hours[i - 1][1]]
        a, b = wraps[0], (wraps[1] if len(wraps) > 1 else 10 ** 6)
        mm = next(l for l in lines if l.startswith(("Min/Max", "Max/Min")))
        vals = [int(m.group()) for m in re.finditer(r"\d+", mm) if a <= m.start() < b]
        out[f"{hdr.group()} ({lines[1].strip()})"] = max(vals) if vals else None
    return out


def main():
    rules_v1 = json.loads(subprocess.run(["git", "show", "rules-locked:RULES.json"], cwd=ROOT, capture_output=True,
                                         text=True, check=True).stdout)
    picks = json.loads((EV / "2026-10-23_picks.json").read_text())
    fc = pd.read_csv(ROOT / "results" / "forecasts.csv")
    tr = fc[fc.split == "TRAIN"]
    cities = {c["station"]: c for c in json.loads((ROOT / "results" / "cities.json").read_text())}
    out = {"_sources": {"picks": "results/evidence/v1-bug/2026-10-23_picks.json",
                        "fit": "RULES.json at tag rules-locked (= results/corrections.json aifs_high a, b, sigma)",
                        "train_range": "results/forecasts.csv (TRAIN rows, aifs_raw_mu)",
                        "gfs": "Open-Meteo single-runs API, gfs_global run 2026-10-23T00, max over the LST day",
                        "nws_forecast": "NWS Point Forecast Matrices PFMPSR/PFMMFL (IEM AFOS archive), saved here",
                        "nws_prelim_high": "NWS CLI via IEM json/cli.py, saved here (preliminary: same-day issue)"},
           "market_day": str(DAY), "stations": {}}
    for st, h in picks["highs"].items():
        c = rules_v1["corrections"][st]
        g = tr[tr.station == st]
        gfs, _ = day_max(run_series(cities[st], dt.datetime(2026, 10, 23)), DAY, cities[st]["tz"])
        row = dict(raw_high_F=h["raw_high_F"], v1_a=round(c["a"], 3), v1_b=round(c["b"], 4),
                   v1_sigma=round(c["sigma"], 3), v1_corrected_F=round(c["a"] + c["b"] * h["raw_high_F"], 2),
                   train_raw_min_F=round(float(g.aifs_raw_mu.min()), 2), train_raw_max_F=round(float(g.aifs_raw_mu.max()), 2),
                   outside_train_range=bool(h["raw_high_F"] < g.aifs_raw_mu.min() or h["raw_high_F"] > g.aifs_raw_mu.max()),
                   gfs_F=gfs)
        row["v1_minus_gfs_F"] = round(row["v1_corrected_F"] - gfs, 2)
        if st in PFM:
            row["nws_pfm_max_F"] = pfm_max(*PFM[st])
        f = EV / f"nws_cli_prelim_{st}_2026-10-24.json"
        if f.exists():
            r = json.loads(f.read_text())[0]
            row["nws_cli_prelim_high_F"], row["nws_cli_product"] = r["high"], r["product"]
        row["picks"] = [dict(ticker=p["ticker"], side=p["side"], price=p["price"], edge=p["edge"], p_side=p["p_side"],
                             bracket=p["yes_sub_title"]) for p in picks["picks"] if p["station"] == st]
        out["stations"][st] = row
    out["scatter_train"] = {st: [[round(float(r.aifs_raw_mu), 2), float(r.actual), r.date] for r in g.itertuples()]
                            for st, g in tr.groupby("station")}
    (EV / "summary.json").write_text(json.dumps(out, indent=1))
    for st, r in out["stations"].items():
        print(st, {k: v for k, v in r.items() if k not in ("picks",)})


if __name__ == "__main__":
    main()
