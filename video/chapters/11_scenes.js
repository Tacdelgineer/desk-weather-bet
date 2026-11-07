/* 11 · Verdict (16 s): the four results on one board, then the repo. */
shot(0, 'riso', 'verdict board', (lt) => {
  const G = DATA.storms.find(s => s.name === 'MELISSA').runs.find(r => r.days === 3), B = DATA.bt.brier,
        J = DATA.judge.judge, L = DATA.live;
  head(lt, 'THE VERDICT');
  const rows = [['storms', `MELISSA landfall: ${G.ref_km} km off, ${G.days} days out`, R.C.white],
                ['accuracy', `the market’s price ${B.market_mid.toFixed(3)} beats every forecast (Brier)`, R.C.white],
                ['backtest', `best player ${money(J.pnl)} on ${J.bets} bets · PAPER MONEY`, R.C.white],
                ['live', `${money(L.pnl)} on ${L.n_orders} bets · REAL MONEY · $10 TEST`, R.C.orange]];
  rows.forEach(([k, s, col], i) => { const y = 300 + i * 150, p = (lt - .5 - i * .8) / .4;
    R.fade(p, () => { R.mono(k.toUpperCase(), 380, y, 28, R.C.dim, 'right', 800); R.mono(s, 420, y, 36, col, 'left', 800); }); });
  R.fade((lt - 4.2) / .4, () => R.mono('a great forecast, priced in already', 960, 940, 40, R.C.orange, 'center', 800));
  R.src('results/hurricanes.json · backtest.json · judge.json · live.json', (lt - .5) / .5);
}, { noCounter: true });
shot(10, 'riso', 'the repo', (lt) => {
  R.printLine('EVERYTHING IS OPEN', 960, 420, 80, R.C.white, lt / .5, 'center');
  R.fade((lt - .8) / .4, () => R.mono('github.com/Tacdelgineer/desk-weather-bet', 960, 540, 44, R.C.orange, 'center', 800));
  R.fade((lt - 1.6) / .4, () => R.mono('rules locked before the money · every pick posted before it settled', 960, 620, 28, R.C.white, 'center', 600));
  R.fade((lt - 2.4) / .4, () => R.mono('Not financial advice. It’s an experiment.', 960, 760, 26, R.C.dim, 'center', 600));
}, { noCounter: true });
[0.5, 1.3, 2.1, 2.9].forEach(t => sfx(t, 'thunk', .4)); sfx(10, 'whoosh', .3);
// slow push-ins so the board never sits still (it holds longest on the voice clock)
win(5, 10, 'punch', [], { k: 1.08, cx: 120, cy: 600 });
