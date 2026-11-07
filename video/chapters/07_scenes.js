/* 07 · Backtest (30 s, PAPER MONEY): the four players racing, the market as a forecaster, and the stress tests. */
shot(0, 'riso', 'backtest race (PAPER MONEY)', backtestRace, { noCounter: true });

shot(9, 'riso', 'who prices brackets best (Brier)', (lt) => {
  const B = DATA.bt.brier, rows = [['the market’s own price', B.market_mid, R.C.orange], ['corrected AIFS', B.aifs_cor, R.C.white],
                                   ['free GFS forecast', B.gfs, R.C.dim], ['raw AIFS', B.aifs_raw, R.C.brick]];
  head(lt, 'WHO PREDICTS THE BRACKETS BEST?', `Brier score on ${B.n_markets} TEST markets · lower is better`);
  hbars(lt, rows.map(([l, v, c]) => ({ label: l, bars: [{ v, col: c, txt: v.toFixed(3) }] })), { x: 620, y: 230, w: 1000, h: 600 }, .16, { stag: .35 });
  R.fade((lt - 2.6) / .4, () => R.mono('the market already knows more than any of the forecasts', 960, 930, 30, R.C.orange, 'center', 800));
  tag('PAPER MONEY', 1580, 92);
  R.src('results/backtest.json (accuracy_brier_test)', (lt - .5) / .5);
}, { noCounter: true });

shot(18, 'riso', 'stress tests: still losing', (lt) => {
  const T = DATA.bt, cases = T.cases, players = ['gfs', 'aifs_raw', 'aifs_cor'], names = { gfs: 'free GFS', aifs_raw: 'raw AIFS', aifs_cor: 'corrected + rule' };
  head(lt, 'MAKE IT EASIER, MAKE IT HARDER', 'TEST P&L when fees go up 50% or the bet threshold moves');
  R.fade((lt - .5) / .4, () => { players.forEach((p, j) => R.mono(names[p], 760 + j * 380, 250, 24, R.C.dim, 'center', 700)); });
  cases.forEach((c, i) => { const y = 330 + i * 88, a = (lt - .6 - i * .25) / .3;
    R.fade(a, () => R.mono(c, 540, y, 24, R.C.white, 'right', 700));
    players.forEach((p, j) => { const r = T.rob.find(r => r.case === c && r.player === p); if (!r) return;
      R.fade(a - j * .4, () => R.mono(r.bets ? money(r.test_pnl) : 'no bets', 760 + j * 380, y, r.bets ? 34 : 22, r.test_pnl > 0 ? R.C.white : r.bets ? R.C.orange : R.C.dim, 'center', 800)); }); });
  R.fade((lt - 3) / .4, () => R.mono(T.any_profitable ? 'one case made money' : 'no case made money', 960, 930, 40, R.C.orange, 'center', 800));
  tag('PAPER MONEY', 1580, 92);
  R.src('results/robustness.json', (lt - .5) / .5);
}, { noCounter: true });
sfx(0, 'whoosh', .3); sfx(6.2, 'thunk', .5); sfx(9, 'whoosh', .3); sfx(18, 'whoosh', .3); sfx(21, 'thunk', .6);
