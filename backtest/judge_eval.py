"""6.2/6.3 — judge vs one-line rule on TEST. Candidates = corrected-AIFS bets with positive edge.
Judge plays: bet when P(bet) > cut-off, cut-off tuned on TRAIN. Rule plays: bet when edge > X, X tuned on TRAIN
(from results/backtest.json). Writes results/judge.json and results/judge_examples.json."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backtest.sim import MIN_TRAIN_BETS, summarize  # noqa: E402
from backtest.window import assert_train_only  # noqa: E402

CUTS = [round(x, 2) for x in np.arange(0.30, 0.951, 0.01)]


def load():
    inp = pd.read_csv(ROOT / "results" / "judge_inputs.csv")
    calls = pd.DataFrame([json.loads(l) for l in (ROOT / "data" / "judge" / "calls.jsonl").read_text().splitlines()])
    calls["p_bet"] = calls.p.map(lambda d: d["bet"])
    df = inp.merge(calls[["ticker", "p_bet"]], on="ticker", how="inner")
    cand = pd.read_csv(ROOT / "results" / "candidates.csv")
    cand = cand[cand.player == "aifs_cor"][["ticker", "city", "cost", "fee"]]
    return df.merge(cand, on="ticker", how="left"), len(inp)


def main():
    df, n_inputs = load()
    tr, te = df[df.split == "TRAIN"], df[df.split == "TEST"]
    assert_train_only(tr.date)
    best = None
    for c in CUTS:
        b = tr[tr.p_bet > c]
        if len(b) >= MIN_TRAIN_BETS and (best is None or b.pnl.sum() > best[1]):
            best = (c, float(b.pnl.sum()), len(b))
    cut = best[0]
    bt = json.loads((ROOT / "results" / "backtest.json").read_text())
    X = bt["players"]["aifs_cor"]["threshold_used"]
    judge_bets, rule_bets = te[te.p_bet > cut], te[te.edge > X]
    # does the judge add anything beyond the edge? correlation of p_bet with edge
    corr = float(np.corrcoef(df.p_bet, df.edge)[0, 1])
    out = dict(label="PAPER MONEY", candidates=int(len(df)), inputs=n_inputs, coverage=round(len(df) / n_inputs, 4),
               judge_cutoff_train=cut, judge_train_pnl=round(best[1], 2), judge_train_bets=best[2],
               rule_threshold_train=X, corr_pbet_vs_edge=round(corr, 3),
               test=dict(judge=summarize(judge_bets), rule=summarize(rule_bets),
                         both_skip_all=summarize(te.iloc[0:0])))
    out["winner_on_test"] = "judge" if out["test"]["judge"]["pnl"] > out["test"]["rule"]["pnl"] else "rule"
    (ROOT / "results" / "judge.json").write_text(json.dumps(out, indent=1))
    # 6.3 — three example decisions for the explainer: a judge 'bet', a judge 'skip' the rule would take, a close call
    ex = []
    pick = [te[te.p_bet > cut].sort_values("p_bet", ascending=False).head(1),
            te[(te.p_bet <= cut) & (te.edge > X)].sort_values("edge", ascending=False).head(1),
            te.iloc[(te.p_bet - cut).abs().argsort()[:1]]]
    for kind, p in zip(["judge says bet", "judge skips a bet the rule takes", "close call"], pick):
        for r in p.itertuples():
            ex.append(dict(kind=kind, ticker=r.ticker, state=json.loads(r.state), p_bet=round(r.p_bet, 3),
                           p_skip=round(1 - r.p_bet, 3), cutoff=cut, judge_action="bet" if r.p_bet > cut else "skip",
                           rule_action="bet" if r.edge > X else "skip", won=bool(r.won), pnl=r.pnl))
    (ROOT / "results" / "judge_examples.json").write_text(json.dumps(ex, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != "test"}, indent=0))
    for k in ["judge", "rule"]:
        t = out["test"][k]
        print(k, "TEST pnl", t["pnl"], "bets", t["bets"], "win", t["win_rate"])


if __name__ == "__main__":
    main()
