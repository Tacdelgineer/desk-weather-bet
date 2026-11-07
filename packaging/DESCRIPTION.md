# Description

A weather AI running on my desk called Hurricane Melissa's landfall 50.3 km off, three days out.
So can it beat Kalshi's daily temperature markets after fees? I backtested four players on paper, found a bug before
it cost me anything, then put $10 of real money on one locked week.

Paper backtest (TEST days only): the best player made +$2.94 on 310 bets; the market's own price was
the most accurate forecast of all. Real money: −$0.50 on 4 bets (2 won, 2 lost), and the
bot crashed on day 3.

Code, locked rules, every pick and every result: https://github.com/Tacdelgineer/desk-weather-bet

Chapters
0:00 Cold open
0:16 Title
0:21 Desk AI
1:02 Hurricanes
1:43 The market
2:26 The trap
3:06 The fix
3:24 Backtest
3:59 The judge
4:30 The bug
5:20 Real money
6:01 Verdict

Credits
- Weather AI: ECMWF AIFS (open weights, CC BY 4.0), © ECMWF.
- Initial conditions / open data: ECMWF open data (CC BY 4.0).
- IBTrACS v04r01 (NOAA NCEI): Knapp et al. (2010), International Best Track Archive for Climate Stewardship.
- NWS Daily Climate Reports via the Iowa Environmental Mesonet (IEM) archive.
- Satellite imagery: NOAA GOES-19 ABI Level-2 Cloud and Moisture Imagery (band 13), mesoscale sectors, via NOAA Open Data Dissemination (NODD) on AWS. Courtesy of NOAA/NESDIS.
- Kalshi market rules and order records: kalshi.com public market pages and the account's own API records (read-only).
- News screenshot: Claims Journal (Bloomberg News), "Kalshi Weather Odds Are Coming to a Weather App Near You", Aug 31, 2026.
- Product page screenshot: Indie Hackers ("Predict & Profit"), seller name blurred.
- Model card screenshot: Hugging Face, ecmwf/aifs-single-2.0.
- Decision model: Strands Decider 2B (run locally).
- Voice: ElevenLabs (eleven_v4), the channel owner's own voice.
- Visual style: built on the riso-rooms and hand-drawn-canvas-animation skills by IshaanKalra2103 (MIT), inspired by
  Kevin Ngo's "a small light, room by room" and "life of a fruit fly" (@kevin_t_ngo).
- Fonts: Inter and JetBrains Mono (SIL OFL 1.1). Terminal recordings: VHS (charmbracelet).

Not financial advice. It's an experiment.
