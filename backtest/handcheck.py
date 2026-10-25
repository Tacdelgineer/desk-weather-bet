"""5.2 CHECK — trace 5 random TEST bets end to end, recomputing every number from the raw inputs
(AIFS samples, settled highs of the 30 days before the run date, raw Kalshi candles/settlement) independently of
sim.py. v2 correction: raw + mean(actual - raw) over [run-30, run-1], sigma = their std (ddof 1); guards re-checked."""
import json
import math
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def main():
    bets = pd.read_csv(ROOT / "results" / "backtest_bets.csv")
    settled = pd.read_csv(ROOT / "results" / "markets.csv").groupby(["station", "date"]).settled_high.first()
    gfs = pd.read_csv(ROOT / "results" / "gfs_highs.csv").set_index(["station", "date"]).gfs_high
    highs = pd.read_csv(ROOT / "results" / "aifs_highs.csv")
    b = bets[bets.player == "aifs_cor"].sample(5, random_state=7)
    lines = ["# Hand check — 5 random TEST bets (player: corrected AIFS v2 + rule), PAPER MONEY", ""]
    ok = True
    for r in b.itertuples():
        h = highs[(highs.station == r.station) & (highs.date == r.date)].iloc[0]
        run = pd.Timestamp(r.date) - pd.Timedelta(days=1)
        win = [str((run - pd.Timedelta(days=k)).date()) for k in range(1, 31)]
        hs = highs[(highs.station == r.station) & highs.date.isin(win)].set_index("date").aifs_high
        diffs = [settled[(r.station, d)] - hs[d] for d in win if d in hs.index and (r.station, d) in settled.index]
        bias = sum(diffs) / len(diffs)
        c = {"sigma": math.sqrt(sum((x - bias) ** 2 for x in diffs) / (len(diffs) - 1))}
        mu = h.aifs_high + bias
        g = gfs[(r.station, r.date)]
        lo = {"between": r.floor - 0.5, "greater": r.floor + 0.5, "less": -1e9}[r.strike_type]
        hi = {"between": r.cap + 0.5, "greater": 1e9, "less": r.cap - 0.5}[r.strike_type]
        p_yes = phi((hi - mu) / c["sigma"]) - phi((lo - mu) / c["sigma"])
        series, event = r.ticker.split("-")[0], "-".join(r.ticker.split("-")[:2])
        raw = json.loads((ROOT / "data" / "kalshi" / series / f"{event}.json").read_text())
        m = next(x for x in raw["markets"] if x["ticker"] == r.ticker)
        bt = int(pd.Timestamp(r.date).timestamp()) - 86400 + 16 * 3600
        cd = max((x for x in m["candles"] if x["t"] <= bt), key=lambda x: x["t"])
        get = lambda q: float(q.get("close", q.get("close_dollars")))  # noqa: E731
        price = get(cd["ask"]) if r.side == "YES" else round(1 - get(cd["bid"]), 4)
        n = r.contracts
        fee = math.ceil(round(0.07 * n * price * (1 - price) * 100, 9)) / 100
        won = (m["result"] == "yes") == (r.side == "YES")
        pnl = (n if won else 0) - n * price - fee
        p_side = p_yes if r.side == "YES" else 1 - p_yes
        edge = p_side - price - fee / n
        match = all(abs(x - y) < 1e-3 for x, y in [(mu, r.mu), (p_yes, r.p_yes), (price, r.price), (fee, r.fee),
                                                     (pnl, r.pnl), (edge, r.edge)]) and won == r.won
        match &= len(diffs) >= 20 and abs(mu - g) <= 4 and edge <= 0.30
        ok &= match
        lines += [f"## {r.ticker} — {r.side}",
                  f"- forecast: AIFS run {h.init}, 6-hourly 2 m temps in the local day: {h.samples} → raw high {h.aifs_high:.2f}°F",
                  f"- correction ({r.station}, v2 rolling): mean(actual − raw) over {len(diffs)} of the 30 days {win[-1]}…{win[0]} = {bias:+.2f}°F → {h.aifs_high:.2f} {bias:+.2f} = {mu:.2f}°F, sigma {c['sigma']:.2f}",
                  f"- guards: GFS {g:.1f}°F, gap {abs(mu - g):.1f}°F ≤ 4; edge ≤ 0.30",
                  f"- bracket: {r.strike_type} floor={r.floor} cap={r.cap} ({m['yes_sub_title']}) → P(YES) = {p_yes:.4f}, P({r.side}) = {p_side:.4f}",
                  f"- price at bet time (candle ending {pd.Timestamp(cd['t'], unit='s')}Z): {r.side} ask = ${price:.2f}",
                  f"- size: {n} contracts, cost ${n * price:.2f}, fee round_up(0.07×{n}×{price:.2f}×{1 - price:.2f}) = ${fee:.2f}; edge = {p_side:.4f} − {price:.2f} − {fee / n:.4f} = {edge:.4f} > threshold {r.threshold}",
                  f"- settlement: Kalshi settled high {m['expiration_value']}°F, result {m['result'].upper()} → {'WIN' if won else 'LOSS'}",
                  f"- P&L: {'%d × $1' % n if won else '$0'} − ${n * price:.2f} − ${fee:.2f} = **${pnl:+.2f}** (sim.py: ${r.pnl:+.2f}) {'✓' if match else '✗ MISMATCH'}", ""]
    lines.append(f"All 5 recomputed independently match sim.py: {'YES' if ok else 'NO'}")
    (ROOT / "logs" / "handcheck.md").write_text("\n".join(lines))
    print("\n".join(lines[-12:]))
    assert ok


if __name__ == "__main__":
    main()
