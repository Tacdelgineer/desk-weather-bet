"""v1 vs v2 side by side, same TRAIN/TEST split (PAPER MONEY, TEST). v1 = results/v1/ (TRAIN-fit line, tag
rules-locked); v2 = results/ top level (rolling 30-day bias + guards). Copies the v2 files to results/v2/ and writes
results/v1_vs_v2.json + .csv."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"
FILES = ["backtest.json", "backtest_summary.csv", "backtest_bets.csv", "corrections.json", "forecasts.csv",
         "judge.json", "judge_examples.json", "robustness.csv", "robustness.json"]


def load(v):
    d = R / v
    bt, jd = json.loads((d / "backtest.json").read_text()), json.loads((d / "judge.json").read_text())
    rb, co = json.loads((d / "robustness.json").read_text()), json.loads((d / "corrections.json").read_text())
    p = {k: dict(pnl=x["test"]["pnl"], bets=x["test"]["bets"], win_rate=x["test"]["win_rate"],
                 threshold=x["threshold_used"]) for k, x in bt["players"].items() if "test" in x}
    p["aifs_cor_judge"] = dict(pnl=jd["test"]["judge"]["pnl"], bets=jd["test"]["judge"]["bets"],
                               win_rate=jd["test"]["judge"]["win_rate"], threshold=jd["judge_cutoff_train"])
    return dict(players=p, brier_test=bt["accuracy_brier_test"], test_mae_F=co["_overall_test_mae_F"],
                any_robustness_case_profitable=rb["any_case_profitable_on_test"],
                guard_skips_test={k: x.get("test_skipped_by_guard") for k, x in bt["players"].items()})


def main():
    (R / "v2").mkdir(exist_ok=True)
    for f in FILES:
        shutil.copy(R / f, R / "v2" / f)
    out = {"label": "PAPER MONEY", "split": "same TRAIN/TEST split (TEST 2026-08-22 → 2026-10-20)",
           "v1": {"rules_tag": "rules-locked", "correction": "a + b × raw, fit on TRAIN", **load("v1")},
           "v2": {"rules_tag": "rules-locked-v2", "correction": "raw + mean(actual − raw) over the 30 days before the "
                  "run date; guards: |corrected − GFS| ≤ 4 °F, edge ≤ 0.30", **load("v2")},
           "note": "v2 was designed after seeing v1's TEST results, so TEST is no longer unseen for v2; the live "
                   "week is the only truly unseen test (DECISIONS.md)."}
    (R / "v1_vs_v2.json").write_text(json.dumps(out, indent=1))
    rows = ["player,v1_test_pnl,v1_bets,v2_test_pnl,v2_bets"]
    for k in out["v1"]["players"]:
        a, b = out["v1"]["players"][k], out["v2"]["players"][k]
        rows.append(f"{k},{a['pnl']},{a['bets']},{b['pnl']},{b['bets']}")
    (R / "v1_vs_v2.csv").write_text("\n".join(rows) + "\n")
    print("\n".join(rows))
    print("Brier v1", out["v1"]["brier_test"], "\nBrier v2", out["v2"]["brier_test"])
    print("MAE v1", out["v1"]["test_mae_F"], "\nMAE v2", out["v2"]["test_mae_F"])


if __name__ == "__main__":
    main()
