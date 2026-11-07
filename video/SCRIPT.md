# My Desk AI vs the Weather Betting Market — script v1

Manual-mode footage (chapters/NN_scenes.js, locked in 8.5) with the voice written to it. Each **Shots** line names the
spoken phrase a shot starts on; tools/warp.py lines the footage up to those words for the assembled render.
Main cast: the AI (AIFS, on the DGX), the market, the judge; yardstick: the free GFS forecast.
Ideas in order: the AI is good (storms) → how a bet pays → the traps → the fix → paper results → the judge → the bug
→ real money → verdict. The money result is kept for chapter 10 (owner, 2026-11-07).
Left the voice (on screen and in Check lines only): exact km per run, per-station errors, Brier scores, every
stress-test cell, fees, the judge's inputs.

---

## 00. Cold open

**Voice**

Three days before Hurricane Melissa hit Jamaica, an AI running on my desk drew this line.

It missed the landfall by about fifty kilometres.

So can an AI that saw this coming beat the weather betting market?

**Shots**
- 0.0 s, before the first word (voice/edits.json "leads") → MELISSA's real GOES-19 loop, the AI's track printing on
- "So can an AI that saw this coming" → the question card

**Check**
- MELISSA, 3 days before, landfall miss 50.3 km: results/hurricanes.json (storms[MELISSA].runs[days_before=3].ref_error_km).

---

## 02. Desk AI

**Voice**

This is AIFS, the weather AI from the European forecast centre, ECMWF. The weights are open, so it runs right here, on a desk computer called a DGX Spark. Here's a real run.

One step of the forecast, six hours of weather, takes about three seconds. My old mini PC needed almost nine minutes for the same step. A whole ten-day forecast now takes about three minutes.

First check: Los Angeles. The AI against what the airport station actually measured. Within two degrees Celsius, every time.

And it's not a toy. ECMWF runs this same model for real, four times a day.

**Shots**
- "This is AIFS" → CRT replay of the real run log; split with the real terminal recording
- "One step of the forecast" → mini PC vs DGX bars
- "First check" → LA forecast vs measured
- "And it's not a toy" → EVIDENCE: the public model card

**Check**
- 2.97 s per 6-h step, 528 s on the mini PC, 10-day run 170.2 s: results/timing.json (measured, previous_minipc_cpu).
- within 2 °C: results/aifs_la_sanity.json (diffs 1.8, 0.7, −1.7, 0.0).
- four times a day: results/evidence/web/aifs_card.png (model card text).

---

## 03. Hurricanes

**Voice**

Weather AIs made their name on hurricanes, so that's where I started. Three big Atlantic storms from last year. For each one, I took the AI's forecast from three days before. Melissa: the line runs almost on top of the real track.

Imelda, passing Bermuda: about sixty kilometres off.

Erin, off the Outer Banks: about a hundred and twenty.

Here's every run. Five days out, it can be way off. One day out, three of the four land within about thirty-five kilometres. Isaias, this year's storm, ran right here on the desk. So the AI is good. The question is whether good is worth money.

**Shots**
- "Weather AIs made their name" → MELISSA loop + track
- "Imelda" → IMELDA loop + track
- "Erin" → ERIN loop + track
- "Here's every run" → the miss table

**Check**
- IMELDA 63.4 km, ERIN 118.2 km (3 days): results/hurricanes.json.
- one day out: MELISSA 30.6, IMELDA 23.3, ISAIAS 32.6 (results/isaias_local.json), ERIN 76.8 → three of four under 35 km.
- five days out: IMELDA 1394.4 km.

---

## 04. The market

**Voice**

Now the betting part. Kalshi runs a market every day on the high temperature in big US cities. I picked the six busiest. The bets come in brackets. This was one of my real bets: Phoenix, eighty-five to eighty-six degrees. I bought NO for fifty-four cents. If the high lands anywhere else, it pays a dollar. It hit eighty-seven. Paid.

