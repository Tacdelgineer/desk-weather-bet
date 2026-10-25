"""6.1 — build one small JSON per candidate bet of the corrected-AIFS player (edge > 0), using only what was known
at bet time: forecast, probability, price, fee, station error stats from the 30 days before the run date (v2),
bid-ask spread, volume traded so far. Candidates the v2 guards skip are left out (the judge never sees them).
Writes results/judge_inputs.csv."""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def volume_before(series, event, ticker, bet_ts):
    raw = json.loads((ROOT / "data" / "kalshi" / series / f"{event}.json").read_text())
    m = next(x for x in raw["markets"] if x["ticker"] == ticker)
    return round(sum(float(c["vol"] or 0) for c in m["candles"] if c["t"] <= bet_ts), 2)


def judge_state(city, station, strike_type, floor, cap, date, side, mu, sigma, p_side, price, fee_per_contract,
                edge, raw_bias_30d, days_30d, spread, volume):
    """The exact JSON the judge sees — shared by the backtest and bot/live.py so live inputs match the backtest."""
    if strike_type == "between":
        label = f"high between {int(floor)}°F and {int(cap)}°F"
    elif strike_type == "greater":
        label = f"high above {int(floor)}°F"
    else:
        label = f"high below {int(cap)}°F"
    return dict(city=city, station=station, market=f"{label} on {date}", bet_side=side.upper(),
                forecast_high_F=round(mu, 1), forecast_error_sd_F=round(sigma, 2),
                model_probability_side_wins=round(p_side, 3), price_to_pay=price,
                fee_per_contract=round(fee_per_contract, 4), model_edge=round(edge, 3),
                station_30d_raw_bias_F=round(raw_bias_30d, 2), station_30d_days=int(days_30d),
                bid_ask_spread=round(spread, 2), volume_traded_before_bet=round(volume, 2))


def main():
    cand = pd.read_csv(ROOT / "results" / "candidates.csv")
    cand = cand[(cand.player == "aifs_cor") & (cand.edge > 0) & cand.guard.isna()].copy()
    mk = pd.read_csv(ROOT / "results" / "markets.csv").set_index("ticker")
    fc = pd.read_csv(ROOT / "results" / "forecasts.csv").set_index(["station", "date"])
    rows = []
    for r in cand.itertuples():
        m = mk.loc[r.ticker]
        c = fc.loc[(r.station, r.date)]
        state = judge_state(r.city, r.station, r.strike_type, r.floor, r.cap, r.date, r.side, r.mu, r.sigma, r.p_side,
                            r.price, r.fee / r.contracts, r.edge, -c.aifs_cor_bias, c.aifs_cor_ndays,
                            float(m.yes_ask - m.yes_bid), volume_before(m.series, m.event, r.ticker, int(m.bet_ts)))
        rows.append(dict(ticker=r.ticker, date=r.date, split=r.split, side=r.side, edge=r.edge, pnl=r.pnl,
                         won=r.won, state=json.dumps(state)))
    pd.DataFrame(rows).to_csv(ROOT / "results" / "judge_inputs.csv", index=False)
    print(len(rows), "candidates;", pd.DataFrame(rows).split.value_counts().to_dict())
    print(rows[0]["state"])


if __name__ == "__main__":
    main()
