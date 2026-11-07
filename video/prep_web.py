"""Public-page captures (results/evidence/web/*.png + .json, from video/rec/capture_pages.cjs) -> video/chapters/tx/
web_frames.js as data URLs (file:// images would taint the canvas), with each page's highlight box, label, URL and
capture time. Run: python3 video/prep_web.py"""
import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "results" / "evidence" / "web"
out = {}
for j in sorted(SRC.glob("*.json")):
    m = json.loads(j.read_text())
    png = j.with_suffix(".png")
    out[m["name"]] = dict(img="data:image/png;base64," + base64.b64encode(png.read_bytes()).decode(), rects=m.get("rects"),
                          label=m["label"], url=m["url"], captured=m["captured_utc"][:10], title=m.get("title"),
                          blurred=m.get("blurred_items", 0))
(ROOT / "video" / "chapters" / "tx" / "web_frames.js").write_text("window.WEB = " + json.dumps(out) + ";\n")
print("web captures:", {k: bool(v["rects"]) for k, v in out.items()})
