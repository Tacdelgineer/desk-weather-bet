# CLAUDE.md — Desk Weather AI vs the Betting Market (tacdel video)

You are building and running a tacdel YouTube experiment end to end, then making the video files.
Before doing anything in any session, read this file, then PLAN.md, STATE.md and DECISIONS.md.

## The one question

Can a weather AI running on this DGX Spark beat Kalshi's daily temperature markets after fees?

Everything serves that question:
- the hurricanes prove the AI is good;
- the decision model is the judge;
- a $10 real-money week is the receipt.

## How to work (resume-safe)

1. **Start of every session, or when the user says "continue":** read the bottom of STATE.md. Then do the first task in PLAN.md that isn't `[x]`, `⏸` or `⚠️`.
2. **One task at a time.** When a task's CHECK passes:
   - tick it `[x]` in PLAN.md;
   - add 2–4 lines to the bottom of STATE.md (what you did, output files, next task);
   - commit and push.
3. **If a task fails 3 times:**
   - write what you tried in STATE.md;
   - mark the task `⚠️ BLOCKED` with the reason;
   - move to the next task that doesn't depend on it.
4. **Never ask the user a question mid-run.** If a choice is needed and it isn't a 🧑 step:
   - pick the simplest option that keeps the test honest;
   - log it in DECISIONS.md (one line: date, choice, why);
   - keep going.
5. **🧑 HUMAN steps:**
   - print one short block starting `🧑 NEEDED:` with exact instructions;
   - mark the step `⏸ WAITING`;
   - carry on with every task that doesn't need it.
6. **Long jobs** (model runs, downloads):
   - run them in the background, logging to `logs/<task>.log`;
   - write a done-marker `results/.done/<task>` when they finish;
   - on resume, check the marker before re-running anything.
7. **Every script must be safe to re-run.** It skips work whose output already exists (cache per date and city). An interruption must never mean starting over.
8. **Keep your context small.** Don't paste big files or logs into the conversation; read the tail.
9. **Stay inside the current session's phases.** Work only on the phases named in the current goal or request (see "Sessions" in PLAN.md). When they're done:
   - report;
   - print the exact `/goal` line for the next session;
   - stop.
   
   A fresh session per block uses fewer tokens than one long one.

## Simplification rules (the user's own rules)

- Do each step once by hand for one city and one day, check the numbers, then scale up.
- Build the simplest version first. Make it faster only if it's too slow to finish.
- Nothing gets deleted unless the checks still pass afterward.
- Automate (timers, loops) only after the manual run works.

## Honesty rules (non-negotiable)

- **Numbers come from files.** Every number in the video, script, README, stat cards or description comes from a file in `results/`. Nobody types a number.
- **Train/test split.**
  - Tune everything on the TRAIN window only: station corrections, bet thresholds, judge cut-offs.
  - Report results on the TEST window only.
  - Add a code assert that fitting never touches TEST dates.
- **Price and fees.**
  - Use the price you could actually have paid at bet time (the ask), never the final price.
  - Use Kalshi's current fee formula from its docs. Look it up; don't guess.
- **Report everything.** Losses, misses, unfilled orders and bugs you found get reported, not hidden.
- **Settle on the right station.** Weather markets settle on the NWS Daily Climate Report for the station named in each market's rules. Use that station, never the city center.

## Money and safety rules (non-negotiable)

- **Keys stay out of the repo.** Kalshi keys live outside it; the paths are in DECISIONS.md.
  - Never print, log or commit keys, key IDs or account details.
  - The only money number that may appear anywhere is this test's P&L.
- **You never place an order yourself,** in chat or with one-off commands. Only `bot/live.py` places orders, and only when ALL of these are true:
  - a `GO_LIVE` file exists in the repo root (the user creates it; it holds the budget in dollars);
  - RULES.md is committed and tagged `rules-locked`;
  - the caps below aren't hit;
  - no `STOP` file exists.
- **Hard caps inside live.py** are constants, each with a unit test:
  - total spend ≤ the number in GO_LIVE (default 10);
  - at most $1 per market;
  - at most 2 new orders per day;
  - limit orders only;
  - cancel unfilled orders after 3 hours.
- **Default is DRY_RUN.** Without GO_LIVE, live.py logs exactly what it *would* have ordered and orders nothing.
- **Test order code safely first.** If demo keys exist, test against Kalshi's demo environment (`demo-api.kalshi.co`). Otherwise, only test auth with a read-only call such as the balance.

## Video pipeline

**Pipeline.** Use the tacdel-video skill for:
- rooms, footage, stat cards and charts;
- the script format, fact check and voice;
- the naming contract.

Follow its hard rules: numbers from files, equal visual treatment, script after footage, hook before the title card, credits, and no hostnames, usernames, IPs or keys in the public repo.

**Styles:**
- riso + papercut for story;
- CRT terminal for raw output;
- **EVIDENCE** for proof (new): a real screenshot or document, an animated yellow highlighter across one line, a small source label in a corner, and paper texture.

EVIDENCE borrows explainer-channel techniques. Never copy any channel's logo or branding.

**Never generate fake images of real things.** No made-up satellite pictures, Kalshi screens or NWS reports. Use real screenshots and recordings, or clearly stylized illustrations.

**Labels on every trading scene:**
- backtest scenes: `PAPER MONEY`;
- live scenes: `REAL MONEY · $10 TEST`.

## Reports to the user

- Under 300 words, plain English.
- Explain any technical term in one line.
- End with the ONE next thing the user must do, or "nothing — still running".
