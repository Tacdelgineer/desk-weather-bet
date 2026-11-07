/* 05 · The trap (36 s): a $67 bot listing (EVIDENCE, seller name blurred), the wrong spot, the afternoon peak,
   raw AI vs the free forecast. */
shot(0, 'evidence', 'evidence: a $67 bot listing', (lt) => evWeb(lt, 'bot_listing', { zoom: 2.2, note: 'a weather bot for sale, built on the free GFS forecast' }), { noCounter: true });
sfx(0, 'paper', .5); sfx(1.6, 'swish', .35);
/* (was) 05 · The trap (20 s): the AI's grid point is not the thermometer the market pays on; raw AI vs the free forecast. */
shot(8, 'riso', 'wrong spot: grid point vs station', (lt) => {
  const L = DATA.la_grid, st = DATA.stations.find(s => s.station === 'KLAX');
  head(lt, 'THE MARKET PAYS ON ONE THERMOMETER', L.name);
  const c = [960, 560], k = 3600, P = ([la, lo]) => [c[0] + (lo - L.station[1]) * k * Math.cos(L.station[0] * Math.PI / 180), c[1] - (la - L.station[0]) * k];
  const [sx, sy] = P(L.station), [gx, gy] = P(L.grid), p = eo((lt - .8) / .6), p2 = eo((lt - 1.6) / .8);
  ctx.beginPath(); ctx.arc(sx, sy, Math.max(0, 26 * back(p)), 0, 7); R.fills(R.C.white); R.fade(p, () => R.mono('the airport thermometer', sx + 44, sy + 8, 26, R.C.white, 'left', 800));
  if (p2 > 0) { ctx.save(); ctx.setLineDash([12, 10]); ctx.lineWidth = 4; ctx.strokeStyle = R.C.dim; ctx.beginPath(); ctx.moveTo(sx, sy); ctx.lineTo(lerp(sx, gx, p2), lerp(sy, gy, p2)); ctx.stroke(); ctx.restore(); }
  R.fade((lt - 2.3) / .3, () => { ctx.beginPath(); ctx.arc(gx, gy, 26, 0, 7); R.fills(R.C.paper, R.P.o); ctx.lineWidth = 4; ctx.strokeStyle = R.C.orange; ctx.stroke();
    R.mono('the AI’s nearest grid point', gx + 44, gy + 8, 26, R.C.orange, 'left', 800);
    R.mono(`${L.km} km apart`, (sx + gx) / 2 - 40, (sy + gy) / 2, 30, R.C.white, 'right', 800); });
  R.fade((lt - 3.6) / .4, () => R.mono(`the real high was ${st.raw_bias}°F warmer than the raw AI, on average (TEST, ${st.n} days)`, 960, 920, 30, R.C.orange, 'center', 800));
  R.src('results/aifs_la_sanity.json (grid point) · results/cities.json · results/forecasts.csv', (lt - .5) / .5);
}, { noCounter: true });

shot(18, 'riso', 'afternoon peak: 6-hourly samples', (lt) => {
  const S = DATA.stations, C = S.find(s => s.station === 'KMDW');
  head(lt, 'THE AI LOOKS AT THE SKY EVERY 6 HOURS', 'its daily high = the warmest of 4 snapshots · the real peak falls in between');
  // left: an illustrated day (EXAMPLE), with Chicago's real snapshot hours marked on it
  const b = { x: 140, y: 300, w: 760, h: 420 }, X = h => b.x + h / 24 * b.w, Y = h => b.y + b.h * (.55 - .42 * Math.cos((h - 15) / 24 * 2 * Math.PI));
  ctx.lineWidth = 3; ctx.strokeStyle = R.C.dim; ctx.beginPath(); ctx.moveTo(b.x, b.y + b.h); ctx.lineTo(b.x + b.w, b.y + b.h); ctx.stroke();
  const pc = clamp((lt - .4) / 1.4); ctx.lineWidth = 6; ctx.strokeStyle = R.C.white; ctx.beginPath();
  for (let h = 0; h <= 24 * pc; h += .25) h ? ctx.lineTo(X(h), Y(h)) : ctx.moveTo(X(h), Y(h)); ctx.stroke();
  [0, 6, 12, 18, 24].forEach(h => R.mono(`${String(h % 24).padStart(2, '0')}:00`, X(h), b.y + b.h + 34, 18, R.C.dim, 'center', 600));
  C.lst_samples.forEach((h, i) => R.fade((lt - 2 - i * .25) / .3, () => { ctx.beginPath(); ctx.arc(X(h), Y(h), 14, 0, 7); R.fills(R.C.paper, R.P.o); ctx.lineWidth = 4; ctx.strokeStyle = R.C.orange; ctx.stroke(); }));
  R.fade((lt - 3.2) / .4, () => { const hp = 15; ctx.save(); ctx.setLineDash([8, 8]); ctx.lineWidth = 3; ctx.strokeStyle = R.C.white; ctx.beginPath(); ctx.moveTo(X(hp), Y(hp)); ctx.lineTo(X(hp), b.y - 20); ctx.stroke(); ctx.restore();
    R.mono('real peak, mid-afternoon', X(15), b.y - 30, 22, R.C.white, 'center', 800); });
  R.fade((lt - 2) / .3, () => R.mono(`${C.city}: snapshots at ${C.lst_samples.map(h => String(h).padStart(2, '0') + ':00').join(', ')} local standard time`, b.x, b.y + b.h + 80, 20, R.C.orange, 'left', 700));
  example(b.x, b.y - 70, clamp((lt - .4) / .3), 'EXAMPLE DAY');
  // right: every station's real average gap (actual − raw AI), TEST window
  R.fade((lt - 3.6) / .3, () => R.mono('real high − AI high, average (TEST)', 1400, 270, 22, R.C.dim, 'center', 700));
  hbars(lt, S.map(s => ({ label: s.city, bars: [{ v: s.peak_test, col: R.C.orange, txt: `+${s.peak_test.toFixed(1)}°F` }] })), { x: 1220, y: 300, w: 420, h: 520 }, 7, { t0: 3.8, stag: .2 });
  R.src('results/v2/corrections.json (bias_raw_test) · results/cities.json', (lt - .5) / .5);
}, { noCounter: true });

shot(27, 'riso', 'raw AI vs free GFS, per station', (lt) => {
  const S = DATA.stations;
  head(lt, 'RAW AI vs THE FREE FORECAST', 'average miss on the daily high, °F, TEST window · shorter is better');
  hbars(lt, S.map(s => ({ label: s.city, bars: [{ v: s.gfs, col: R.C.dim, txt: `${s.gfs}°` }, { v: s.raw, col: R.C.brick, txt: `${s.raw}°` }] })),
        { x: 470, y: 210, w: 1150, h: 680 }, 7);
  legend([['free GFS forecast', R.C.dim], ['raw AIFS', R.C.brick]], 600, 950, (lt - .3) / .4);
  R.src('results/forecasts.csv (TEST rows)', (lt - .5) / .5);
}, { noCounter: true });
sfx(8.8, 'thunk', .4); sfx(10.3, 'thunk', .5); sfx(18.0, 'whoosh', .3); sfx(20.0, 'tick', .3); sfx(27.0, 'whoosh', .3);
