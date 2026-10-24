"""7.3 — order-path test. With demo keys (~/.kalshi/demo.pem + demo_key_id): place and cancel one tiny demo order
through the same order_body() the live bot uses. Without them: one read-only authenticated balance call on prod.
Logs only OK/error — never balances, keys or account details. Output: logs/live/order_test.json"""
import datetime as dt
import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bot.kalshi import Kalshi, has_keys  # noqa: E402
from bot.live import LOGDIR, order_body  # noqa: E402


def main():
    now = dt.datetime.now(dt.timezone.utc)
    res = {"at": now.isoformat()}
    if has_keys("demo"):
        k = Kalshi(env="demo")
        m = next(m for m in k.paged("/markets", "markets", status="open") if float(m.get("yes_bid_dollars") or 0) > 0.02)
        order = dict(ticker=m["ticker"], side="yes", price=0.01, count=1, client_order_id=str(uuid.uuid4()))
        r = k.request("POST", "/portfolio/events/orders", json=order_body(order, now))
        oid = r.get("order", r).get("order_id")
        k.request("DELETE", f"/portfolio/events/orders/{oid}")
        res.update(mode="demo order placed and canceled", ticker=m["ticker"], ok=True)
    else:
        try:
            ok = "balance" in Kalshi(env="prod").get("/portfolio/balance")
            res.update(mode="no demo keys: read-only prod balance call", ok=ok)
        except Exception as e:  # noqa: BLE001
            res.update(mode="no demo keys: read-only prod balance call", ok=False, error=str(e)[:200])
    LOGDIR.mkdir(parents=True, exist_ok=True)
    (LOGDIR / "order_test.json").write_text(json.dumps(res, indent=1))
    print(res)


if __name__ == "__main__":
    main()
