/* 05 · The trap (20 s): the AI's grid point is not the thermometer the market pays on; raw AI vs the free forecast. */
shot(0, 'riso', 'wrong spot: grid point vs station', (lt) => {
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

shot(10, 'riso', 'raw AI vs free GFS, per station', (lt) => {
  const S = DATA.stations;
  head(lt, 'RAW AI vs THE FREE FORECAST', 'average miss on the daily high, °F, TEST window · shorter is better');
  hbars(lt, S.map(s => ({ label: s.city, bars: [{ v: s.gfs, col: R.C.dim, txt: `${s.gfs}°` }, { v: s.raw, col: R.C.brick, txt: `${s.raw}°` }] })),
        { x: 470, y: 210, w: 1150, h: 680 }, 7);
  legend([['free GFS forecast', R.C.dim], ['raw AIFS', R.C.brick]], 600, 950, (lt - .3) / .4);
  R.src('results/forecasts.csv (TEST rows)', (lt - .5) / .5);
}, { noCounter: true });
sfx(.8, 'thunk', .4); sfx(2.3, 'thunk', .5); sfx(10, 'whoosh', .3);
