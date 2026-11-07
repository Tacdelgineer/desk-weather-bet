/* 90 · Style preview (~41 s). Six shots, one per look, every number from DATA (export.py) or GOES
   (prep_goes.py). The hook line plays over the cold open. */
const S2 = 10, S3 = 15, S4 = 23, S5 = 27, S6 = 35;

/* ---------- 1 · cold open: real GOES-19 loop, the AI's track drawing on top in riso ink ---------- */
shot(0, 'riso', 'cold open: satellite + AI track', coldOpen, { noCounter: true });   // tx/coldopen.js
sfx(.6, 'whoosh', .35); sfx(2.4, 'thunk', .5); sfx(6.6, 'tick', .4);

/* ---------- 2 · EVIDENCE: the NWS forecast with a highlighter, next to the bot's v1 number ---------- */
shot(S2, 'evidence', 'evidence: NWS vs bot', evNwsBot, { noCounter: true });
sfx(S2, 'paper', .5); sfx(S2 + .9, 'swish', .35); sfx(S2 + 1.8, 'paper', .4); sfx(S2 + 3.1, 'thunk', .5);

/* ---------- 3 · the bug: Phoenix TRAIN scatter, the v1 line extended to the October day (riso) ---------- */
shot(S3, 'riso', 'the bug: extrapolation', bugShot, { noCounter: true });
sfx(S3, 'whoosh', .3); sfx(S3 + 1.9, 'swish', .4); sfx(S3 + 4.3, 'thunk', .6);

/* ---------- 4 · CRT: the real AIFS run log scrolling ---------- */
shot(S4, 'crt', 'crt: AIFS run log', crtAifsLog, { boot: true, noCounter: true });

/* ---------- 5 · backtest: the four players' paper P&L lines racing ---------- */
shot(S5, 'riso', 'backtest race (PAPER MONEY)', backtestRace, { noCounter: true });
sfx(S5, 'whoosh', .3); sfx(S5 + 6.2, 'thunk', .5);

/* ---------- 6 · stat card: the live-week result ---------- */
shot(S6, 'riso', 'stat card (REAL MONEY)', liveCard, { noCounter: true });
for (let i = 0; i < 8; i++) sfx(S6 + .5 + i * .2, 'tick', .25);
sfx(S6 + 2.1, 'thunk', .6);
