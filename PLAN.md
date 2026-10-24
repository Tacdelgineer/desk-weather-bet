# PLAN.md — "My Desk AI vs the Weather Betting Market"

Status keys:
- `[ ]` to do
- `[x]` done
- `⏸` waiting (on the user, or on the calendar)
- `⚠️` blocked

Every task has a CHECK. Don't tick a task until its CHECK passes. 🧑 = needs the user.

## Decisions (user: edit before starting · Claude: read, don't change)

- **Weather AI:** ECMWF AIFS Single v2 (open weights on Hugging Face: `ecmwf/aifs-single-2.0`), run on this DGX.
- **Extra hurricane models:** none by default. Add GraphCast only if it installs in under 2 hours.
- **Cities:** the 6 Kalshi daily-high cities with the most volume.
- **Backtest window:** the most recent ~120 days with full data. First half = TRAIN, second half = TEST.
- **Players:**
  - free GFS forecast (the method the $67 bots sell);
  - raw AIFS;
  - corrected AIFS + one-line rule;
  - corrected AIFS + decision-model judge.
  
  Market prices are also scored as a forecast, as the accuracy bar.
- **Decision model:** Strands Decider 2B via Ollama (ON).
- **Live test:** 7 days, $10, at most $1 per market, the earliest available market for each date (avoid same-day).
- **Repo:** `desk-weather-bet`. Public from the start of the live week at the latest.
- **Key paths (outside the repo):** `~/.kalshi/prod.pem` + `~/.kalshi/prod_key_id`; optional `~/.kalshi/demo.pem` + `~/.kalshi/demo_key_id`.

## Sessions (one fresh session per block keeps token use low)

| Session | Phases | Done when | Effort |
|---|---|---|---|
| 1 | 0–2 | AIFS runs on the DGX and the hurricane scores are saved | medium |
| 2 | 3–6 | backtest + judge results saved | high |
| 3 | 7.1–7.5 | rules locked, bot tested, daily timer running (DRY_RUN until GO_LIVE) | high |
| — | 7.6 | the live week: 7 calendar days. The user only creates GO_LIVE | — |
| 4 | 8–9 | footage, script and voice done; live chapters 09–10 left as slots | medium |
| 5 | 10 | live results in, full render with recording slots, packaging | medium |

Start each session with one line (Claude Code reads CLAUDE.md on its own):
`/goal Every task in Phases X–Y of PLAN.md is [x], ⏸ or ⚠️ — print those tasks' checklist to prove it.`

If a session stops, type `continue` in the same conversation.

---

## Phase 0 — Setup

- [x] **0.1 Repo skeleton.**
  - Folders: `fetch/ model/ backtest/ bot/ video/ results/ logs/`.
  - Files: README stub, `STATE.md`, `DECISIONS.md`, `CREDITS.md`.
  - `.gitignore`: `results/final_footage`, `*.mp4`, `*.grib*`, `data/`, `.env`, `*.pem`, `GO_LIVE`, `STOP`.
  - CHECK: first commit pushed; `git check-ignore` confirms `.pem` and `GO_LIVE` are ignored.
- ⚠️ BLOCKED (no NVIDIA GPU on this machine — nvidia-smi missing; env itself done, running on CPU) **0.2 Environment.** Python env with uv.
  - CHECK: `nvidia-smi` works; log the free disk space (want >200 GB) and the CPU type. This box is ARM64, so expect some packages to need ARM builds.
- ⏸ WAITING (ElevenLabs key/voice ID not in env; Kalshi key + $10 + git push confirmed) **0.3 🧑 H1 — print once, don't wait for it.**
  1. Kalshi: create an API key in account settings and save the private key. It's shown only once.
  2. Put the key file at `~/.kalshi/prod.pem` and the key ID in `~/.kalshi/prod_key_id`.
  3. Make sure the account has $10.
  4. Optional: a demo account + demo key in the same folder.
  5. Confirm the ElevenLabs key and voice ID from the last video are in the environment, and that `git push` to GitHub works.
  
  Mark ⏸ and continue.

## Phase 1 — Get the weather AI running (riskiest, so first)

- [ ] **1.1 Install and run once.** Install `anemoi-inference` and AIFS Single v2, following the model card's demo notebook. If a package won't build on ARM64 (e.g. a fast-attention library), use the documented fallback and log it.
  - CHECK: a 10-day forecast from today's ECMWF open data exists, and Los Angeles' 2 m temperature looks sane (print 3 values next to current NWS observations).
