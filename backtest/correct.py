"""4.3 — station correction, fitted on TRAIN only: actual_high ≈ a + b × model_high, per station and model.
Spread (sigma) = std of TRAIN residuals. Raw forecasts get sigma = TRAIN RMSE around the raw value (no bias fix).
Saves results/corrections.json (coefficients + before/after error in °F on TRAIN and TEST) and
results/forecasts.csv (one row per city/date with every player's centre and sigma)."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backtest.window import assert_train_only, is_test  # noqa: E402


def load():
    mk = pd.read_csv(ROOT / "results" / "markets.csv")
    actual = mk.groupby(["city", "station", "date"], as_index=False).settled_high.first()
    a = pd.read_csv(ROOT / "results" / "aifs_highs.csv")[["station", "date", "aifs_high"]]
    g = pd.read_csv(ROOT / "results" / "gfs_highs.csv")[["station", "date", "gfs_high"]]
    df = actual.merge(a, on=["station", "date"], how="left").merge(g, on=["station", "date"], how="left")
    df["split"] = np.where(df.date.map(is_test), "TEST", "TRAIN")
    return df


def fit(train, col):
    assert_train_only(train.date)
    x, y = train[col].to_numpy(float), train.settled_high.to_numpy(float)
    b, a = np.polyfit(x, y, 1)
    resid = y - (a + b * x)
    return dict(a=float(a), b=float(b), sigma=float(resid.std(ddof=2)),
                raw_rmse=float(np.sqrt(np.mean((y - x) ** 2))), n_train=int(len(x)))


def mae(y, f):
    return round(float(np.mean(np.abs(y - f))), 3)


def main():
    df = load().dropna(subset=["settled_high", "aifs_high", "gfs_high"])
    out, rows = {}, []
    for st, g in df.groupby("station"):
        tr, te = g[g.split == "TRAIN"], g[g.split == "TEST"]
        out[st] = {}
        for col in ["aifs_high", "gfs_high"]:
            p = fit(tr, col)
            for name, part in [("train", tr), ("test", te)]:
                y, x = part.settled_high.to_numpy(float), part[col].to_numpy(float)
                p[f"mae_raw_{name}"] = mae(y, x)
                p[f"mae_corrected_{name}"] = mae(y, p["a"] + p["b"] * x)
                p[f"bias_raw_{name}"] = round(float(np.mean(x - y)), 3)
            out[st][col] = p
        for r in g.itertuples():
            pa, pg = out[st]["aifs_high"], out[st]["gfs_high"]
            rows.append(dict(city=r.city, station=st, date=r.date, split=r.split, actual=r.settled_high,
                             gfs_mu=r.gfs_high, gfs_sigma=pg["raw_rmse"],
                             aifs_raw_mu=r.aifs_high, aifs_raw_sigma=pa["raw_rmse"],
                             aifs_cor_mu=pa["a"] + pa["b"] * r.aifs_high, aifs_cor_sigma=pa["sigma"]))
    fc = pd.DataFrame(rows)
    fc.to_csv(ROOT / "results" / "forecasts.csv", index=False)
    te = fc[fc.split == "TEST"]
    out["_overall_test_mae_F"] = {k: mae(te.actual, te[k]) for k in ["gfs_mu", "aifs_raw_mu", "aifs_cor_mu"]}
    tr = fc[fc.split == "TRAIN"]
    out["_overall_train_mae_F"] = {k: mae(tr.actual, tr[k]) for k in ["gfs_mu", "aifs_raw_mu", "aifs_cor_mu"]}
    out["_fit_dates"] = {"train_only": True, "n_train_rows": int(len(tr)), "n_test_rows": int(len(te))}
    (ROOT / "results" / "corrections.json").write_text(json.dumps(out, indent=1))
    print("TEST MAE °F:", out["_overall_test_mae_F"])
    print("TRAIN MAE °F:", out["_overall_train_mae_F"])
    for st in sorted(k for k in out if not k.startswith("_")):
        p = out[st]["aifs_high"]
        print(st, f"AIFS raw bias(train) {p['bias_raw_train']:+.1f}  TEST MAE raw {p['mae_raw_test']} -> corrected {p['mae_corrected_test']}  sigma {p['sigma']:.2f}")


if __name__ == "__main__":
    main()
