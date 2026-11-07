/* 04 · The market (26 s): how a temperature bracket pays (one real live order), the rule that settles it, and the
   settlement cross-check against the NWS climate reports. */
shot(0, 'paper', 'how a bracket pays (real order)', (lt) => {
  const O = DATA.market.order, cost = O.fill_cost + O.fee;
  PC.text('HOW A TEMPERATURE BET PAYS', 960, 140, 54, PC.C.ink);
  const dx = PC.slideIn(lt, .2);
  PC.ticket(260 + dx, 260, 1000, 380, [
    { s: `${O.city.toUpperCase()} · HIGH ON ${O.market_day}`, size: 34, y: 120 },
    { s: `"${O.bracket}"`, size: 64, y: 210 },
    { s: `bought NO at $${O.limit_price.toFixed(2)}`, size: 34, y: 290, col: PC.C.red }], 4);
  PC.text('PAYS', 1105 + dx, 400, 28, PC.C.dim); PC.text('$1', 1105 + dx, 480, 64, PC.C.ink);
  R.fade((lt - 1.6) / .4, () => { PC.text(`if the high is NOT ${O.bracket}`, 760, 740, 36, PC.C.ink); });
  R.fade((lt - 3) / .4, () => PC.text(`settled ${parseFloat(O.settled_value)}°  →  paid $${O.revenue.toFixed(2)} on $${cost.toFixed(2)} (fee incl.)`, 960, 830, 40, PC.C.red));
  PC.stamp(O.won ? 'WON' : 'LOST', 1500, 330, -.12, (lt - 3.4) / .4, 70, O.won ? PC.C.teal : PC.C.red);
  PC.dymo('REAL MONEY · $10 TEST', 1560, 600, 26, .02, (lt - .3) / .4);
  PC.src('results/live.json (Kalshi records)', (lt - .5) / .5);
}, { noCounter: true });

shot(9, 'evidence', 'evidence: the market page names its data', (lt) => evWeb(lt, 'kalshi_market', { zoom: 2.2, note: 'one station, one source: the market\u2019s own rules' }), { noCounter: true });

shot(17, 'riso', 'settlement check: 720 days', (lt) => {
  const M = DATA.market, n = M.settle_total, cols = 40, s = 26, g = 6, x0 = 960 - (cols * (s + g)) / 2, y0 = 260;
  head(lt, 'DOES KALSHI PAY ON THE NWS NUMBER?', 'every station-day in the backtest: Kalshi’s settled high vs the NWS climate report');
  const bad = new Set(M.mismatches.map(m => `${m.city}|${m.date}`)); let k = 0; const shown = Math.floor(n * clamp((lt - .6) / 2.4));
  for (let i = 0; i < n; i++) { const [x, y] = R.gridPos(i, x0, y0, s, g, cols), mis = i >= n - M.mismatches.length;
    R.tile(x, y, s, i >= shown ? 'off' : mis ? 'test' : 'pass'); }
  R.fade((lt - 3.2) / .4, () => { R.mono(`${M.settle_matches} of ${M.settle_total} match`, 960, 880, 48, R.C.orange, 'center', 800);
    R.mono(M.mismatches.map(m => `${m.city} ${m.date}: Kalshi ${parseFloat(m.settled_high)} vs NWS ${m.nws_high}`).join('   ·   '), 960, 940, 22, R.C.white, 'center', 600); });
  R.src('results/settlement_check.json', (lt - .5) / .5);
}, { noCounter: true });
shot(26, 'evidence', 'evidence: weather app shows Kalshi odds', (lt) => evWeb(lt, 'news_twc', { zoom: 2, note: 'the odds are coming to the weather app' }), { noCounter: true });
sfx(26, 'paper', .5); sfx(27.6, 'swish', .35);
sfx(.2, 'paper', .5); sfx(3.4, 'thunk', .6); sfx(9, 'paper', .5); sfx(10, 'swish', .35); sfx(17, 'whoosh', .3); sfx(20.2, 'thunk', .5);
// real footage: the NWS climate report page, in the corner of the settlement check; the market page itself
win(13, 17, 'pip', [{ src: '../../results/final_footage/rec/web_kalshi_market.mp4', title: 'kalshi.com' }], { at: 'tr', w: 480, wide: true });
win(20, 26, 'pip', [{ src: '../../results/final_footage/rec/web_nws_cli_phx.mp4', title: 'NWS climate report' }], { at: 'br', w: 520, wide: true });
