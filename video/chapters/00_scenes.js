/* 00 · Cold open (14 s). The approved preview shot, then the payoff pair: the storm miss next to the money result. */
shot(0, 'riso', 'cold open: satellite + AI track', coldOpen, { noCounter: true });
shot(10, 'riso', 'payoff: storm vs money', (lt) => {
  const G = window.GOES.MELISSA, L = DATA.live;
  R.panel(150, 250, 740, 520); R.panel(1030, 250, 740, 520);
  R.mono('THE STORM', 520, 330, 28, R.C.dim, 'center', 800);
  R.printLine(`${G.ref_error_km} km`, 520, 520, 110, R.C.white, lt / .4, 'center');
  R.mono(`off at landfall, ${G.days_before} days out`, 520, 620, 26, R.C.white, 'center', 700);
  R.mono('THE BETS', 1400, 330, 28, R.C.dim, 'center', 800);
  R.printLine(money(L.pnl), 1400, 520, 110, R.C.orange, (lt - .9) / .4, 'center');
  R.fade((lt - 1.3) / .4, () => R.mono(`${L.n_orders} real orders, ${L.won} won, ${L.lost} lost`, 1400, 620, 26, R.C.white, 'center', 700));
  R.fade((lt - .9) / .3, () => tag('REAL MONEY · $10 TEST', 1250, 220));
  R.src('results/hurricanes.json · results/live.json', (lt - .5) / .5);
}, { noCounter: true });
sfx(.6, 'whoosh', .35); sfx(2.4, 'thunk', .5); sfx(10, 'thunk', .5); sfx(10.9, 'thunk', .6);
