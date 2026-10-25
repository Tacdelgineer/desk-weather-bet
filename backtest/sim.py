"""5.1–5.4 — turn forecasts into bracket probabilities and simulate betting, same rules for every player.

Probability: high ~ Normal(mu, sigma) with integer settlement (continuity ±0.5 °F):
  between [F, C]  -> P(F-0.5 < X < C+0.5);  greater F -> P(X > F+0.5);  less C -> P(X < C-0.5)
Bet rule (at the ask at bet time, taker fee): buy YES if p - ask_yes - fee/contract > threshold, buy NO if
(1-p) - ask_no - fee/contract > threshold (ask_no = 1 - yes_bid); at most one side and $1 (incl. fee) per market.
Fill assumption: a $1 order fills in full at the quoted ask (candles have no depth) — stated in results.
Threshold: tuned on TRAIN (grid 0.00–0.30), reported on TEST.
Guards (v2, backtest/rolling.py, same for every player): skip if the player's high is > 4 °F from GFS, or edge > 0.30.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backtest.fees import fee  # noqa: E402
from backtest.rolling import guard  # noqa: E402
from backtest.window import assert_train_only  # noqa: E402

PLAYERS = {"gfs": "free GFS forecast", "aifs_raw": "raw AIFS", "aifs_cor": "corrected AIFS + one-line rule"}
GRID = [round(x, 2) for x in np.arange(0.0, 0.301, 0.01)]
MAX_PER_MARKET = 1.0
MIN_TRAIN_BETS = 10


def bracket_prob(row, mu, sigma):
    st = row.strike_type
    if st == "between":
        return norm.cdf(row.cap + 0.5, mu, sigma) - norm.cdf(row.floor - 0.5, mu, sigma)
    if st == "greater":
        return 1 - norm.cdf(row.floor + 0.5, mu, sigma)
    if st == "less":
        return norm.cdf(row.cap - 0.5, mu, sigma)
    raise ValueError(st)


def size(price, budget=MAX_PER_MARKET, fee_mult=1.0):
    """Most contracts whose cost + fee fits the per-market budget."""
    c = int(budget // price)
    while c > 0 and c * price + fee(price, c, multiplier=fee_mult) > budget + 1e-9:
        c -= 1
    return c


def candidates(markets, fc, fee_mult=1.0):
    """One row per market per player with probability, both sides' edges, and the P&L if bet."""
    m = markets.merge(fc, on=["city", "station", "date", "split"], how="inner")
    rows = []
    for r in m.itertuples():
        for pl in PLAYERS:
            mu, sg = getattr(r, f"{pl}_mu"), getattr(r, f"{pl}_sigma")
            if pd.isna(mu):
                continue
            p = float(bracket_prob(r, mu, sg))
            best = None
            for side, price, pwin in (("YES", r.yes_ask, p), ("NO", r.no_ask, 1 - p)):
                if pd.isna(price) or not (0.01 <= price <= 0.99):
                    continue  # no real offer at bet time
                c = size(price, fee_mult=fee_mult)
                if c == 0:
                    continue
                f = fee(price, c, multiplier=fee_mult)
                edge = pwin - price - f / c
                if best is None or edge > best["edge"]:
                    won = (r.result == "yes") == (side == "YES")
                    best = dict(side=side, price=price, contracts=c, fee=f, edge=edge, p_side=pwin, won=won,
                                pnl=round((c if won else 0) - c * price - f, 4), cost=round(c * price + f, 4))
            if best:
                best["guard"] = guard(mu, r.gfs_mu, best["edge"])
                rows.append(dict(player=pl, city=r.city, station=r.station, date=r.date, split=r.split,
                                 ticker=r.ticker, strike_type=r.strike_type, floor=r.floor, cap=r.cap, mu=mu,
                                 sigma=sg, p_yes=p, yes_ask=r.yes_ask, no_ask=r.no_ask, actual=r.actual,
                                 result=r.result, volume=r.volume, **best))
    return pd.DataFrame(rows)


def pick_threshold(cand_train):
    assert_train_only(cand_train.date)
    best = None
    for th in GRID:
        b = cand_train[cand_train.edge > th]
        if len(b) < MIN_TRAIN_BETS:
            continue
        score = b.pnl.sum()
        if best is None or score > best[1]:
            best = (th, score, len(b))
    return best


def summarize(bets):
    if bets.empty:
        return dict(pnl=0.0, bets=0, win_rate=None, fees=0.0, staked=0.0, roi=None, by_city={})
    eq = bets.sort_values(["date", "ticker"]).assign(equity=lambda d: d.pnl.cumsum())
    return dict(pnl=round(float(bets.pnl.sum()), 2), bets=int(len(bets)), win_rate=round(float(bets.won.mean()), 3),
                fees=round(float(bets.fee.sum()), 2), staked=round(float(bets.cost.sum()), 2),
                roi=round(float(bets.pnl.sum() / bets.cost.sum()), 4),
                by_city={k: round(float(v), 2) for k, v in bets.groupby("city").pnl.sum().items()},
                equity_curve=[[str(d), round(float(e), 2)] for d, e in eq.groupby("date").equity.last().items()])


