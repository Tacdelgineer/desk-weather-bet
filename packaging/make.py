"""10.3 packaging from the results files: packaging/DESCRIPTION.md, packaging/TITLES.md, packaging/THUMBNAILS.md and the
results section of README.md. No number is typed; chapter times come from the master's chapters.txt.
Run after the master: python3 packaging/make.py"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"
J = lambda p: json.loads((R / p).read_text())
hur, bt, jd, live, ev, st = J("hurricanes.json"), J("backtest.json"), J("judge.json"), J("live.json"), J("evidence/v1-bug/summary.json"), J("settlement_check.json")
mel = next(r for r in next(s for s in hur["storms"] if s["name"] == "MELISSA")["runs"] if r["days_before"] == 3)
P = {k: bt["players"][k]["test"] for k in ("gfs", "aifs_raw", "aifs_cor")}
J_ = jd["test"]["judge"]; T = live["totals"]; phx = ev["stations"]["KPHX"]; order0 = live["orders"][0]
money = lambda v: f"{'+' if v >= 0 else '−'}${abs(v):.2f}"
chapters = (ROOT / "video/results/final/chapters.txt").read_text().strip()

results = f"""## Results (every number from `results/`)

- **Hurricanes** (`results/hurricanes.json`): AIFS's forecast from 3 days before MELISSA's landfall missed by {mel['ref_error_km']} km.
- **Backtest, PAPER MONEY**, TEST window only (`results/backtest.json`, `results/judge.json`): free GFS {money(P['gfs']['pnl'])},
  raw AIFS {money(P['aifs_raw']['pnl'])}, corrected AIFS + rule {money(P['aifs_cor']['pnl'])}, corrected AIFS + judge {money(J_['pnl'])} on {J_['bets']} bets.
  The market's own price was the most accurate forecast (Brier {bt['accuracy_brier_test']['market_mid']} vs {bt['accuracy_brier_test']['aifs_cor']} for the best model).
- **The bug** (`results/evidence/v1-bug/`): v1 turned Phoenix's raw {phx['raw_high_F']} °F into {phx['v1_corrected_F']} °F; the NWS said
  {next(v for k, v in phx['nws_pfm_max_F'].items() if '401 PM' in k)} °F. Caught in a dry run; rules v2 locked before any real money.
- **Live week, REAL MONEY · $10 TEST** (`results/live.json`, settled from Kalshi's records): {T['orders']} orders, {T['won']} won,
  {T['lost']} lost, P&L {money(T['pnl'])}. The bot crashed from day {T['runs_completed'] + 1}: {T['runs_completed']} of {T['runs_completed'] + T['runs_crashed']} days traded.
- Settlement check: Kalshi's settled high matched the NWS climate report on {st['matches']} of {st['compared']} station-days.
"""
readme = (ROOT / "README.md").read_text().split("## Results")[0].rstrip()
readme = readme.replace("Work in progress. Every number will come from a file in `results/`.",
                        "Video: \"My Desk AI vs the Weather Betting Market\". Every number comes from a file in `results/`.")
(ROOT / "README.md").write_text(readme + "\n\n" + results + "\nRules: RULES.md (tag `rules-locked-v2`). Picks log: issue #1. Credits: CREDITS.md.\n\nNot financial advice. It's an experiment.\n")

(ROOT / "packaging/TITLES.md").write_text("""# Titles (≤ 60 characters)

1. My Desk AI vs the Weather Betting Market
2. My AI Saw the Hurricane Coming. Can It Beat Kalshi?
3. I Bet Real Money on My Own Weather AI
""")
for t in ["My Desk AI vs the Weather Betting Market", "My AI Saw the Hurricane Coming. Can It Beat Kalshi?", "I Bet Real Money on My Own Weather AI"]:
    assert len(t) <= 60, t

credits = (ROOT / "CREDITS.md").read_text().split("\n", 1)[1].strip()
(ROOT / "packaging/DESCRIPTION.md").write_text(f"""# Description

A weather AI running on my desk called Hurricane Melissa's landfall {mel['ref_error_km']} km off, three days out.
So can it beat Kalshi's daily temperature markets after fees? I backtested four players on paper, found a bug before
it cost me anything, then put $10 of real money on one locked week.

Paper backtest (TEST days only): the best player made {money(J_['pnl'])} on {J_['bets']} bets; the market's own price was
the most accurate forecast of all. Real money: {money(T['pnl'])} on {T['orders']} bets ({T['won']} won, {T['lost']} lost), and the
bot crashed on day {T['runs_completed'] + 1}.

Code, locked rules, every pick and every result: https://github.com/Tacdelgineer/desk-weather-bet

Chapters
{chapters}

Credits
{credits}

Not financial advice. It's an experiment.
""")

pk = phx["picks"][0]; c = lambda v: round(v * 100)
nws = next(v for k, v in phx["nws_pfm_max_F"].items() if "401 PM" in k)
(ROOT / "packaging/THUMBNAILS.md").write_text(f"""# Thumbnail prompts (ChatGPT) — real numbers only

One prompt per existing thumbnail. Every number below is from a results file (source in brackets).

## 1. AI vs BETTORS
Numbers: AI **{c(pk['p_side'])}%** vs market **{c(pk['price'])}%** — the buggy v1 bot was {c(pk['p_side'])}% sure Phoenix would hit
"{pk['bracket']}"; the market priced it at {c(pk['price'])}¢. The market was right (NWS forecast {nws}°F, the bot said
{phx['v1_corrected_F']:.1f}°F). [results/evidence/v1-bug/summary.json, stations.KPHX.picks[0]]

"YouTube thumbnail, 16:9, risograph print look, black paper, orange and white ink. Left: a small desk computer with a
glowing orange screen reading 'AI {c(pk['p_side'])}%'. Right: a crowd of silhouettes holding up a sign reading '{c(pk['price'])}%'.
Big bold text across the top: 'AI vs BETTORS'. High contrast, few words, no logos, no real app screens."

## 2. $10 → ?
Numbers: **$10** real-money test budget (REAL MONEY · $10 TEST); first real bet **{c(order0['limit_price'])}¢** for NO on Phoenix
"{order0['bracket']}"; it hit **{float(order0['settled_value']):.0f}°** and paid. Keep the "?": the result ({money(T['pnl'])}) is the payoff, not the thumbnail.
[results/live.json orders[0]]

"YouTube thumbnail, 16:9, risograph print look, black paper, orange and white ink. A torn paper receipt with a price
tag reading '{c(order0['limit_price'])}¢' and a thermometer reading '{float(order0['settled_value']):.0f}°'. Huge bold text: '$10 → ?'. A hurricane eye
printed faintly in the corner. High contrast, few words, no logos."

## 3. IT WAS RIGHT?
Numbers: forecast from **{mel['days_before']} days** before Hurricane Melissa's landfall, missed by **{round(mel['ref_error_km'])} km**.
[results/hurricanes.json, MELISSA, days_before {mel['days_before']}] Matches the first shot of the video (the hurricane eye).

"YouTube thumbnail, 16:9. Satellite view of a hurricane eye in grayscale infrared, a bold orange forecast line drawn
across it in risograph ink, ending at a coastline. Small label '{round(mel['ref_error_km'])} km off · {mel['days_before']} days out'. Huge bold text:
'IT WAS RIGHT?'. High contrast, few words, no logos."
""")
print("packaging written")