- [ ] **1.2 Past start dates.** Rerun AIFS for one past date (e.g. 2025-10-01 00z), using start data from ECMWF's open-data copy on AWS (it goes back to April 2024).
  - CHECK: a forecast exists for that date.
  - If this is impossible, fall back to archived AIFS forecasts (ECMWF's archive, from Feb 2024). Log it in DECISIONS.md and say so in the next report.
- [x] **1.3 Timing.** Measure the time per forecast run and estimate total runtime for every run in this plan.
  - CHECK: the numbers are in STATE.md. If the total is over 24 h, shrink the window and log it.

## Phase 2 — Hurricanes (Act 1)

- [x] **2.1 Pick storms.** Choose 3 Atlantic hurricanes from 2025 with landfall and big news coverage, from IBTrACS. Log the choice.
- [x] **2.2 Run and track.** Run AIFS from 5, 3 and 1 day(s) before each landfall. Track the storm center every 6 h: the lowest sea-level pressure near the last position.
- [ ] **2.3 Score.** Compare against the IBTrACS best tracks: km error at 24/48/72/120 h, plus landfall position error.
  - CHECK: one storm, one time step hand-checked against the printed IBTrACS row.
- [ ] **2.4 Save and gather footage.**
  - Save `results/hurricanes.json` (tracks + errors).
  - Download real NOAA GOES satellite loops for the cold open; add the credit line to CREDITS.md.
  - CHECK: files exist and the credits are written.

## Phase 3 — Kalshi data

- [x] **3.1 Cities and stations.** List the daily-high series (`KXHIGH*`) and pick 6 US cities by volume. Read each market's rules for its settlement station.
  - CHECK: `results/cities.json` maps city → station → series.
- [x] **3.2 Market history.** For the window, pull:
  - every settled bracket market;
  - its settled temperature;
  - price history, so you know the ask at bet time.
  
  Bet time = the morning before the market's date (same as live). Also record when Kalshi opens each date's markets.
  - CHECK: for one market, print our recorded ask next to Kalshi's candle; they match.
- [x] **3.3 Cross-check settlement.** Pull the NWS Daily Climate Report highs for the same stations and dates.
  - CHECK: at least 98% match; mismatches listed.
- [x] **3.4 Fees.** Find Kalshi's current fee formula in its docs and implement `fee()`.
  - CHECK: unit tests pass on 2 worked examples from the docs.

## Phase 4 — Forecasts for the backtest

- [x] **4.1 AIFS daily highs.** Run AIFS once per day in the window, using the run that was available before bet time. Take each station's nearest grid point. Daily high = max of the 6-hourly 2 m temperatures, plus any max-temperature field the model outputs.
  - CHECK: one city and one day by hand first, then all.
- [x] **4.2 Free-forecast baseline.** Get GFS forecasts for the same stations and dates from Open-Meteo's historical-forecast data.
  - CHECK: one day by hand matches.
- [x] **4.3 Station correction (TRAIN only).** For each station, fit `actual_high ≈ a + b × model_high` and measure how spread out the errors are. Save before/after error in °F for the "trap" chapter.
  - CHECK: TEST error printed, and the assert proves no TEST data was used in fitting.

## Phase 5 — The backtest (Act 3)

- [x] **5.1 Probabilities.** Turn each forecast into a probability for each temperature bracket: a normal curve around the corrected high, using that station's error spread.
- [x] **5.2 Simulate betting.** Every player uses the same rules:
  - buy YES or NO at the ask if `probability − price − fee > threshold`;
  - at most $1 per market;
  - tune the threshold on TRAIN, report on TEST.
  - CHECK: 5 random bets traced end to end (forecast → probability → price → fee → settlement → P&L) in `logs/handcheck.md`.
- [x] **5.3 Results.** For each player: P&L, number of bets, win rate, fees paid, P&L by city and equity curves. Save to `results/backtest.json` + CSV.
  - CHECK: the per-bet P&L sums to the total.
- [x] **5.4 Robustness.** Rerun with fees ×1.5 and the threshold moved up and down. Note whether the conclusion still holds.
  - CHECK: table saved.

## Phase 6 — The judge (Act 4)

- [x] **6.1 Run the decision model.** Run Strands Decider 2B locally. For each candidate bet, give it a small JSON (city, forecast, probability, price, station error history, spread, volume) and the options bet/skip.
  - CHECK: one call by hand returns probabilities.
- [ ] **6.2 Judge vs rule.** On TEST, compare the judge with the one-line rule ("bet if edge > X cents", with X from TRAIN).
  - CHECK: `results/judge.json` saved.
- [ ] **6.3 Explainer examples.** Save 3 example decisions with the judge's probabilities for the 60-second explainer scene.

## Phase 7 — Lock the rules, then go live (Act 5)

- [ ] **7.1 Lock the rules.**
  1. Write RULES.md in plain English: which player goes live, the threshold, the caps and the dates. Pick the best player on TEST; if nothing wins, use corrected AIFS + rule, and say so.
  2. Commit, tag `rules-locked`, push.
  3. Open a GitHub issue named "Live picks log". Post RULES.md's SHA-256 and the commit hash as the first comment. GitHub comment times are set by the server and can't be back-dated; plain git commit dates can be.
  - CHECK: issue URL in STATE.md.
- [ ] **7.2 Build `bot/live.py`.**
  - Each morning: get the latest data → run AIFS → compute probabilities → choose picks → post picks to the issue → if GO_LIVE, place limit orders → log.
  - Next morning: settle and update P&L.
  - Unit tests for every cap and for DRY_RUN.
  - CHECK: tests pass, and one full DRY_RUN is run by hand.
- [ ] **7.3 Order test.** With demo keys, place and cancel one demo order. Without them, make a read-only balance call.
  - CHECK: logged.
- [ ] **7.4 🧑 H2 — GO_LIVE.** Print: "Read RULES.md. If you're OK with it, run: `echo 10 > GO_LIVE` in the repo folder." Until then, the daily job keeps running in DRY_RUN. ⏸
- [ ] **7.5 Automate.** Only after 7.2's manual run worked: add a daily systemd user timer (or cron) for the morning run, plus the settle job.
  - CHECK: the timer is listed, and its first automatic run is logged.
- [ ] **7.6 Live week.** 7 days ⏸ (calendar). Do Phases 8–10 meanwhile. On day 8: settle, write `results/live.json`, include unfilled orders.

## Phase 8 — Footage (tacdel-video pipeline)

- [ ] **8.1 Outline.** Write the chapter outline to `video/OUTLINE.md`, from the chapter list below.
- [ ] **8.2 Rooms.** Build rooms from the results files, including the new EVIDENCE room type.
- [ ] **8.3 Claude-made recordings,** 1920×1080 at 30 fps.
  - VHS terminal recordings of real commands: an AIFS run, `nvidia-smi`, a live.py DRY_RUN.
  - Playwright recordings of public pages: one Kalshi temperature market, one NWS climate report, the AIFS model card, the GitHub picks issue.
  - CHECK: every file plays.
- [ ] **8.4 Render.** Footage, stat cards and charts, following the naming contract, plus ORDER.txt. Leave chapter 09–10 slots for the live result.
  - Every manual recording gets a placeholder slate, the same as the Kalshi video. Each slate is a full-screen card that says `📼 RECORDING SLOT`, what to record, and how many seconds.
  - Only two slots:
    - the user's Kalshi account showing the live orders and fills;
    - an optional 3-second phone clip of the DGX on the desk.
- [ ] **8.5 Lock footage.** No new rooms after this.

## Phase 9 — Script and voice

- [ ] **9.1 Script.** Write it to the footage using the skill's template, following these rules:
  - the first sentence matches the title, and the first shot matches the thumbnail (the hurricane eye);
  - reach the betting part by ~2:30;
  - put the twist around 3:00;
  - end on the payoff.
- [ ] **9.2 Fact check** against the results files, then fix.
- [ ] **9.3 Voice.** ElevenLabs, the user's v2 voice, one chapter per generation, into `video/voice/`.
  - CHECK: durations logged.

## Phase 10 — Assembly and packaging

- [ ] **10.1 After the live week.** Render chapters 09–10 with the live numbers, then rerun the fact check.
- [ ] **10.2 Full render.** Use ffmpeg to put the voice and footage together following the Shots lists, recording slates included, and set loudness to −14 LUFS → `results/full_render.mp4`. Also write `video/RECORDINGS.md`: each slot's timestamp, what to record and its length.
  - CHECK: the video plays end to end, and the slot timestamps match the file.
- [ ] **10.3 Packaging.**
  - a title + 2 backups (≤60 characters);
  - a description with chapters, credits and "Not financial advice. It's an experiment.";
  - a README with results from files.
  
  Thumbnails: the user made them in ChatGPT; they show a price tag (31¢), a temperature (74°) and a market price (12%). Pick ONE real example from the results files for each number, and write updated ChatGPT prompts that use those real numbers. A thumbnail number must be true too.
- [ ] **10.4 🧑 H3 — recordings + edit.** In CapCut, replace the slates in `full_render.mp4` with the recordings listed in RECORDINGS.md. ⏸
- [ ] **10.5 🧑 H4.** Pick 2–3 thumbnails for YouTube's Test & Compare, then upload. ⏸

---

## Chapters (video order)

| NN | Chapter | What it shows |
|---|---|---|
| 00 | cold open | real satellite loop + the AI's tracks. "Can an AI that saw this coming beat the weather betting market?" |
| 01 | title | title card, after the hook |
| 02 | desk AI | what the AI is, running here (terminal + evidence) |
| 03 | hurricanes | 3 storms, each miss in km |
| 04 | the market | how a temperature bet pays; the NWS report as evidence; the Weather Channel app now shows Kalshi odds |
| 05 | the trap | the $67 bots, the afternoon peak, the wrong station |
| 06 | the fix | before/after error |
| 07 | backtest | the players, PAPER MONEY, fees, the number |
| 08 | the judge | decision models in 60 s; judge vs one-line rule |
| 09 | real money | the $10 week, timestamped picks, fills, result |
| 10 | verdict | what it means, the repo, the call to action |
