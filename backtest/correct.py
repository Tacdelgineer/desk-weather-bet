"""4.3 — station corrections.
v2 (live player, aifs_cor): rolling 30-day bias per station, past data only (backtest/rolling.py).
v1 (kept for comparison, aifs_fit): fitted on TRAIN only: actual_high ≈ a + b × model_high, per station and model;
spread (sigma) = std of TRAIN residuals. It extrapolates badly outside the summer range (video/JOURNAL.md).
Raw forecasts get sigma = TRAIN RMSE around the raw value (no bias fix).
Saves results/corrections.json (coefficients + before/after error in °F on TRAIN and TEST) and
results/forecasts.csv (one row per city/date with every player's centre and sigma)."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backtest.rolling import rolling_correction  # noqa: E402
from backtest.window import assert_train_only, is_test  # noqa: E402
import datetime as dt  # noqa: E402


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
        hist = list(zip(g.date, g.settled_high.astype(float), g.aifs_high.astype(float)))
        for r in g.itertuples():
            pa, pg = out[st]["aifs_high"], out[st]["gfs_high"]
            rc = rolling_correction(hist, dt.date.fromisoformat(r.date) - dt.timedelta(days=1))
            rows.append(dict(city=r.city, station=st, date=r.date, split=r.split, actual=r.settled_high,
                             gfs_mu=r.gfs_high, gfs_sigma=pg["raw_rmse"],
                             aifs_raw_mu=r.aifs_high, aifs_raw_sigma=pa["raw_rmse"],
                             aifs_cor_mu=r.aifs_high + rc["bias"] if rc else np.nan,
                             aifs_cor_sigma=rc["sigma"] if rc else np.nan, aifs_cor_bias=rc["bias"] if rc else np.nan,
                             aifs_cor_ndays=rc["n"] if rc else 0,
                             aifs_fit_mu=pa["a"] + pa["b"] * r.aifs_high, aifs_fit_sigma=pa["sigma"]))
        sg = pd.DataFrame(rows[-len(g):])
        out[st]["aifs_rolling30"] = {f"mae_{n.lower()}": mae(p.actual, p.aifs_cor_mu) for n, p in
                                     sg.dropna(subset=["aifs_cor_mu"]).groupby("split")}
        out[st]["aifs_rolling30"]["days_with_forecast"] = {n: int(p.aifs_cor_mu.notna().sum()) for n, p in sg.groupby("split")}
    fc = pd.DataFrame(rows)
    fc.to_csv(ROOT / "results" / "forecasts.csv", index=False)
    cols = ["gfs_mu", "aifs_raw_mu", "aifs_cor_mu", "aifs_fit_mu"]
    te = fc[fc.split == "TEST"]
    out["_overall_test_mae_F"] = {k: mae(te.dropna(subset=[k]).actual, te[k].dropna()) for k in cols}
    tr = fc[fc.split == "TRAIN"]
    out["_overall_train_mae_F"] = {k: mae(tr.dropna(subset=[k]).actual, tr[k].dropna()) for k in cols}
    out["_columns"] = {"aifs_cor_mu": "v2: raw + rolling 30-day bias (past data only; NaN if < 20 of 30 days)",
                       "aifs_fit_mu": "v1: a + b × raw, fit on TRAIN"}
    out["_rolling_days_with_forecast"] = {n: int(p.aifs_cor_mu.notna().sum()) for n, p in fc.groupby("split")}
    out["_fit_dates"] = {"train_only": True, "n_train_rows": int(len(tr)), "n_test_rows": int(len(te))}
    (ROOT / "results" / "corrections.json").write_text(json.dumps(out, indent=1))
    print("TEST MAE °F:", out["_overall_test_mae_F"])
    print("TRAIN MAE °F:", out["_overall_train_mae_F"])
    for st in sorted(k for k in out if not k.startswith("_")):
        p = out[st]["aifs_high"]
        print(st, f"AIFS raw bias(train) {p['bias_raw_train']:+.1f}  TEST MAE raw {p['mae_raw_test']} -> v1 fit {p['mae_corrected_test']}"
              f" -> v2 rolling {out[st]['aifs_rolling30'].get('mae_test')}")
    print("rolling-correction days:", out["_rolling_days_with_forecast"])


if __name__ == "__main__":
    main()
