/* papercut.js · wide paper-cut collage look (from tacdel-shorts styles/papercut.html): cut paper, tape, dymo labels,
   ransom letters, red stamps, motion on twos (12 fps). All paper colours and textures live here; scenes use PC.C names. */
const PC = (() => {
  const C = { bg: '#e9dec7', cream: '#fbf6ea', kraft: '#c69a66', red: '#d4452a', teal: '#1f6a73', mustard: '#e5ad36', ink: '#221d19', news: '#d8d1c1',
              pink: '#eaa596', green: '#5d8a4a', shadow: 'rgba(72,46,20,.30)', dim: 'rgba(34,29,25,.55)' };
  function noiseCanvas(lo, hi) { const s = document.createElement('canvas'); s.width = s.height = 256; const g = s.getContext('2d'), im = g.createImageData(256, 256);
    for (let i = 0; i < im.data.length; i += 4) { const v = lo + Math.random() * (hi - lo); im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; } g.putImageData(im, 0, 0); return s; }
  const TEX = ctx.createPattern(noiseCanvas(200, 255), 'repeat');
  const BG = (() => { const s = document.createElement('canvas'); s.width = W; s.height = H; const g = s.getContext('2d');
    g.fillStyle = C.bg; g.fillRect(0, 0, W, H); g.globalCompositeOperation = 'multiply'; g.fillStyle = g.createPattern(noiseCanvas(215, 255), 'repeat'); g.fillRect(0, 0, W, H); g.globalCompositeOperation = 'source-over';
    for (let i = 0; i < 1500; i++) { const x = Math.random() * W, y = Math.random() * H, a = Math.random() * 6.3, l = 6 + Math.random() * 22;
      g.strokeStyle = Math.random() < .5 ? 'rgba(255,255,255,.35)' : 'rgba(120,90,50,.12)'; g.lineWidth = 1.2; g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + Math.cos(a) * l, y + Math.sin(a) * l * .3, x + Math.cos(a + .4) * l * 1.6, y + Math.sin(a + .4) * l); g.stroke(); }
    const v = g.createRadialGradient(960, 540, 700, 960, 540, 1250); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(70,40,10,.22)'); g.fillStyle = v; g.fillRect(0, 0, W, H); return s; })();
  const jit = (k, amt) => (rnd(k * 7.3 + Q * 1.91) - .5) * amt;
  const poly = pts => { ctx.beginPath(); pts.forEach((p, i) => i ? ctx.lineTo(...p) : ctx.moveTo(...p)); ctx.closePath(); };
  function torn(x, y, w, h, seed, rough = 4, step = 15) { const pts = [], s = seed + (Q % 3) * .013;
    const edge = (x0, y0, x1, y1, k) => { const L = Math.hypot(x1 - x0, y1 - y0), n = Math.max(2, Math.round(L / step)), nx = -(y1 - y0) / L, ny = (x1 - x0) / L;
      for (let i = 0; i < n; i++) { const u = i / n, j = (rnd(s * 3.1 + k * 97 + i * 13.7) - .5) * rough * 2; pts.push([x0 + (x1 - x0) * u + nx * j, y0 + (y1 - y0) * u + ny * j]); } };
    edge(x, y, x + w, y, 1); edge(x + w, y, x + w, y + h, 2); edge(x + w, y + h, x, y + h, 3); edge(x, y + h, x, y, 4); poly(pts); }
  function cutCircle(x, y, r, seed, rough = 2.5) { const pts = [], n = Math.max(14, Math.round(r / 5));
    for (let i = 0; i < n; i++) { const a = i / n * 6.283, rr = r + (rnd(seed + i * 7.7 + (Q % 3) * .01) - .5) * rough * 2; pts.push([x + Math.cos(a) * rr, y + Math.sin(a) * rr]); } poly(pts); }
  function piece(path, col, sh = true, edge = false) {
    if (sh) { ctx.save(); ctx.translate(7, 9); path(); ctx.fillStyle = C.shadow; ctx.fill(); ctx.restore(); }
    path(); ctx.fillStyle = col; ctx.fill(); ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = TEX; ctx.fill(); ctx.restore();
    if (edge) { ctx.strokeStyle = 'rgba(255,252,242,.75)'; ctx.lineWidth = 3; ctx.stroke(); } }
  const rect = (x, y, w, h, r = 6) => () => { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); };
  function tape(x, y, w, ang) { ctx.save(); ctx.translate(x, y); ctx.rotate(ang); torn(-w / 2, -17, w, 34, x * .1 + y, 2.5, 9); ctx.fillStyle = 'rgba(243,232,190,.78)'; ctx.fill(); ctx.restore(); }
  function dymo(s, x, y, size = 30, ang = 0, a = 1) { if (a <= 0) return; ctx.save(); ctx.globalAlpha *= clamp(a); ctx.translate(x, y); ctx.rotate(ang); ctx.font = `900 ${size}px ${FONT.sans}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    const w = ctx.measureText(s).width + 44, h = size * 1.55; piece(() => { ctx.beginPath(); ctx.roundRect(-w / 2, -h / 2, w, h, 7); }, '#1c1b1d');
    ctx.fillStyle = '#000'; ctx.fillText(s, 1.5, 2.5); ctx.fillStyle = '#f2efe8'; ctx.fillText(s, 0, 0); ctx.restore(); return w; }
  function text(s, x, y, size, col = C.ink, align = 'center', wt = 900, font = FONT.sans) { ctx.font = `${wt} ${size}px ${font}`; ctx.textAlign = align; ctx.textBaseline = 'alphabetic'; ctx.fillStyle = col; ctx.fillText(s, x, y); }
  function ransom(lines, cx, y0, size, seed, lt, maxW = 1600, lh = 1.28) {
    const fonts = [s => `900 ${s}px ${FONT.sans}`, s => `700 ${s * 1.06}px ${FONT.serif}`, s => `700 ${s * .98}px ${FONT.type}`, s => `italic 700 ${s}px ${FONT.serif}`, s => `700 ${s * .9}px ${FONT.sans}`];
    const looks = [[C.cream, C.ink], [C.ink, C.cream], [C.red, C.cream], [C.mustard, C.ink], [C.teal, C.cream], [C.news, C.ink], [C.kraft, C.ink], [C.pink, C.ink]];
    let k = 0;
    lines.forEach((line, li) => {
      const chars = [...line.toUpperCase()];
      const widths = sz => chars.map((ch, i) => { ctx.font = fonts[Math.floor(rnd(seed + i + li * 31) * 5)](sz); return ch === ' ' ? sz * .32 : ctx.measureText(ch).width + sz * .3; });
      let ws = widths(size), total = ws.reduce((a, b) => a + b + 6, -6); const fit = Math.min(1, maxW / total), sz = size * fit; if (fit < 1) { ws = widths(sz); total = ws.reduce((a, b) => a + b + 6, -6); }
      let x = cx - total / 2; const y = y0 + li * size * lh;
      chars.forEach((ch, i) => { const id = seed + i + li * 31, w = ws[i], ccx = x + w / 2; x += w + 6; k++; if (ch === ' ') return;
        const tIn = stepT(lt - k * .035); if (tIn < 0) return;
        const sc = lerp(1.45, 1, back(tIn / .25)), rot = (rnd(id * 1.7) - .5) * .22 + (rnd(id + Q) - .5) * .015;
        const [bg, fg] = looks[Math.floor(rnd(id * 2.3) * looks.length)], hh = sz * 1.18, dy = (rnd(id * 5.1) - .5) * sz * .12;
        ctx.save(); ctx.translate(ccx, y + dy); ctx.rotate(rot); ctx.scale(sc, sc);
        piece(() => (rnd(id * 3.9) < .5 ? torn(-w / 2, -hh / 2, w, hh, id, 3.5, 12) : (ctx.beginPath(), ctx.rect(-w / 2, -hh / 2, w, hh))), bg);
        ctx.font = fonts[Math.floor(rnd(id) * 5)](sz); ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = fg; ctx.fillText(ch, 0, sz * .05); ctx.restore(); });
    });
  }
  function stamp(s, x, y, ang, p, size = 54, col = C.red) { if (p <= 0) return; ctx.save(); ctx.translate(x, y); ctx.rotate(ang); const sc = lerp(1.8, 1, back(p / .4)); ctx.scale(sc, sc); ctx.globalAlpha *= clamp(p * 3) * .9;
    ctx.font = `900 ${size}px ${FONT.sans}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; const w = ctx.measureText(s).width + 56;
    ctx.strokeStyle = col; ctx.lineWidth = 8; ctx.setLineDash([26, 5]); ctx.beginPath(); ctx.roundRect(-w / 2, -size * .9, w, size * 1.8, 14); ctx.stroke(); ctx.setLineDash([]);
    ctx.fillStyle = col; ctx.fillText(s, 0, 3); ctx.restore(); }
  // a coin seen edge-on while it flips: ph = flip phase (radians); face 'H' or 'T'
  function coin(x, y, r, ph, face, seed, glow = 0) { const sx = Math.abs(Math.cos(ph)), up = Math.cos(ph) >= 0; ctx.save(); ctx.translate(x, y);
    if (glow > 0) { ctx.save(); ctx.globalAlpha *= glow; ctx.beginPath(); ctx.arc(0, 0, r * 1.5, 0, 7); ctx.fillStyle = 'rgba(229,173,54,.45)'; ctx.fill(); ctx.restore(); }
    ctx.scale(Math.max(.08, sx), 1); piece(() => cutCircle(0, 0, r, seed), up ? C.mustard : C.kraft); piece(() => cutCircle(0, 0, r * .72, seed + 3), up ? '#f0c25a' : '#d4ab78', false);
    if (sx > .35) text(up ? face : (face === 'H' ? 'T' : 'H'), 0, r * .34, r * .9, C.ink); ctx.restore(); }
  function ticket(x, y, w, h, lines, seed, col = C.cream) { piece(() => torn(x, y, w, h, seed, 3, 14), col);
    ctx.save(); ctx.setLineDash([10, 9]); ctx.strokeStyle = C.dim; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(x + w * .78, y + 14); ctx.lineTo(x + w * .78, y + h - 14); ctx.stroke(); ctx.restore();
    lines.forEach((l, i) => text(l.s, x + (l.x ?? w * .39), y + (l.y ?? h * .42 + i * l.size * 1.25), l.size, l.col || C.ink, 'center', l.wt || 900, l.font || FONT.sans)); }
  // a wall calendar page: days crossed off up to p; label on the header strip
  function calendar(x, y, w, h, title, nDays, p, seed, o = {}) {
    piece(() => torn(x, y, w, h, seed, 2.5), C.cream); piece(rect(x, y, w, h * .2, 4), o.head || C.red, false);
    text(title, x + w / 2, y + h * .14, h * .095, C.cream); const cols = 7, rows = Math.ceil(nDays / cols), cw = (w - 40) / cols, ch = (h * .78 - 30) / rows;
    for (let i = 0; i < nDays; i++) { const cx = x + 20 + (i % cols) * cw, cy = y + h * .22 + 10 + Math.floor(i / cols) * ch;
      ctx.strokeStyle = 'rgba(34,29,25,.25)'; ctx.lineWidth = 2; ctx.strokeRect(cx, cy, cw - 6, ch - 6);
      if (o.labels) text(o.labels[i], cx + 8, cy + ch * .45, ch * .32, C.ink, 'left', 700, FONT.mono);
      if (i < Math.floor(p * nDays)) { ctx.strokeStyle = C.red; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(cx + 8, cy + 8); ctx.lineTo(cx + cw - 14, cy + ch - 14); ctx.moveTo(cx + cw - 14, cy + 8); ctx.lineTo(cx + 8, cy + ch - 14); ctx.stroke(); } } }
  // a round vault door; open 0..1 swings it aside (drawn as a squash), spin turns the wheel
  function vault(x, y, r, open, spin, seed, inner) { piece(() => cutCircle(x, y, r * 1.12, seed), C.ink); if (inner) inner();
    const sx = 1 - open * .85, ox = -open * r * 1.05; ctx.save(); ctx.translate(x + ox, y); ctx.scale(sx, 1);
    piece(() => cutCircle(0, 0, r, seed + 1), '#8d8579'); piece(() => cutCircle(0, 0, r * .82, seed + 2), '#a39b8e', false);
    ctx.rotate(spin); for (let i = 0; i < 6; i++) { ctx.save(); ctx.rotate(i * Math.PI / 3); piece(rect(-9, -r * .62, 18, r * .62, 6), C.ink, false); ctx.restore(); }
    piece(() => cutCircle(0, 0, r * .16, seed + 3), C.mustard, false); ctx.restore(); }
  // a balance beam: tilt in radians (+ = right side down); returns the pan centres
  function scale(x, y, len, tilt) { piece(rect(x - 14, y, 28, 300, 6), C.kraft); piece(() => { ctx.beginPath(); ctx.moveTo(x - 90, y + 330); ctx.lineTo(x + 90, y + 330); ctx.lineTo(x, y + 270); ctx.closePath(); }, C.teal);
    const dx = Math.cos(tilt) * len / 2, dy = Math.sin(tilt) * len / 2;
    ctx.save(); ctx.translate(x, y); ctx.rotate(tilt); piece(rect(-len / 2, -10, len, 20, 6), C.ink); ctx.restore(); piece(() => cutCircle(x, y, 20, 77), C.mustard, false);
    const L = [x - dx, y - dy], Rr = [x + dx, y + dy];
    [L, Rr].forEach(([px, py], i) => { ctx.strokeStyle = C.ink; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(px - 110, py + 120); ctx.moveTo(px, py); ctx.lineTo(px + 110, py + 120); ctx.stroke();
      piece(() => { ctx.beginPath(); ctx.ellipse(px, py + 128, 140, 26, 0, 0, 7); }, C.kraft); });
    return [[L[0], L[1] + 110], [Rr[0], Rr[1] + 110]]; }
  function pie(x, y, r, frac, seed, col = C.red) { piece(() => cutCircle(x, y, r, seed), C.cream);
    if (frac > 0) piece(() => { ctx.beginPath(); ctx.moveTo(x, y); ctx.arc(x, y, r - 6, -Math.PI / 2, -Math.PI / 2 + frac * 6.283); ctx.closePath(); }, col, false); }
  function bill(x, y, w, ang, seed) { const h = w * .45; ctx.save(); ctx.translate(x, y); ctx.rotate(ang); piece(() => torn(-w / 2, -h / 2, w, h, seed, 2), C.green);
    piece(rect(-w / 2 + 14, -h / 2 + 12, w - 28, h - 24, 6), '#8fb36f', false); piece(() => cutCircle(0, 0, h * .3, seed + 1), C.green, false); text('$1', 0, h * .13, h * .34, C.cream); ctx.restore(); }
  function envelope(x, y, w, ang, seed) { const h = w * .62; ctx.save(); ctx.translate(x, y); ctx.rotate(ang); piece(() => torn(-w / 2, -h / 2, w, h, seed, 2), C.news);
    ctx.strokeStyle = C.dim; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(-w / 2 + 8, -h / 2 + 8); ctx.lineTo(0, h * .1); ctx.lineTo(w / 2 - 8, -h / 2 + 8); ctx.stroke(); ctx.restore(); }
  function receipt(x, y, w, len, lines, seed, p = 1) {
    const L = len * clamp(p); const path = () => { ctx.beginPath(); ctx.moveTo(x, y); for (let i = 0; i <= 20; i++) ctx.lineTo(x + w * i / 20, y + (rnd(seed + i) - .5) * 8);
      for (let i = 20; i >= 0; i--) ctx.lineTo(x + w * i / 20, y + L + (i % 2 ? 14 : 0)); ctx.closePath(); };
    piece(path, C.cream, true); ctx.save(); path(); ctx.clip();
    lines.forEach((l, i) => { const yy = y + 60 + i * 52; if (l.blur) { ctx.filter = 'blur(7px)'; } text(l.s, x + 26, yy, 30, l.col || C.ink, 'left', 700, FONT.type); if (l.r) text(l.r, x + w - 26, yy, 30, l.col || C.ink, 'right', 700, FONT.type); ctx.filter = 'none'; });
    ctx.restore(); }
  // paper puppet person: body col, a bobbing head; arm angle up (radians, 0 = down)
  function figure(x, y, s, col, seed, arm = .3, o = {}) { ctx.save(); ctx.translate(x + jit(seed, 3), y + jit(seed + 1, 3)); ctx.scale(s, s);
    piece(rect(-34, -40, 26, 120, 8), C.ink); piece(rect(8, -40, 26, 120, 8), C.ink);
    ctx.save(); ctx.translate(46, -150); ctx.rotate(-arm); piece(rect(-12, 0, 24, 100, 10), col); ctx.restore();
    ctx.save(); ctx.translate(-46, -150); ctx.rotate(.25); piece(rect(-12, 0, 24, 100, 10), col); ctx.restore();
    piece(() => torn(-56, -170, 112, 150, seed, 3), col); piece(() => cutCircle(0, -215, 44, seed + 2), C.pink);
    ctx.fillStyle = C.ink; [-1, 1].forEach(d => { ctx.beginPath(); ctx.arc(d * 15, -222, 6, 0, 7); ctx.fill(); });
    if (o.smile) { ctx.strokeStyle = C.ink; ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(0, -205, 14, .2, Math.PI - .2); ctx.stroke(); }
    ctx.restore(); }
  function arrow(x0, y0, x1, y1, col = C.ink, wdt = 10) { const a = Math.atan2(y1 - y0, x1 - x0); ctx.strokeStyle = col; ctx.lineWidth = wdt; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x1 - Math.cos(a - .5) * 34, y1 - Math.sin(a - .5) * 34); ctx.lineTo(x1 - Math.cos(a + .5) * 34, y1 - Math.sin(a + .5) * 34); ctx.closePath(); ctx.fillStyle = col; ctx.fill(); }
  const slideIn = (lt, t0, dist = 900) => (1 - back(stepT(lt - t0) / .4)) * dist;
  function src(s, a = 1) { if (a <= 0) return; ctx.save(); ctx.globalAlpha *= a; text('SOURCE: ' + s, 960, SAFE.b - 6, 22, C.dim, 'center', 600, FONT.mono); ctx.restore(); }
  const LOOK = { dim: C.dim, begin(lt) { ctx.drawImage(BG, 0, 0); ctx.globalAlpha = clamp(stepT(lt) / .17); }, end() {} };
  LOOKS.paper = LOOK;
  return { C, TEX, BG, jit, poly, torn, cutCircle, piece, rect, tape, dymo, text, ransom, stamp, coin, ticket, calendar, vault, scale, pie, bill, envelope, receipt, figure, arrow, slideIn, src, LOOK };
})();
