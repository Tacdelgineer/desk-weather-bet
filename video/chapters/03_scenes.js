/* 03 · Hurricanes (34 s): each storm's real satellite loop with the AI's 3-days-before track, then every miss in km. */
const BOX = { x: 700, y: 60, s: 960 };
function stormShot(name) {
  return (lt) => {
    const G = satTrack(lt, name, BOX, { loop: 8, ai: [.3, 4], best: [4, 5.4], ref: 5.4, zoom: .004 });
    satLegend(lt, G, 96, { title: 0, ai: .3, best: 4 });
    R.fade((lt - 5.6) / .3, () => R.mono(G.ref_kind === 'landfall' ? 'MISS AT LANDFALL' : 'MISS AT CLOSEST APPROACH', 96, 640, 22, R.C.dim, 'left', 700));
    R.printLine(`${G.ref_error_km} km`, 96, 730, 72, R.C.orange, (lt - 5.8) / .5, 'left');
    ctx.fillStyle = 'rgba(15,13,12,.85)'; ctx.fillRect(BOX.x, SAFE.b - 34, BOX.s, 44);
    R.src('NOAA GOES-19 ABI band 13 IR · track: ECMWF AIFS (archived run) vs IBTrACS', (lt - .5) / .5);
  };
}
shot(0, 'riso', 'MELISSA: loop + AI track', stormShot('MELISSA'), { noCounter: true });
shot(8, 'riso', 'IMELDA: loop + AI track', stormShot('IMELDA'), { noCounter: true });
shot(16, 'riso', 'ERIN: loop + AI track', stormShot('ERIN'), { noCounter: true });

shot(24, 'riso', 'every miss, km', (lt) => {
  const S = DATA.storms, I = DATA.isaias, days = [5, 3, 1], x0 = 640, cw = 330;
  head(lt, 'HOW FAR OFF, AT LANDFALL OR CLOSEST APPROACH', 'km between the AI’s storm centre and the real one');
  days.forEach((d, j) => R.mono(`${d} day${d > 1 ? 's' : ''} before`, x0 + j * cw, 260, 26, R.C.dim, 'center', 700));
  const rows = [...S.map(s => ({ name: s.name, sub: s.event.split(' (')[0], v: days.map(d => (s.runs.find(r => r.days === d) || {}).ref_km) })),
                { name: 'ISAIAS 2026', sub: 'run here on the DGX', v: days.map(d => (I.runs.find(r => r.days === d) || {}).local_km) }];
  rows.forEach((r, i) => { const y = 360 + i * 150, p = (lt - .5 - i * .4) / .4;
    R.fade(p, () => { R.mono(r.name, 120, y, 32, R.C.white, 'left', 800); R.mono(r.sub.slice(0, 34), 120, y + 36, 18, R.C.dim, 'left', 600); });
    r.v.forEach((v, j) => R.fade(p - j * .5, () => R.mono(v == null ? "no storm yet" : `${v.toFixed(1)} km`, x0 + j * cw, y + 12, v == null ? 22 : 44,
      v == null ? R.C.dim : v < 100 ? R.C.orange : R.C.white, 'center', 800))); });
  R.fade((lt - 3.5) / .4, () => R.mono('orange = under 100 km', 1800, 980, 20, R.C.orange, 'right', 700));
  R.src('results/hurricanes.json · results/isaias_local.json', (lt - .5) / .5);
}, { noCounter: true });
[0, 8, 16].forEach(t => { sfx(t, 'whoosh', .3); sfx(t + 5.8, 'thunk', .5); }); sfx(24, 'paper', .4);