Who decides the high? The market's own rules: one airport station, and the data from The Weather Company.

I checked every backtest day against the National Weather Service's own climate reports. Seven hundred eighteen out of seven hundred twenty matched.

And this is going mainstream. Kalshi's odds are coming to the weather app on your phone.

**Shots**
- "Now the betting part" → the real order as a ticket (REAL MONEY · $10 TEST)
- "Who decides the high" → EVIDENCE: the Kalshi market page, highlighter on "according to The Weather Company"
- "I checked every backtest day" → 720 tiles, 718 match; NWS report page in the corner
- "And this is going mainstream" → EVIDENCE: the news article, highlighter on the weather-app line (no numbers)

**Check**
- the order: results/live.json orders[0] (NO at 0.54, settled 87.00, revenue 1.0).
- 718 / 720: results/settlement_check.json.
- six busiest: results/cities.json (volume_30d).
- weather app: results/evidence/web/news_twc.png; data source: results/evidence/web/kalshi_market.png.

---

## 05. The trap

**Voice**

There are people selling bots for this. This one is a weather bot for sixty-seven dollars, built on the free GFS forecast.

But there's a trap. The market pays on one thermometer. In Los Angeles, it's at the airport, and the AI's nearest point is eight kilometres away.

There's a second trap. The AI only looks at the sky every six hours. The real peak, mid-afternoon, falls in between. So its high reads cold. In LA, by six degrees on average. In New York, almost nothing.

Straight out of the box, the raw AI is worse than the free forecast in four of six cities.

**Shots**
- "There are people selling bots" → EVIDENCE: the listing (seller name blurred)
- "But there's a trap" → grid point vs station
- "There's a second trap" → 6-hourly snapshots (EXAMPLE day) + every station's gap
- "Straight out of the box" → raw AI vs GFS per station

