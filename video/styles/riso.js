/* riso.js · wide riso print look (from tacdel-shorts styles/riso.html): black paper, white, orange and brick halftone,
   misregistered print type, grain, iso boxes. All riso colours and textures live here; scenes use R.C / R.P names only.
   Credits: riso look after IshaanKalra2103's riso-rooms (MIT) and Kevin Ngo's "a small light, room by room". */
const R = (() => {
  const C = { paper: '#0f0d0c', white: '#f2eadd', orange: '#ff7a21', brick: '#b3432c', dim: 'rgba(242,234,221,.45)', faint: 'rgba(242,234,221,.16)', ink: '#17120f' };
  function screen(col, step, r, ang) { const s = document.createElement('canvas'); s.width = s.height = step; const g = s.getContext('2d');
    g.fillStyle = col; g.beginPath(); g.arc(step / 2, step / 2, r, 0, 7); g.fill(); return { p: ctx.createPattern(s, 'repeat'), m: new DOMMatrix().rotateSelf(ang) }; }
  const P = { o: screen(C.orange, 10, 3.9, 15), oL: screen(C.orange, 10, 2.3, 15), b: screen(C.brick, 9, 3.6, 45), bL: screen(C.brick, 9, 2.2, 45),
              w: screen(C.white, 8, 1.4, 75), wM: screen(C.white, 8, 2.3, 75), wH: screen(C.white, 8, 3.1, 75) };
  const pat = s => { s.p.setTransform(ctx.getTransform().invertSelf().multiplySelf(s.m)); return s.p; };
  const fills = (...f) => f.forEach(s => { ctx.fillStyle = typeof s === 'string' ? s : pat(s); ctx.fill(); });
  const GRAIN = [0, 1, 2].map(() => { const g = document.createElement('canvas'); g.width = 960; g.height = 540; const x = g.getContext('2d'), im = x.createImageData(960, 540);
    for (let i = 0; i < im.data.length; i += 4) { const v = Math.random() < .5 ? 255 : 0; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = Math.random() < .35 ? 34 : 0; }
    x.putImageData(im, 0, 0); return g; });
  // iso
  const K = 62, CS = K * .866, CH = K * .5; let OX = 960, OY = 600;
  const at = (x, y) => { OX = x; OY = y; };
  const iso = (x, y, z = 0) => [OX + (x - y) * CS, OY + (x + y) * CH - z * K];
  const poly = pts => { ctx.beginPath(); pts.forEach((p, i) => i ? ctx.lineTo(...p) : ctx.moveTo(...p)); ctx.closePath(); };
  function box(x, y, z, w, d, h, top, left, right) {
    const A = iso(x, y, z + h), B = iso(x + w, y, z + h), Cc = iso(x + w, y + d, z + h), D = iso(x, y + d, z + h), E = iso(x + w, y + d, z), F = iso(x, y + d, z), G = iso(x + w, y, z);
    ctx.lineWidth = 3.5; ctx.lineJoin = 'round'; ctx.strokeStyle = C.white;
    poly([D, Cc, E, F]); fills(C.paper, ...left); ctx.stroke(); poly([B, Cc, E, G]); fills(C.paper, ...right); ctx.stroke(); poly([A, B, Cc, D]); fills(C.paper, ...top); ctx.stroke();
  }
  function onFace(x, y, z, fn) { const [sx, sy] = iso(x, y, z); ctx.save(); ctx.transform(CS, CH, 0, K, sx, sy); fn(); ctx.restore(); }
  // type
  function printLine(s, x, y, size, col, p, align = 'center') {
    if (p <= 0) return; ctx.save(); ctx.font = `900 ${size}px ${FONT.sans}`; ctx.textAlign = align; ctx.textBaseline = 'alphabetic';
    const w = ctx.measureText(s).width, L = align === 'center' ? x - w / 2 : align === 'right' ? x - w : x;
    ctx.beginPath(); ctx.rect(L - 30, y - size * 1.05, (w + 80) * eo(p), size * 1.4); ctx.clip();
    const reg = (1 - eo(p * 1.2)) * 22; ctx.fillStyle = pat(P.b); ctx.fillText(s, x + size * .07 + reg, y + size * .07 + reg * .4);
    ctx.fillStyle = col || C.white; ctx.fillText(s, x - reg * .3, y); ctx.restore();
  }
  function mono(s, x, y, size, col, align = 'center', wt = 700) { ctx.font = `${wt} ${size}px ${FONT.mono}`; ctx.textAlign = align; ctx.textBaseline = 'alphabetic'; ctx.fillStyle = col || C.white; ctx.fillText(s, x, y); }
  function fade(a, fn) { if (a <= 0) return; ctx.save(); ctx.globalAlpha *= clamp(a); fn(); ctx.restore(); }
  function stamp(s, x, y, ang, col, p, size = 46) {
    if (p <= 0) return; ctx.save(); ctx.translate(x, y); ctx.rotate(ang); const sc = lerp(1.7, 1, back(p / .6)); ctx.scale(sc, sc); ctx.globalAlpha *= clamp(p * 3);
    ctx.font = `900 ${size}px ${FONT.sans}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; const w = ctx.measureText(s).width + 50;
    ctx.lineWidth = 7; ctx.strokeStyle = col || C.orange; ctx.beginPath(); ctx.roundRect(-w / 2, -size * .85, w, size * 1.7, 12); ctx.stroke();
    ctx.fillStyle = col || C.orange; ctx.fillText(s, 0, 2); ctx.restore();
  }
  function src(s, a = 1) { if (a <= 0) return; ctx.save(); ctx.globalAlpha *= a; mono('SOURCE: ' + s, 960, SAFE.b - 6, 22, C.dim, 'center', 500); ctx.restore(); }
  function panel(x, y, w, h, fill = C.paper, r = 18) { ctx.beginPath(); ctx.roundRect(x + 14, y + 14, w, h, r); fills(P.b); ctx.beginPath(); ctx.roundRect(x, y, w, h, r); fills(fill); ctx.lineWidth = 4; ctx.strokeStyle = C.white; ctx.stroke(); }
  function meter(x, y, w, h, frac, label, value, fill = P.wM) {   // horizontal bar; frac in -1..1 from a centre zero line
    ctx.lineWidth = 4; ctx.strokeStyle = C.white; ctx.beginPath(); ctx.roundRect(x, y, w, h, 10); ctx.stroke();
    const z = x + w / 2; ctx.fillStyle = C.white; ctx.fillRect(z - 2, y - 14, 4, h + 28);
    if (frac) { const L = Math.min(z, z + (w / 2 - 10) * frac), Wd = Math.abs((w / 2 - 10) * frac); ctx.beginPath(); ctx.rect(L, y + 9, Wd, h - 18); fills(fill); }
    if (label) mono(label, x, y - 22, 30, C.white, 'left', 700); if (value) mono(value, x + w, y - 22, 36, C.white, 'right', 800);
  }
  // tiles: one per tested group
  function tile(x, y, s, state, k = 0, p = 1) {
    ctx.beginPath(); ctx.roundRect(x, y, s, s, s * .16);
    if (state === 'off') { fills(P.w); ctx.lineWidth = 2; ctx.strokeStyle = C.faint; ctx.stroke(); }
    else if (state === 'test') { fills(C.white); }
    else if (state === 'pass') { fills(C.orange, P.b); ctx.lineWidth = 2.5; ctx.strokeStyle = C.white; ctx.stroke(); }
    else if (state === 'fail') { ctx.fillStyle = C.faint; ctx.fill(); }
    else if (state === 'dead') { ctx.strokeStyle = C.faint; ctx.lineWidth = 2; ctx.stroke(); }
  }
  const gridPos = (i, x0, y0, s, g, cols = 23) => [x0 + (i % cols) * (s + g), y0 + Math.floor(i / cols) * (s + g)];
  // icons (same size for maker and taker: compared things get equal weight)
  function tagIcon(x, y, s, col = C.white) { ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100); ctx.beginPath();
    ctx.moveTo(-40, -30); ctx.lineTo(18, -30); ctx.lineTo(46, 0); ctx.lineTo(18, 30); ctx.lineTo(-40, 30); ctx.closePath(); ctx.lineWidth = 9; ctx.strokeStyle = col; ctx.stroke();
    ctx.beginPath(); ctx.arc(14, 0, 8, 0, 7); ctx.fillStyle = col; ctx.fill(); ctx.restore(); }
  function buyIcon(x, y, s, col = C.white) { ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100); ctx.beginPath(); ctx.roundRect(-46, -30, 92, 60, 14); ctx.lineWidth = 9; ctx.strokeStyle = col; ctx.stroke();
    ctx.font = `900 34px ${FONT.sans}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = col; ctx.fillText('BUY', 0, 2); ctx.restore(); }
  // a riso person (head + body), for crowds; arm 'up' raises an arm with a tag, 'hit' swings down on a button
  function person(x, y, s, fill, k, pose = 0) { ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    ctx.beginPath(); ctx.roundRect(-26, -70, 52, 78, 22); fills(C.paper, fill); ctx.lineWidth = 3.5; ctx.strokeStyle = C.white; ctx.stroke();
    ctx.beginPath(); ctx.arc(0, -96, 22, 0, 7); fills(C.paper, fill); ctx.stroke();
    if (pose) { ctx.beginPath(); ctx.moveTo(20, -58); ctx.lineTo(20 + 24 * Math.cos(pose), -58 - 50 * Math.sin(pose)); ctx.lineWidth = 7; ctx.lineCap = 'round'; ctx.stroke(); }
    ctx.restore(); }
  function arrowRow(parts, x, y, size, ps, hiLast = true) {   // "368 → 24 → 8", each part printing in at its own progress
    ctx.save(); ctx.font = `900 ${size}px ${FONT.sans}`; const ar = '  →  ', wA = ctx.measureText(ar).width, ws = parts.map(s => ctx.measureText(s).width);
    const total = ws.reduce((a, b) => a + b, 0) + wA * (parts.length - 1); let xx = x - total / 2; ctx.restore();
    parts.forEach((s, i) => { if (i) { if (ps[i] > 0) fade(ps[i] * 2, () => mono('→', xx + wA / 2, y - size * .12, size * .7, C.dim, 'center', 800)); xx += wA; }
      printLine(s, xx, y, size, hiLast && i === parts.length - 1 ? C.orange : C.white, ps[i], 'left'); xx += ws[i]; });
  }
  const LOOK = { dim: C.dim,
    begin(lt) { ctx.fillStyle = C.paper; ctx.fillRect(0, 0, W, H); ctx.globalAlpha = eo(lt / .2); },
    end() { const g = ctx.createRadialGradient(960, 540, 600, 960, 540, 1150); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,.5)');
      ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); ctx.globalAlpha = .9; ctx.drawImage(GRAIN[Math.floor(T * 12) % 3], 0, 0, W, H); ctx.globalAlpha = 1; } };
  LOOKS.riso = LOOK;
  return { C, P, pat, fills, GRAIN, at, iso, poly, box, onFace, printLine, mono, fade, stamp, src, panel, meter, tile, gridPos, tagIcon, buyIcon, person, arrowRow, LOOK };
})();
