"""v2 dry run vs what the v1 line would have said on the same raw highs (video/JOURNAL.md 2026-10-25).
Reads logs/live/2026-10-24_picks.json and RULES.json at tag rules-locked; writes results/dryrun_v1_vs_v2.json."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = "logs/live/2026-10-24_picks.json"


def main():
    r = json.loads((ROOT / LOG).read_text())
    v1 = json.loads(subprocess.run(["git", "show", "rules-locked:RULES.json"], cwd=ROOT, capture_output=True, text=True,
                                   check=True).stdout)["corrections"]
    out = {"source": LOG, "market_day": r["market_day"], "stations": {}}
    for st, h in r["highs"].items():
        m1 = v1[st]["a"] + v1[st]["b"] * h["raw_high_F"]
        out["stations"][st] = dict(raw_high_F=h["raw_high_F"], gfs_F=h["gfs_F"], v1_corrected_F=round(m1, 2),
                                   v1_minus_gfs_F=round(m1 - h["gfs_F"], 2), v2_corrected_F=h["mu"],
                                   v2_minus_gfs_F=round(h["mu"] - h["gfs_F"], 2), v2_bias_30d=h["bias_30d"],
                                   v2_sigma_30d=h["sigma_30d"], v2_days_30d=h["days_30d"])
    out["v2_picks"] = [{k: p[k] for k in ("ticker", "side", "price", "edge", "p_side", "p_bet", "mu", "gfs_F")}
                       for p in r["picks"]]
    out["v2_guarded"] = r["guarded"]
    (ROOT / "results" / "dryrun_v1_vs_v2.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out["stations"]["KPHX"]))


if __name__ == "__main__":
    main()