def brier(markets, fc):
    """Accuracy bar: Brier score on TEST for market mid-price vs each player's probabilities."""
    m = markets.merge(fc, on=["city", "station", "date", "split"], how="inner")
    m = m[(m.split == "TEST") & m.yes_ask.notna() & m.yes_bid.notna()]
    y = (m.result == "yes").astype(float)
    out = {"market_mid": round(float(np.mean(((m.yes_ask + m.yes_bid) / 2 - y) ** 2)), 4), "n_markets": int(len(m))}
    for pl in PLAYERS:
        p = np.array([bracket_prob(r, getattr(r, f"{pl}_mu"), getattr(r, f"{pl}_sigma")) for r in m.itertuples()])
        out[pl] = round(float(np.mean((p - y) ** 2)), 4)
    return out


def run(fee_mult=1.0, th_shift=0.0, extra_players=None):
    markets = pd.read_csv(ROOT / "results" / "markets.csv")
    markets["actual"] = markets.settled_high
    fc = pd.read_csv(ROOT / "results" / "forecasts.csv").drop(columns=["actual"])
    for pl in PLAYERS:
        if f"{pl}_mu" not in fc:
            fc[f"{pl}_mu"], fc[f"{pl}_sigma"] = fc[f"{pl.replace('_cor', '_cor')}_mu"], fc[f"{pl}_sigma"]
    cand = candidates(markets, fc, fee_mult)
    res, allbets = {}, []
    for pl in PLAYERS:
        c = cand[(cand.player == pl) & (cand.guard == "")]
        th, train_pnl, train_n = pick_threshold(c[c.split == "TRAIN"]) or (None, None, 0)
        if th is None:
            res[pl] = dict(label=PLAYERS[pl], threshold=None, note="no threshold with enough TRAIN bets")
            continue
        th_used = round(th + th_shift, 2)
        test = c[(c.split == "TEST") & (c.edge > th_used)]
        allbets.append(test.assign(threshold=th_used))
        g = cand[(cand.player == pl) & (cand.split == "TEST") & (cand.guard != "") & (cand.edge > th_used)]
        res[pl] = dict(label=PLAYERS[pl], threshold_train=th, threshold_used=th_used,
                       train_pnl=round(float(train_pnl), 2), train_bets=int(train_n), test=summarize(test),
                       test_skipped_by_guard=dict(n=int(len(g)), pnl_if_taken=round(float(g.pnl.sum()), 2),
                                                  gfs_gap=int(g.guard.str.contains("from GFS").sum()),
                                                  edge_cap=int(g.guard.str.startswith("edge").sum())))
    return res, cand, (pd.concat(allbets) if allbets else pd.DataFrame()), markets, fc


def main():
    res, cand, bets, markets, fc = run()
    cand.to_csv(ROOT / "results" / "candidates.csv", index=False)
    bets.to_csv(ROOT / "results" / "backtest_bets.csv", index=False)
    out = dict(method=__doc__.strip(), label="PAPER MONEY", players=res, accuracy_brier_test=brier(markets, fc),
               fills_assumption="full fill at quoted ask for <= $1 per market (no order-book depth in candles)")
    # 5.3 CHECK: per-bet P&L sums to the total
    for pl, r in res.items():
        if "test" in r:
            s = round(float(bets[bets.player == pl].pnl.sum()), 2)
            assert abs(s - r["test"]["pnl"]) < 0.005, (pl, s, r["test"]["pnl"])
    out["check_per_bet_sum_equals_total"] = True
    (ROOT / "results" / "backtest.json").write_text(json.dumps(out, indent=1))
    pd.DataFrame([dict(player=pl, label=r["label"], threshold=r.get("threshold_used"), train_pnl=r.get("train_pnl"),
                       **{k: v for k, v in r.get("test", {}).items() if k not in ("by_city", "equity_curve")})
                  for pl, r in res.items()]).to_csv(ROOT / "results" / "backtest_summary.csv", index=False)
    for pl, r in res.items():
        t = r.get("test", {})
        print(f"{pl:9s} th={r.get('threshold_used')} TEST pnl={t.get('pnl')} bets={t.get('bets')} "
              f"win={t.get('win_rate')} fees={t.get('fees')} roi={t.get('roi')} guarded={r.get('test_skipped_by_guard')}")
    print("Brier TEST:", out["accuracy_brier_test"])


if __name__ == "__main__":
    main()
