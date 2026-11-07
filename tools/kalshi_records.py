"""Read-only: pull this account's orders, fills and settlements from Kalshi into data/live_kalshi/ (gitignored).
GET calls only. Prints counts and field names, never keys or balances."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bot.kalshi import Kalshi

out = Path(__file__).resolve().parents[1] / "data" / "live_kalshi"
out.mkdir(parents=True, exist_ok=True)
k = Kalshi()
for name, path, key in [("orders", "/portfolio/orders", "orders"), ("fills", "/portfolio/fills", "fills"),
                        ("settlements", "/portfolio/settlements", "settlements")]:
    rows = list(k.paged(path, key, limit=200))
    (out / f"{name}.json").write_text(json.dumps(rows, indent=1))
    print(name, len(rows), sorted(rows[0].keys()) if rows else [])
