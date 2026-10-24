"""3.2 — for each city and market date in the window, save every bracket market (with its settled value)
and hourly candles (yes bid/ask OHLC) from open to close. Cached per event: data/kalshi/<series>/<event>.json.
Then writes results/markets.csv with the ask at bet time. Safe to re-run."""
import datetime as dt
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backtest.window import DAYS, bet_time, is_test  # noqa: E402
from bot.kalshi import Kalshi  # noqa: E402

CACHE = ROOT / "data" / "kalshi"
MON = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()


def event_ticker(series, d):
    return f"{series}-{d:%y}{MON[d.month - 1]}{d:%d}"


def ts(s):
    return int(dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())


def fetch_event(k, series, d):
    ev = event_ticker(series, d)
    f = CACHE / series / f"{ev}.json"
    if f.exists():
        return json.loads(f.read_text())
    ms = k.get("/markets", event_ticker=ev, limit=100).get("markets", [])
    hist = False
    if not ms:
        ms = k.get("/historical/markets", event_ticker=ev, limit=100).get("markets", [])
        hist = True
    out = {"event": ev, "date": str(d), "historical": hist, "markets": []}
    for m in ms:
        if m.get("status") not in ("finalized", "settled", "determined") and not hist:
            raise RuntimeError(f"{m['ticker']} not settled yet ({m.get('status')})")
        a, b = ts(m["open_time"]), min(ts(m["close_time"]), ts(m["open_time"]) + 3 * 86400)
        path = (f"/historical/markets/{m['ticker']}/candlesticks" if hist
                else f"/series/{series}/markets/{m['ticker']}/candlesticks")
        candles = k.get(path, start_ts=a, end_ts=b, period_interval=60).get("candlesticks", [])
        keep = {x: m.get(x) for x in ["ticker", "strike_type", "floor_strike", "cap_strike", "result",
                                      "expiration_value", "open_time", "close_time", "volume_fp", "rules_primary",
                                      "yes_sub_title"]}
        keep["candles"] = [{"t": c["end_period_ts"], "ask": c["yes_ask"], "bid": c["yes_bid"],
                            "vol": c.get("volume", c.get("volume_fp")), "price": c.get("price")} for c in candles]
        out["markets"].append(keep)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(out))
    return out


def quote_at(candles, t):
    """Yes bid/ask as of time t: the close of the last hourly candle ending at or before t."""
    best = None
    for c in candles:
        if c["t"] <= t and (best is None or c["t"] > best["t"]):
            best = c
    if best is None:
        return None, None, None
    def close(q):  # historical candles use "close", live ones "close_dollars"
        x = (q or {}).get("close", (q or {}).get("close_dollars"))
        return float(x) if x is not None else None
    return close(best["ask"]), close(best["bid"]), best["t"]


def main():
    cities = json.loads((ROOT / "results" / "cities.json").read_text())
    k = Kalshi(auth=False)
    rows, missing = [], []
    for c in cities:
        for d in DAYS:
            try:
                ev = fetch_event(k, c["series"], d)
            except Exception as e:  # noqa: BLE001
                missing.append((c["series"], str(d), str(e)[:120]))
                continue
            if not ev["markets"]:
                missing.append((c["series"], str(d), "no markets"))
                continue
            bt = int(bet_time(d).timestamp())
            for m in ev["markets"]:
                ask, bid, qt = quote_at(m["candles"], bt)
                rows.append(dict(city=c["city"], station=c["station"], series=c["series"], date=str(d),
                                 split="TEST" if is_test(d) else "TRAIN", event=ev["event"], ticker=m["ticker"],
                                 strike_type=m["strike_type"], floor=m["floor_strike"], cap=m["cap_strike"],
                                 result=m["result"], settled_high=float(m["expiration_value"]) if m["expiration_value"] else None,
                                 open_time=m["open_time"], bet_ts=bt, quote_ts=qt, yes_ask=ask, yes_bid=bid,
                                 no_ask=None if bid is None else round(1 - bid, 4),
                                 volume=float(m["volume_fp"] or 0)))
        print(c["series"], "done", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(ROOT / "results" / "markets.csv", index=False)
    (ROOT / "results" / "markets_missing.json").write_text(json.dumps(missing, indent=1))
    print(f"markets={len(df)} events={df.event.nunique()} missing_events={len(missing)} "
          f"no_quote_at_bet_time={int(df.yes_ask.isna().sum())}")


if __name__ == "__main__":
    main()