**Check**
- $67, GFS: results/evidence/web/bot_listing.png (the page's own words).
- 8.3 km: video/export.py from results/aifs_la_sanity.json grid point + results/cities.json.
- LA 6.02 °F, NYC 0.28 °F: results/v2/corrections.json (−bias_raw_test).
- worse in LA, Miami, Chicago, Phoenix (4 of 6): results/forecasts.csv TEST rows (MAE raw vs gfs).

---

## 06. The fix

**Voice**

The fix is simple. For each station, take the AI's average miss over the last thirty days, and add it back.

After the fix, the average miss drops from three and a half degrees to under two. Better than the free forecast. New York got a little worse. It was fine to begin with.

**Shots**
- "The fix is simple" → before/after per station
- "After the fix" → 3.49 → 1.93 °F

**Check**
- 3.49 → 1.928, GFS 3.281: results/v1_vs_v2.json (v2.test_mae_F). NYC 1.24 → 1.32: results/forecasts.csv.

---

## 07. Backtest

**Voice**

So, the backtest. Sixty days I didn't tune on. Four players, same rules, paper money: the free forecast, the raw AI, the corrected AI with a simple rule, and the corrected AI with a judge. Three of them lose. The simple rule loses the most: over a hundred dollars.

Here's why. Score every forecast against what really happened, and the market's own price beats all of them. The market already knows.

I made it easier. I made it harder. Higher fees, pickier thresholds. No version made money.

**Shots**
- "So, the backtest" → four P&L lines racing (PAPER MONEY)
- "Here's why" → Brier bars
- "I made it easier" → stress-test table

**Check**
- 60 TEST days 2026-08-22 → 2026-10-20: results/v1_vs_v2.json (split); P&L: results/backtest.json, results/judge.json.
- market Brier 0.1054 lowest: results/backtest.json (accuracy_brier_test).
- no case profitable: results/robustness.json (any_case_profitable_on_test = false).

---

## 08. The judge

**Voice**

The fourth player has a judge: a small decision model, running here too. It reads each bet's numbers and says bet, or skip. Here it says bet.

Here it skips a bet the simple rule would take. That one would have lost a dollar.

And here, a close call. Right on the line, so it skips.

Over sixty days, the judge ends up two dollars and ninety-four cents ahead. The simple rule: down a hundred and six. That's about break-even. Not proof of an edge.

**Shots**
- "The fourth player has a judge" → CRT: judge example 1 (bet)
- "Here it skips" → CRT: example 2 (skip, the rule bets, −$1.00)
- "And here, a close call" → CRT: example 3 (P(bet) 0.77 = cut-off, skip)
- "Over sixty days" → judge vs rule cards (PAPER MONEY)

**Check**
- examples: results/judge_examples.json. +2.94 / −106.46: results/judge.json (test.judge, test.rule).

---

## 09. The bug

**Voice**

And here's the part I almost missed. I nearly went live with a bug. The first version fit a straight line for each station, on summer days. In October, Phoenix's forecast was colder than anything in that summer cloud. The line just kept going, and said eighty-five and a half degrees.

The National Weather Service said seventy-nine.

I caught it in a dry run, with no money. I locked new rules, version two, and posted their fingerprints on GitHub before any real bet.

That bug would have bet on a six-cent long shot, calling it a huge edge. The real high was seventy-seven.

On paper, version one of the live player lost ninety-three dollars. Version two made two dollars ninety-four. But I designed version two after seeing those days. So the only honest test left was real money.

**Shots**
- "And here's the part" → Phoenix TRAIN scatter, the v1 line extended (PAPER MONEY)
- "The National Weather Service said" → EVIDENCE: the NWS forecast vs the bot's log
- "I caught it in a dry run" → CRT: git tags + the issue's SHA-256s
- "That bug would have bet" → stat card NWS 79 °F → BOT 85.5 °F, edge 0.85 at 6¢
- "On paper" → stat card v1 −$93.15 → v2 +$2.94

**Check**
- 76.31 raw, train min 90.42, v1 85.49, NWS 79, prelim 77, edge 0.8453 at 0.06: results/evidence/v1-bug/summary.json.
- −93.15 → +2.94: results/v1_vs_v2.json. Hashes: results/evidence/captures/.

---

## 10. Real money

**Voice**

Then, ten dollars of real money, for one locked week. On days one and two, the bot placed four bets. Every pick was posted on GitHub before its market settled. Two won. Two lost.

Then, on day three, it crashed. Kalshi started reporting one settled temperature as a range instead of a number, and my bot choked on it. Every morning, for the rest of the week.

So only two of the seven days traded. No order outside the week, nothing left unfilled.

The result: minus fifty cents.

Here's the account itself.

**Shots**
- "Then, ten dollars" → EVIDENCE: the four orders from Kalshi's records; split with the public picks issue
- "Then, on day three" → CRT: the real traceback
- "So only two of the seven days" → the week calendar
- "The result" → stat card −$0.50 (REAL MONEY · $10 TEST)
- "Here's the account itself" → REC-01 slot (owner's screen recording)

**Check**
- 4 orders, 2 won, 2 lost, −0.4959, 2 of 7 runs, 0 outside, 0 unfilled: results/live.json.
- the range string: results/evidence/captures/crash_traceback_2026-10-28.txt.

---

## 11. Verdict

**Voice**

So, can an AI that saw a hurricane coming beat the weather betting market? Not yet. The forecast is great. But the market's price is better, because it already knows what the AI knows. My best player was about break-even on paper, and down fifty cents with real money.

Three things you can use. One: a great forecast isn't an edge if the market already has it. Two: check where the market measures, and when. Three: test your bot on days you didn't tune it on.

Everything is open: the code, the rules, every pick. Would you have trusted that eighty-five and a half degrees?

**Shots**
- "So, can an AI" → verdict board
- "Everything is open" → the repo card

**Check**
- all numbers as above (hurricanes.json, backtest.json, judge.json, live.json).
