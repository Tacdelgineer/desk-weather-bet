/* 06 · The fix (16 s): each station's 30-day bias correction, before vs after, then the overall number. */
shot(0, 'riso', 'before/after per station', (lt) => {
  const S = DATA.stations;
  head(lt, 'THE FIX: CORRECT EACH STATION', 'raw AI vs corrected (last 30 days’ average error), °F, TEST window');
  hbars(lt, S.map(s => ({ label: s.city, bars: [{ v: s.raw, col: R.C.brick, txt: `${s.raw}°` }, { v: s.v2, col: R.C.orange, txt: `${s.v2}°` }] })),
        { x: 470, y: 210, w: 1150, h: 680 }, 7, { t0: .5, stag: .3 });
  legend([['raw AIFS', R.C.brick], ['corrected AIFS', R.C.orange]], 600, 950, (lt - .3) / .4);
  R.src('results/forecasts.csv (TEST rows)', (lt - .5) / .5);
}, { noCounter: true });

shot(9, 'riso', 'overall error before/after', (lt) => {
  const M = DATA.test_mae;
  R.mono(`AVERAGE MISS, ALL ${DATA.stations.length} STATIONS (TEST)`, 960, 260, 30, R.C.dim, 'center', 800);
  R.arrowRow([`${M.aifs_raw_mu.toFixed(2)}°F`, `${M.aifs_cor_mu.toFixed(2)}°F`], 960, 520, 150, [clamp(lt / .5), clamp((lt - 1) / .5)]);
  R.fade((lt - 2) / .4, () => R.mono(`free GFS forecast: ${M.gfs_mu.toFixed(2)}°F`, 960, 680, 34, R.C.white, 'center', 700));
  R.fade((lt - 3) / .4, () => { const worse = DATA.stations.filter(s => s.v2 > s.raw);
    if (worse.length) R.mono(`got worse: ${worse.map(s => `${s.city} ${s.raw}° → ${s.v2}°`).join(' · ')}`, 960, 760, 28, R.C.dim, 'center', 600); });
  R.src('results/v1_vs_v2.json (test_mae_F) · results/forecasts.csv', (lt - .5) / .5);
}, { noCounter: true });
sfx(0, 'whoosh', .3); sfx(9, 'thunk', .5); sfx(10, 'thunk', .6);
