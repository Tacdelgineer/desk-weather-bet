/* 10 · Real money (36 s, REAL MONEY · $10 TEST): the four orders from Kalshi's own records, the day-3 crash, the
   calendar of the locked week, the result card, and the owner's recording slot (the Kalshi account). */
shot(0, 'evidence', 'evidence: the 4 real orders', (lt) => {
  const O = DATA.live.orders;
  EV.text('THE FOUR REAL ORDERS', 96, 120, 48, EV.C.ink, 900, FONT.sans);
  O.forEach((o, i) => { const x = 96 + i * 440, y = 200, p = eo((lt - .3 - i * .5) / .5); if (p <= 0) return;
    EV.sheet(x, y + (1 - p) * 60, 400, 600, (i % 2 ? .01 : -.012), () => {
      EV.text(o.placed_utc.slice(0, 16).replace('T', ' ') + ' UTC', 30, 50, 18, EV.C.dim, 600);
      EV.text(o.city, 30, 110, 36, EV.C.ink, 900, FONT.sans); EV.text(`high on ${o.market_day}`, 30, 145, 20, EV.C.dim, 600);
      EV.text(`"${o.bracket}"`, 30, 210, 30, EV.C.ink, 700);
      EV.text(`bought ${o.side_held.toUpperCase()} · ${o.contracts} × $${o.limit_price.toFixed(2)}`, 30, 270, 22, EV.C.ink, 600);
      EV.text(`filled ${o.filled}/${o.contracts} · fee $${o.fee.toFixed(4)}`, 30, 305, 20, EV.C.dim, 600);
      EV.text(`settled ${parseFloat(o.settled_value)}° → ${o.market_result.toUpperCase()}`, 30, 400, 26, EV.C.ink, 700);
      const s = money(o.pnl); ctx.font = `900 56px ${FONT.sans}`; const w = ctx.measureText(s).width;
      EV.hilite(30, 500, w, 56, (lt - 2.4 - i * .35) / .4); EV.text(s, 30, 500, 56, o.won ? EV.C.ink : EV.C.red, 900, FONT.sans);
      EV.text(o.market, 30, 570, 15, EV.C.dim, 500); }); });
  EV.source('SOURCE: Kalshi /portfolio/orders, /fills, /settlements → results/live.json', 96, 1010);
  R.fade((lt - .3) / .3, () => tag('REAL MONEY · $10 TEST', 1500, 100));
}, { noCounter: true });

shot(10, 'crt', 'crt: the day-3 crash', (lt) => {
  const C = DATA.captures.crash;
  CR.statusBar(`dwb-picks.service · ${DATA.live.window[DATA.live.runs_completed]} 16:00 UTC · logs/timer_picks.log`, 'REAL LOG');
  C.forEach((l, k) => { const s = CR.typed(l, lt, .1 + k * .14, 120); if (s) CR.tx(s.slice(0, 100), 14, 46 + k * 14.5, 10, k === C.length - 1 ? CR.C.orange : CR.C.g, { wt: k === C.length - 1 ? 700 : 400 }); });
  if (lt > 3.4) CR.tx('NO PICKS · NO ORDERS · SAME CRASH EVERY DAY AFTER', 320, 340, 13, CR.C.gh, { wt: 700, align: 'center', inv: true });
}, { boot: true, noCounter: true });

shot(16, 'riso', 'the locked week: 2 of 7 days', (lt) => {
  const L = DATA.live, n = L.runs.length, s = 190, g = 30, x0 = 960 - (n * s + (n - 1) * g) / 2;
  head(lt, 'THE LOCKED WEEK', `7 daily runs, ${L.window[0]} → ${L.window[L.window.length - 1]}`);
  L.runs.forEach((r, i) => { const x = x0 + i * (s + g), y = 360, p = (lt - .5 - i * .3) / .3, ok = r.picks_job === 'ok';
    R.fade(p, () => { R.tile(x, y, s, ok ? 'pass' : 'fail'); R.mono(r.day.slice(5), x + s / 2, y - 24, 24, R.C.white, 'center', 700);
      R.mono(ok ? `${r.real_orders} orders` : 'crashed', x + s / 2, y + s / 2 + 10, 26, ok ? R.C.white : R.C.dim, 'center', 800); }); });
  R.fade((lt - 3) / .4, () => R.mono(`${L.runs_completed} days traded · ${L.runs_crashed} crashed · ${L.orders_outside_window} orders outside the week · ${L.unfilled} unfilled`, 960, 700, 30, R.C.orange, 'center', 800));
  tag('REAL MONEY · $10 TEST', 1500, 92);
  R.src('results/live.json (runs from the systemd journal)', (lt - .5) / .5);
}, { noCounter: true });

shot(22, 'riso', 'stat card (REAL MONEY)', liveCard, { noCounter: true });
recSlot('REC-01', 'Your Kalshi account: the 4 live orders and their fills (the first 2 days of the week)', 'balance, account number, name, email', 28, 36);
sfx(0, 'paper', .5); [0, 1, 2, 3].forEach(i => sfx(2.4 + i * .35, 'swish', .3)); sfx(16, 'whoosh', .3); sfx(22, 'thunk', .5);
