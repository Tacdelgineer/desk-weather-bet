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

shot(9, 'evidence', 'evidence: the settlement rule', (lt) => {
  const s = DATA.market.rules, key = s.match(/at [A-Z][a-z]+ \(CLI[A-Z]+\)/)[0], size = 30;
  EV.sheet(170, 260, 1580, 420, -.006, () => {
    EV.text('Kalshi market rules · KXHIGHTPHX (daily high, Phoenix)', 50, 70, 24, EV.C.dim, 600, FONT.sans);
    ctx.font = `500 ${size}px ${FONT.serif}`; const words = s.split(' '); let line = '', y = 160, lines = [];
    words.forEach(w => { const t = line ? line + ' ' + w : w; if (ctx.measureText(t).width > 1460 && line) { lines.push(line); line = w; } else line = t; }); lines.push(line);
    lines.forEach((l, i) => { const k = l.indexOf(key.split(' ')[1]);
      if (k >= 0) { ctx.font = `500 ${size}px ${FONT.serif}`; const x = 60 + ctx.measureText(l.slice(0, k)).width, w = ctx.measureText(key.split(' ').slice(1).join(' ')).width; EV.hilite(x, y + i * 56, w, size, (lt - 1) / .5); }
      EV.text(l, 60, y + i * 56, size, EV.C.ink, 500, FONT.serif); });
  });
  R.fade((lt - 2) / .4, () => EV.text('CLIPHX = the NWS Daily Climate Report for Phoenix', 960, 800, 34, EV.C.ink, 800, FONT.sans, 'center'));
  EV.source('SOURCE: Kalshi API market rules (results/cities.json)', 96, 1010);
}, { noCounter: true });

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
sfx(.2, 'paper', .5); sfx(3.4, 'thunk', .6); sfx(9, 'paper', .5); sfx(10, 'swish', .35); sfx(17, 'whoosh', .3); sfx(20.2, 'thunk', .5);
