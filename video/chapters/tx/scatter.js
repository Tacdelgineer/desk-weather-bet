/* scatter.js · the "bug" scatter (riso): Phoenix's summer TRAIN days (raw AIFS vs actual), the v1 line drawn across
   them, then extended out to the October raw high, landing on v1's corrected high; GFS and NWS marked on the same
   axis. Shared by the wide preview (90_scenes.js) and the vertical still (preview/vertical.html).
   b = {x, y, w, h} plot box, s = type scale. Every number from DATA.v1. */
function bugScatter(lt, b, s = 1) {
  const v = DATA.v1, lo = 70, hi = 120;
  const X = f => b.x + (f - lo) / (hi - lo) * b.w, Y = f => b.y + b.h - (f - lo) / (hi - lo) * b.h;
  // axes
  ctx.lineWidth = 3; ctx.strokeStyle = R.C.white; ctx.beginPath(); ctx.moveTo(b.x, b.y); ctx.lineTo(b.x, b.y + b.h); ctx.lineTo(b.x + b.w, b.y + b.h); ctx.stroke();
  for (let f = lo; f <= hi; f += 10) { R.mono(f + '°', X(f), b.y + b.h + 34 * s, 20 * s, R.C.dim, 'center', 600); R.mono(f + '°', b.x - 14 * s, Y(f) + 7 * s, 20 * s, R.C.dim, 'right', 600); }
  R.mono('AI forecast high (raw AIFS, °F)', b.x + b.w / 2, b.y + b.h + 74 * s, 22 * s, R.C.white, 'center', 700);
  ctx.save(); ctx.translate(b.x - 78 * s, b.y + b.h / 2); ctx.rotate(-Math.PI / 2); R.mono('what really happened (°F)', 0, 0, 22 * s, R.C.white, 'center', 700); ctx.restore();
  // the summer cloud, printing in
  v.scatter.forEach(([r, a], i) => { const p = clamp((lt - .2 - i * .022) / .25); if (p <= 0) return;
    ctx.beginPath(); ctx.arc(X(r) + 3, Y(a) + 3, 9 * s, 0, 7); R.fills(R.P.b); ctx.beginPath(); ctx.arc(X(r), Y(a), 9 * s * back(p), 0, 7); R.fills(R.C.white); });
  R.fade((lt - 1.4) / .4, () => R.mono(`${v.n_train} summer TRAIN days`, X(v.train_min) - 10 * s, Y(v.train_max) - 30 * s, 24 * s, R.C.white, 'left', 800));
  // the v1 line across the cloud, then extended past it
  const f = r => v.a + v.b * r, seg = (r0, r1, p, dash) => { if (p <= 0) return; const r = lerp(r0, r1, eo(p));
    ctx.save(); ctx.setLineDash(dash ? [16 * s, 12 * s] : []); ctx.lineCap = 'round';
    ctx.lineWidth = 7 * s; ctx.strokeStyle = R.C.brick; ctx.beginPath(); ctx.moveTo(X(r0) + 4, Y(f(r0)) + 4); ctx.lineTo(X(r) + 4, Y(f(r)) + 4); ctx.stroke();
    ctx.strokeStyle = R.C.orange; ctx.beginPath(); ctx.moveTo(X(r0), Y(f(r0))); ctx.lineTo(X(r), Y(f(r))); ctx.stroke(); ctx.restore(); };
  seg(v.train_min, v.train_max, (lt - 1.9) / .9, false);
  R.fade((lt - 2.6) / .3, () => R.mono('v1 line, fit on summer', X(106), Y(f(106)) + 64 * s, 22 * s, R.C.orange, 'left', 800));
  seg(v.train_min, v.raw, (lt - 3.1) / 1.2, true);
  // the October day: raw high -> v1 corrected high
  const pO = clamp((lt - 4.3) / .35);
  if (pO > 0) { ctx.save(); ctx.globalAlpha *= pO; ctx.setLineDash([4, 8]); ctx.lineWidth = 2; ctx.strokeStyle = R.C.dim;
    ctx.beginPath(); ctx.moveTo(X(v.raw), b.y + b.h); ctx.lineTo(X(v.raw), Y(v.corrected)); ctx.lineTo(b.x, Y(v.corrected)); ctx.stroke(); ctx.restore();
    ctx.beginPath(); ctx.arc(X(v.raw), Y(v.corrected), 15 * s * back(pO), 0, 7); R.fills(R.C.orange); ctx.lineWidth = 4; ctx.strokeStyle = R.C.white; ctx.stroke();
    R.printLine(`October: raw ${v.raw.toFixed(2)}° → v1 says ${v.corrected.toFixed(2)}°`, X(v.raw) + 30 * s, Y(v.corrected) - 26 * s, 34 * s, R.C.orange, pO * 1.5, 'left'); }
  // GFS and NWS on the same axis
  [[v.gfs, 'GFS', R.C.white, 5.3], [v.nws, 'NWS', R.C.white, 5.9]].forEach(([val, name, col, t0], k) => { const p = clamp((lt - t0) / .3); if (p <= 0) return;
    ctx.save(); ctx.globalAlpha *= p; ctx.lineWidth = 6 * s; ctx.strokeStyle = col; ctx.beginPath(); ctx.moveTo(X(v.raw) - 26 * s, Y(val)); ctx.lineTo(X(v.raw) + 26 * s, Y(val)); ctx.stroke(); ctx.restore();
    R.fade(p, () => R.mono(`${name} ${val}°`, X(v.raw) + 40 * s, Y(val) + (k ? -6 : 22) * s, 26 * s, col, 'left', 800)); });
  R.fade((lt - 6.5) / .3, () => R.mono(`${v.minus_nws}° hotter than the NWS forecast`, b.x + b.w, b.y + b.h - 60 * s, 28 * s, R.C.orange, 'right', 800));
}
