"""The one export step for the style preview: results/ (and the real logs) -> video/chapters/data.js.
No number is typed here; every value is read from a file. Home paths are cut from log lines.
Run: python3 video/preview/export.py"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / "results"
J = lambda p: json.loads((R / p).read_text())

# shot 2 — EVIDENCE: the real Phoenix block of the NWS Point Forecast Matrix + the bot's v1 dry-run line
ev = J("evidence/v1-bug/summary.json")
phx = ev["stations"]["KPHX"]
pfm_txt = (R / "evidence/v1-bug/nws_pfm_PSR_2026-10-23.txt").read_text().splitlines()
i0 = next(i for i, l in enumerate(pfm_txt) if l.startswith("FOUS55"))
i1 = next(i for i, l in enumerate(pfm_txt) if l.strip() == "$$")
block = pfm_txt[i0:i1]
mm = next(i for i, l in enumerate(block) if l.startswith("Min/Max"))
issued = next(k for k in phx["nws_pfm_max_F"] if "401 PM" in k)
pfm_max = phx["nws_pfm_max_F"][issued]
nums = [(m.start(), m.group()) for m in re.finditer(r"\d+", block[mm])]
col, val = nums[1]                      # Min/Max row: Fri night min, then the Sat 10/24 max
assert int(val) == pfm_max, (val, pfm_max)
picks = json.loads((R / "evidence/v1-bug/2026-10-23_picks.json").read_text())
pk = next(p for p in picks["picks"] if p["station"] == "KPHX")

# shot 4 — CRT: the real AIFS 10-day run log on the DGX (warnings with paths dropped)
log = (ROOT / "logs/1.1_dgx_00z.log").read_text().splitlines()
keep = [l for l in log if not re.search(r"/home/|warnings\.warn|return torch|Uninstalled|Installed", l)]
timing = J("timing.json")

# shot 5 — backtest, TEST window, PAPER MONEY: four players' equity curves
bt, jd = J("backtest.json"), J("judge.json")
players = [dict(key=k, label=bt["players"][k]["label"], curve=bt["players"][k]["test"]["equity_curve"],
                pnl=bt["players"][k]["test"]["pnl"], bets=bt["players"][k]["test"]["bets"]) for k in ("gfs", "aifs_raw", "aifs_cor")]
players.append(dict(key="aifs_cor_judge", label="corrected AIFS + judge", curve=jd["test"]["judge"]["equity_curve"],
                    pnl=jd["test"]["judge"]["pnl"], bets=jd["test"]["judge"]["bets"]))
split = J("v1_vs_v2.json")["split"]

# shot 6 — live week, REAL MONEY
lv = J("live.json")["totals"]

DATA = dict(
    pfm=dict(lines=block, row=mm - 0, col=col, val=val, issued=issued, product="NWS Point Forecast Matrix · Phoenix AZ",
             src="results/evidence/v1-bug/nws_pfm_PSR_2026-10-23.txt (IEM AFOS archive)"),
    v1=dict(raw=phx["raw_high_F"], corrected=phx["v1_corrected_F"], gfs=phx["gfs_F"], nws=pfm_max, a=phx["v1_a"],
            b=phx["v1_b"], train_min=phx["train_raw_min_F"], train_max=phx["train_raw_max_F"],
            scatter=[[r[0], r[1]] for r in ev["scatter_train"]["KPHX"]], n_train=len(ev["scatter_train"]["KPHX"]),
            cli=phx["nws_cli_prelim_high_F"], market_day=ev["market_day"], minus_nws=round(phx["v1_corrected_F"] - pfm_max, 2),
            train_from=ev["scatter_train"]["KPHX"][0][2], train_to=ev["scatter_train"]["KPHX"][-1][2], log_day=picks["day"],
            pick=dict(ticker=pk["ticker"], side=pk["side"].upper(), price=pk["price"], edge=pk["edge"], mu=pk["mu"],
                      bracket=pk["yes_sub_title"]), mode=picks["mode"]),
    aifs=dict(lines=keep, wall_s=timing["measured"]["ten_day_240h_wall_s"], src="logs/1.1_dgx_00z.log"),
    bt=dict(players=players, split=split),
    live=dict(pnl=lv["pnl"], won=lv["won"], lost=lv["lost"], orders=lv["orders"], staked=lv["staked"], fees=lv["fees"],
              runs_completed=lv["runs_completed"], runs_crashed=lv["runs_crashed"], unfilled=lv["unfilled"]),
)
out = ROOT / "video/chapters/data.js"
out.write_text("const DATA = " + json.dumps(DATA, ensure_ascii=False) + ";\n")
print("wrote", out, "| aifs log lines", len(keep), "| live pnl", lv["pnl"], "| pfm max", val, "at col", col)
