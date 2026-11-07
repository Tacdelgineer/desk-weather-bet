"""The one export step for every video page: results/ (and the real logs and captures) -> video/chapters/data.js.
No number is typed here; every value is read from a file or computed from file values. Home paths are cut.
Run: python3 video/export.py"""
import csv
import json
import math
import re
import statistics as stt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"
J = lambda p: json.loads((R / p).read_text())
nohome = lambda s: re.sub(r"/home/[^/\s]+/(Projects/)?", "~/", s)

# ---------- 02 desk AI ----------
timing = J("timing.json")
log = (ROOT / "logs/1.1_dgx_00z.log").read_text().splitlines()
aifs_lines = [l for l in log if not re.search(r"/home/|warnings\.warn|return torch|Uninstalled|Installed", l)]
la = J("aifs_la_sanity.json")
cpu = timing["previous_minipc_cpu"]

# ---------- 03 hurricanes ----------
hur = J("hurricanes.json")
storms = [dict(name=s["name"], event=s["ref_event"], runs=[dict(days=r["days_before"], ref_km=r["ref_error_km"],
              err=r["error_km"]) for r in s["runs"]]) for s in hur["storms"]]
isl, isa = J("isaias_local.json")["storms"][0], J("isaias_archive.json")["storms"][0]
isaias = dict(event=isl["ref_event"].split(" (")[0], runs=[dict(days=a["days_before"], local_km=a["ref_error_km"], archive_km=b["ref_error_km"])
              for a, b in zip(isl["runs"], isa["runs"])])

# ---------- 04 market ----------
live = J("live.json")
cities = J("cities.json")
settle = J("settlement_check.json")

# ---------- 05 trap / 06 fix: TEST error per station (forecasts.csv, TEST rows) ----------
rows = [r for r in csv.DictReader(open(R / "forecasts.csv")) if r["split"] == "TEST" and r["actual"]]
def mae(rs, col):
    v = [abs(float(r["actual"]) - float(r[col])) for r in rs if r[col]]
    return round(stt.mean(v), 2) if v else None
by_st = []
from datetime import datetime
from zoneinfo import ZoneInfo
def lst_hours(tz):   # local standard time of the 00/06/12/18 UTC samples (RULES.md: the station's local-standard-time day)
    off = datetime(2026, 1, 15, tzinfo=ZoneInfo(tz)).utcoffset().total_seconds() / 3600
    return sorted(int((h + off) % 24) for h in (0, 6, 12, 18))
for c in cities:
    rs = [r for r in rows if r["station"] == c["station"]]
    raw_bias = round(stt.mean(float(r["actual"]) - float(r["aifs_raw_mu"]) for r in rs if r["aifs_raw_mu"]), 2)
    by_st.append(dict(city=c["city"], station=c["station"], n=len(rs), gfs=mae(rs, "gfs_mu"), raw=mae(rs, "aifs_raw_mu"),
                      v1=mae(rs, "aifs_fit_mu"), v2=mae(rs, "aifs_cor_mu"), raw_bias=raw_bias,
                      # afternoon peak: v2 correction file, bias_raw = raw − actual, so actual − raw = −bias_raw
                      lst_samples=lst_hours(c["tz"]), peak_train=round(-J("v2/corrections.json")[c["station"]]["aifs_high"]["bias_raw_train"], 2),
                      peak_test=round(-J("v2/corrections.json")[c["station"]]["aifs_high"]["bias_raw_test"], 2)))
vv = J("v1_vs_v2.json")
lac = next(c for c in cities if c["station"] == "KLAX")
glat, glon = la["grid_point"][0], la["grid_point"][1] - 360
km = 6371 * 2 * math.asin(math.sqrt(math.sin(math.radians(glat - lac["lat"]) / 2) ** 2 + math.cos(math.radians(glat)) *
                                    math.cos(math.radians(lac["lat"])) * math.sin(math.radians(glon - lac["lon"]) / 2) ** 2))

# ---------- 07 backtest ----------
bt, jd = J("backtest.json"), J("judge.json")
players = [dict(key=k, label=bt["players"][k]["label"], curve=bt["players"][k]["test"]["equity_curve"],
                pnl=bt["players"][k]["test"]["pnl"], bets=bt["players"][k]["test"]["bets"],
                win=bt["players"][k]["test"]["win_rate"], fees=bt["players"][k]["test"]["fees"]) for k in ("gfs", "aifs_raw", "aifs_cor")]
players.append(dict(key="aifs_cor_judge", label="corrected AIFS + judge", curve=jd["test"]["judge"]["equity_curve"],
                    pnl=jd["test"]["judge"]["pnl"], bets=jd["test"]["judge"]["bets"], win=jd["test"]["judge"]["win_rate"],
                    fees=jd["test"]["judge"]["fees"]))
rob = J("robustness.json")

