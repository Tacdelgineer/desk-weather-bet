"""5.4 — rerun the backtest with fees x1.5 and the TRAIN threshold shifted down/up; does the conclusion hold?"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backtest.sim import run  # noqa: E402

CASES = [("base", 1.0, 0.0), ("fees x1.5", 1.5, 0.0), ("threshold -0.02", 1.0, -0.02), ("threshold +0.02", 1.0, 0.02),
         ("threshold +0.05", 1.0, 0.05), ("fees x1.5, threshold +0.05", 1.5, 0.05)]


def main():
    rows = []
    for name, fm, sh in CASES:
        res = run(fee_mult=fm, th_shift=sh)[0]
        for pl, r in res.items():
            t = r.get("test", {})
            rows.append(dict(case=name, player=pl, threshold=r.get("threshold_used"), test_pnl=t.get("pnl"),
                             bets=t.get("bets"), roi=t.get("roi")))
    df = pd.DataFrame(rows)
    df.to_csv(ROOT / "results" / "robustness.csv", index=False)
    any_profit = bool((df.test_pnl > 0).any())
    best = df.loc[df.groupby("case").test_pnl.idxmax()][["case", "player", "test_pnl"]]
    out = dict(table=rows, any_case_profitable_on_test=any_profit,
               conclusion=("No player makes money on TEST in any case" if not any_profit
                           else "At least one case is profitable on TEST — see table"),
               best_player_per_case=best.to_dict("records"))
    (ROOT / "results" / "robustness.json").write_text(json.dumps(out, indent=1))
    print(df.pivot(index="case", columns="player", values="test_pnl").to_string())
    print(out["conclusion"])


if __name__ == "__main__":
    main()
