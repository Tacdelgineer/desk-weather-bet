"""6.1 — build one small JSON per candidate bet of the corrected-AIFS player (edge > 0), using only what was known
at bet time: forecast, probability, price, fee, station TRAIN error stats, bid-ask spread, volume traded so far.
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


def main():
    cand = pd.read_csv(ROOT / "results" / "candidates.csv")
    cand = cand[(cand.player == "aifs_cor") & (cand.edge > 0)].copy()
    mk = pd.read_csv(ROOT / "results" / "markets.csv").set_index("ticker")
    corr = json.loads((ROOT / "results" / "corrections.json").read_text())
    rows = []
    for r in cand.itertuples():
        m = mk.loc[r.ticker]
        c = corr[r.station]["aifs_high"]
        if r.strike_type == "between":
            label = f"high between {int(r.floor)}°F and {int(r.cap)}°F"
        elif r.strike_type == "greater":
            label = f"high above {int(r.floor)}°F"
        else:
            label = f"high below {int(r.cap)}°F"
        state = dict(city=r.city, station=r.station, market=f"{label} on {r.date}", bet_side=r.side,
                     forecast_high_F=round(r.mu, 1), forecast_error_sd_F=round(r.sigma, 2),
                     model_probability_side_wins=round(r.p_side, 3), price_to_pay=r.price,
                     fee_per_contract=round(r.fee / r.contracts, 4), model_edge=round(r.edge, 3),
                     station_train_mae_corrected_F=round(c["mae_corrected_train"], 2),
                     station_train_raw_bias_F=round(c["bias_raw_train"], 2),
                     bid_ask_spread=round(float(m.yes_ask - m.yes_bid), 2),
                     volume_traded_before_bet=volume_before(m.series, m.event, r.ticker, int(m.bet_ts)))
        rows.append(dict(ticker=r.ticker, date=r.date, split=r.split, side=r.side, edge=r.edge, pnl=r.pnl,
                         won=r.won, state=json.dumps(state)))
    pd.DataFrame(rows).to_csv(ROOT / "results" / "judge_inputs.csv", index=False)
    print(len(rows), "candidates;", pd.DataFrame(rows).split.value_counts().to_dict())
    print(rows[0]["state"])


if __name__ == "__main__":
    main()
