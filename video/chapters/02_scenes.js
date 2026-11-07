/* 02 · Desk AI (22 s): the real AIFS run log, how fast it runs here vs the old mini PC, and the first sanity check. */
shot(0, 'crt', 'crt: AIFS run log', crtAifsLog, { boot: true, noCounter: true });

shot(8, 'riso', 'speed: mini PC vs DGX', (lt) => {
  const T = DATA.timing;
  head(lt, 'ONE 6-HOUR STEP OF THE WEATHER AI', 'same model, same input · seconds per step');
  const row = (y, label, sub, s, col, t0) => { const p = eo((lt - t0) / 1.2), w = 1300 * Math.min(1, s / T.cpu_step_s) * p;
    R.mono(label, 160, y - 40, 30, R.C.white, 'left', 800); R.mono(sub, 160, y - 8, 20, R.C.dim, 'left', 600);
    ctx.beginPath(); ctx.rect(165, y + 15, Math.max(4, w), 70); R.fills(R.P.b); ctx.beginPath(); ctx.rect(160, y + 10, Math.max(4, w), 70); R.fills(col);
    R.fade((p - .5) * 3, () => R.mono(`${s} s`, 160 + Math.max(4, w) + 24, y + 62, 40, col, 'left', 800)); };
  row(330, 'old mini PC (CPU)', T.cpu_machine.split(',')[0], T.cpu_step_s, R.C.dim, .4);
  row(580, 'DGX Spark (GPU)', T.machine.split(':')[0], T.step_s, R.C.orange, 1.0);
  R.fade((lt - 2.6) / .4, () => R.mono(`a 10-day forecast: ${T.cpu_ten_day_h} h there · ${Math.round(T.ten_day_s)} s here`, 960, 880, 34, R.C.white, 'center', 800));
  R.src('results/timing.json · logs/1.1_test.log · logs/1.1_dgx_00z.log', (lt - .5) / .5);
}, { noCounter: true });

shot(15, 'riso', 'sanity check: LA vs NWS', (lt) => {
  const C = DATA.la_check, b = { x: 260, y: 230, w: 1400, h: 560 }, lo = 10, hi = 25, Y = v => b.y + b.h - (v - lo) / (hi - lo) * b.h;
  head(lt, 'FIRST CHECK · LOS ANGELES', 'AI forecast vs what the NWS station measured, °C');
  ctx.lineWidth = 3; ctx.strokeStyle = R.C.white; ctx.beginPath(); ctx.moveTo(b.x, b.y + b.h); ctx.lineTo(b.x + b.w, b.y + b.h); ctx.stroke();
  C.forEach((c, i) => { const cx = b.x + (i + .5) * b.w / C.length, p = eo((lt - .5 - i * .35) / .6);
    [[c.aifs, R.C.orange, -60], [c.obs, R.C.white, 10]].forEach(([v, col, dx]) => { const top = lerp(b.y + b.h, Y(v), p);
      ctx.beginPath(); ctx.rect(cx + dx + 5, top + 5, 50, b.y + b.h - top); R.fills(R.P.b); ctx.beginPath(); ctx.rect(cx + dx, top, 50, b.y + b.h - top); R.fills(col);
      R.fade((p - .7) * 4, () => R.mono(`${v}°`, cx + dx + 25, top - 14, 26, col, 'center', 800)); });
    R.mono(`${c.valid} UTC`, cx, b.y + b.h + 40, 22, R.C.dim, 'center', 600); });
  legend([['AI (AIFS on the DGX)', R.C.orange], ['NWS station', R.C.white]], 560, 930, (lt - .3) / .4);
  R.src('results/aifs_la_sanity.json', (lt - .5) / .5);
}, { noCounter: true });
sfx(8, 'whoosh', .3); sfx(9, 'swish', .3); sfx(15, 'whoosh', .3);