# ---------- 09 bug ----------
ev = J("evidence/v1-bug/summary.json")
phx = ev["stations"]["KPHX"]
pfm_txt = (R / "evidence/v1-bug/nws_pfm_PSR_2026-10-23.txt").read_text().splitlines()
i0 = next(i for i, l in enumerate(pfm_txt) if l.startswith("FOUS55"))
i1 = next(i for i, l in enumerate(pfm_txt) if l.strip() == "$$")
block = pfm_txt[i0:i1]
mm = next(i for i, l in enumerate(block) if l.startswith("Min/Max"))
issued = next(k for k in phx["nws_pfm_max_F"] if "401 PM" in k)
pfm_max = phx["nws_pfm_max_F"][issued]
col, val = [(m.start(), m.group()) for m in re.finditer(r"\d+", block[mm])][1]   # Min/Max row: Fri night min, then Sat 10/24 max
assert int(val) == pfm_max, (val, pfm_max)
picks = json.loads((R / "evidence/v1-bug/2026-10-23_picks.json").read_text())
pk = next(p for p in picks["picks"] if p["station"] == "KPHX")
caps = R / "evidence/captures"

DATA = dict(
    timing=dict(machine=timing["machine"], ten_day_s=timing["measured"]["ten_day_240h_wall_s"],
                ten_day_model_s=timing["measured"]["ten_day_240h_model_s"], run60_s=timing["measured"]["backtest_run_60h_wall_s"],
                step_s=timing["measured"]["seconds_per_6h_step_steady"], backtest_h=timing["estimates_hours"]["backtest_local_120_runs_x_60h"],
                cpu_machine=cpu["machine"], cpu_step_s=cpu["seconds_per_6h_step"], cpu_ten_day_h=cpu["estimates_hours"]["ten_day_forecast_40_steps"],
                ten_day_h=timing["estimates_hours"]["ten_day_forecast"]),
    la_check=[dict(valid=c["valid"][5:16].replace("T", " "), aifs=c["aifs_C"], obs=c["nws_obs_C"]) for c in la["comparisons"]],
    aifs=dict(lines=aifs_lines, wall_s=timing["measured"]["ten_day_240h_wall_s"], src="logs/1.1_dgx_00z.log"),
    storms=storms, isaias=isaias,
    market=dict(order=live["orders"][0], rules=next(c for c in cities if c["station"] == "KPHX")["rules_example"],
                settle_matches=settle["matches"], settle_total=settle["compared"], settle_rate=settle["match_rate"],
                mismatches=settle["mismatches"]),
    stations=by_st, test_mae=vv["v2"]["test_mae_F"], test_mae_v1=vv["v1"]["test_mae_F"],
    la_grid=dict(grid=[round(glat, 2), round(glon, 2)], station=[lac["lat"], lac["lon"]], km=round(km, 1),
                 name=lac["station_name"]),
    pfm=dict(lines=block, row=mm, col=col, val=val, issued=issued, product="NWS Point Forecast Matrix · Phoenix AZ",
             src="results/evidence/v1-bug/nws_pfm_PSR_2026-10-23.txt (IEM AFOS archive)"),
    v1=dict(raw=phx["raw_high_F"], corrected=phx["v1_corrected_F"], gfs=phx["gfs_F"], nws=pfm_max, a=phx["v1_a"],
            b=phx["v1_b"], train_min=phx["train_raw_min_F"], train_max=phx["train_raw_max_F"],
            scatter=[[r[0], r[1]] for r in ev["scatter_train"]["KPHX"]], n_train=len(ev["scatter_train"]["KPHX"]),
            cli=phx["nws_cli_prelim_high_F"], market_day=ev["market_day"], minus_nws=round(phx["v1_corrected_F"] - pfm_max, 2),
            train_from=ev["scatter_train"]["KPHX"][0][2], train_to=ev["scatter_train"]["KPHX"][-1][2], log_day=picks["day"],
            pick=dict(ticker=pk["ticker"], side=pk["side"].upper(), price=pk["price"], edge=pk["edge"], mu=pk["mu"],
                      bracket=pk["yes_sub_title"]), mode=picks["mode"]),
    v1v2=dict(v1=vv["v1"]["players"], v2=vv["v2"]["players"]),
    bt=dict(players=players, split=vv["split"], brier=bt["accuracy_brier_test"],
            any_profitable=rob["any_case_profitable_on_test"], cases=list(dict.fromkeys(r["case"] for r in rob["table"])),
            rob=[{k: r[k] for k in ("case", "player", "test_pnl", "bets")} for r in rob["table"]],
            best_case=max((r for r in rob["table"] if r["bets"]), key=lambda r: r["test_pnl"])),
    judge=dict(examples=J("judge_examples.json"), cutoff=jd["judge_cutoff_train"], rule_threshold=jd["rule_threshold_train"],
               judge=jd["test"]["judge"], rule=jd["test"]["rule"], corr=jd["corr_pbet_vs_edge"]),
    captures=dict(git=nohome((caps / "git_tags.txt").read_text()).splitlines(),
                  issue=(caps / "issue1_first_comment.md").read_text().splitlines(),
                  crash=nohome((caps / "crash_traceback_2026-10-28.txt").read_text()).splitlines()),
    live=dict(**{k: live["totals"][k] for k in ("pnl", "won", "lost", "staked", "fees", "runs_completed",
                                                  "runs_crashed", "unfilled", "orders_outside_window")},
              n_orders=live["totals"]["orders"], orders=live["orders"], runs=live["runs"], window=live["window_runs"]),
)
out = ROOT / "video/chapters/data.js"
out.write_text("const DATA = " + json.dumps(DATA, ensure_ascii=False) + ";\n")
print("wrote", out, "| stations", [(s["station"], s["raw"], s["v2"]) for s in by_st], "| LA grid km", round(km, 1))
