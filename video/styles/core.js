/* core.js · shared wide (1920x1080) player for every chapter: word cues, shots, real-clip windows, overlays, slates,
   clip holes, player. From the tacdel-video skill's chapter kit (scripts/chapters/README.md).
   Colours here are only for the overlays that sit above every look (counter, slates, EXAMPLE tags, the fake label,
   NOT FINANCIAL ADVICE). Look colours, textures and helpers live in riso.js, papercut.js and crt.js. Scenes never set
   their own colours. */
const W = 1920, H = 1080;
const SAFE = { l: 96, t: 54, r: 1824, b: 1026, cx: 960, cy: 540 };      // 5% margin: nothing important outside
const FONT = { sans: '"Inter","Helvetica Neue",Arial,sans-serif', mono: '"JetBrains Mono","DejaVu Sans Mono",Menlo,monospace',
               serif: 'Georgia,"DejaVu Serif","Times New Roman",serif', type: '"Courier New",Courier,"Liberation Mono",monospace' };
const OV = { panel: 'rgba(14,12,11,.88)', ink: '#f2eadd', hot: '#ff7a21', dim: 'rgba(242,234,221,.62)', line: 'rgba(242,234,221,.35)',
             label: { bg: '#0e0c0b', bgAlpha: .82, ink: '#f2eadd', size: 24, font: '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf' }, slate: '#ffd84a', slateInk: '#17130f', slateHot: '#d4452a', slateDim: 'rgba(23,19,15,.6)', hole: '#0a0a0a', tag: '#f2eadd', tagInk: '#17130f' };

/* ---------- math ---------- */
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x)), lerp = (a, b, u) => a + (b - a) * u;
const eo = u => 1 - Math.pow(1 - clamp(u), 3), eio = u => { u = clamp(u); return u < .5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2; };
const back = u => { u = clamp(u); const c = 1.7; return 1 + (c + 1) * Math.pow(u - 1, 3) + c * Math.pow(u - 1, 2); };
const rnd = n => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const stepT = x => Math.floor(x * 12) / 12;                      // 12 fps "twos" for paper motion
const fmt = (x, d = 0) => x.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
const sgn = (x, d = 2) => (x >= 0 ? '+' : '−') + Math.abs(x).toFixed(d);
let T = 0, Q = 0;

const cv = document.getElementById('c'), ctx = cv.getContext('2d');
const ERRS = []; const fail = m => { ERRS.push(m); console.error(m); };

/* ---------- word cues: every animation keys to the start of a spoken word ---------- */
const norm = s => s.toLowerCase().replace(/[^a-z0-9]/g, '');
const WT = (window.WORDS || []).map(w => ({ ...w, n: norm(w.text) }));
function cueIdx(phrase, after = 0) {
  const toks = phrase.split(/\s+/).map(norm).filter(Boolean);
  for (let i = 0; i <= WT.length - toks.length; i++) {
    if (WT[i].start < after - 1e-6) continue;
    if (toks.every((k, j) => WT[i + j].n === k)) return [i, i + toks.length - 1];
  }
  fail(`cue not found: "${phrase}" after ${after}`); return [0, 0];
}
const cue = (p, after = 0) => WT.length ? WT[cueIdx(p, after)[0]].start : 0;      // start of the phrase
const cueEnd = (p, after = 0) => WT.length ? WT[cueIdx(p, after)[1]].end : 0;     // end of the phrase
const VOICE_END = WT.length ? WT[WT.length - 1].end : 0;

/* ---------- re-timing (timing.py warp writes WARP) ---------- */
// the inverse: page time (what the shots were written for) -> video time (the take), for sounds, clips and slates
const unwarp = s => { if (WARP.length < 2) return s; let i = 0; while (i < WARP.length - 2 && s > WARP[i + 1][1]) i++;
  const [a0, b0] = WARP[i], [a1, b1] = WARP[i + 1]; return a0 + (s - b0) * (a1 - a0) / (b1 - b0); };
const warp = t => { if (WARP.length < 2) return t; let i = 0; while (i < WARP.length - 2 && t > WARP[i + 1][0]) i++;
  const [a0, b0] = WARP[i], [a1, b1] = WARP[i + 1]; return b0 + (t - a0) * (b1 - b0) / (a1 - a0); };

/* ---------- shots, looks, sound cues, clips ---------- */
const LOOKS = {};                         // filled by riso.js, papercut.js, crt.js and slate below
const SHOTS = [];                         // {at, look, draw(lt, t, dur), name}
const shot = (at, look, name, draw, o = {}) => SHOTS.push({ at, look, name, draw, ...o });
const SFX = [];                           // [page time, name, gain]; mixed by tools/sfx.py
const sfx = (t, name, g = 1) => SFX.push([+t.toFixed(3), name, g]);
const CLIPS = [];                         // real footage composited by tools/build.sh with ffmpeg at these rects
// o.label: a small caption burned onto the clip (style: OV.label)
const clip = (src, t0, t1, x, y, w, h, from = 0, o = {}) => CLIPS.push({ src, t0, t1, x, y, w, h, from, ...(o.label ? { label: o.label, labelStyle: OV.label } : {}), ...(o.crop ? { crop: o.crop } : {}) });
// windows: real clips over, beside or instead of the shot underneath (page time, written in time order)
//   'full'  the clips fill the frame on a plain background, with a title     'split' the shot shrinks left, clips stand right
//   'pip'   one small clip in a corner (o.at 'br' | 'bl' | 'tr' | 'tl'; o.wide keeps 16:9)     'punch' no clip: the shot pushes in (o.k, o.cx, o.cy)
// items: [{ src, title, from, crop }]; a window that starts where one of the same mode ends continues it (no re-entry move)
const WINS = [], SPLIT = { x: 60, y: 227, w: 1114, h: 626 };
function grid(n, box, aspect, gap = 36, cols = n <= 3 ? n : n === 4 ? 2 : n <= 6 ? 3 : 5) {
  const rows = Math.ceil(n / cols);
  const tw = Math.floor(Math.min((box.w - gap * (cols - 1)) / cols, (box.h - gap * (rows - 1)) / rows * aspect)), th = Math.round(tw / aspect);
  const x0 = box.x + (box.w - cols * tw - (cols - 1) * gap) / 2, y0 = box.y + (box.h - rows * th - (rows - 1) * gap) / 2;
  return Array.from({ length: n }, (_, i) => ({ x: Math.round(x0 + (i % cols) * (tw + gap)), y: Math.round(y0 + Math.floor(i / cols) * (th + gap)), w: tw, h: th }));
}
function win(t0, t1, mode, items = [], o = {}) {
  const prev = WINS[WINS.length - 1], c0 = prev && prev.mode === mode && Math.abs(prev.t1 - t0) < .01 ? prev.c0 : t0;
  const narrow = !o.wide && (mode === 'pip' || mode === 'split' || items.length === 3), aspect = narrow ? 4 / 3 : 16 / 9;
  let R0;
  if (mode === 'full') R0 = grid(items.length, items.length === 1 ? { x: 240, y: 178, w: 1440, h: 810 } : { x: 88, y: 200, w: 1744, h: 800 }, aspect);
  else if (mode === 'split') R0 = grid(items.length, { x: 1214, y: 170, w: 646, h: 800 }, aspect, 28, items.length <= 2 ? 1 : 2);
  else if (mode === 'pip') { const w = o.w || 440, h = Math.round(w / aspect), at = o.at || 'br', m = 24;
    R0 = [{ x: at[1] === 'r' ? SAFE.r - m - w : SAFE.l + m, y: at[0] === 'b' ? SAFE.b - m - h : SAFE.t + m, w, h }]; }
  else R0 = [];
  const w = { t0, t1, mode, c0, items, rects: R0, ...o }; WINS.push(w);
  const lag = mode === 'split' && c0 === t0 ? .3 : 0;   // the split slides in first
  items.forEach((it, i) => { const r = R0[i];
    clip(it.src, t0 + lag, t1, r.x, r.y, r.w, r.h, it.from || 0, { label: items.length > 1 || mode !== 'full' ? it.title : (it.label || 'real run'), crop: it.crop !== undefined ? it.crop : narrow ? [160, 0, 960, 720] : undefined }); });   // 1280x720 sources: centre 4:3
  return w;
}
const winAt = t => WINS.find(w => t >= w.t0 && t < w.t1), winLook = (w, s) => w.look || (s.look === 'crt' ? 'riso' : s.look);
const shotAt = t => { let i = 0; while (i < SHOTS.length - 1 && t >= SHOTS[i + 1].at) i++; return i; };
const shotSpans = () => SHOTS.map((s, i) => ({ look: s.look, name: s.name, rec: s.rec || null, t0: s.at, t1: i < SHOTS.length - 1 ? SHOTS[i + 1].at : warp(DUR) }));

/* ---------- overlays above every look ---------- */
let COUNTER = [], COUNTER_LABEL = 'COUNT';  // [[from time, ['368', '24', ...]]] drawn top right; set both in common.js
let NFA = false;                          // "NOT FINANCIAL ADVICE" small, bottom left
function counter(t, s) {
  if (s.noCounter) return; let cur = null, t0 = 0; for (const [at, v] of COUNTER) if (t >= at) { cur = v; t0 = at; } if (!cur) return;
  const p = eo((t - t0) / .35), parts = cur, h = 72, pad = 24;
  ctx.save(); ctx.font = `800 40px ${FONT.mono}`; const arrow = '  →  ';
  const wTxt = parts.reduce((a, s, i) => a + ctx.measureText(s).width + (i ? ctx.measureText(arrow).width : 0), 0);
  ctx.font = `700 15px ${FONT.mono}`; const wLab = ctx.measureText(COUNTER_LABEL).width;
  const w = Math.max(wTxt, wLab) + pad * 2, x = SAFE.r - w, y = SAFE.t;
  ctx.globalAlpha = .4 + .6 * p; ctx.fillStyle = OV.panel; ctx.beginPath(); ctx.roundRect(x, y, w, h + 26, 12); ctx.fill();
  ctx.strokeStyle = OV.line; ctx.lineWidth = 2; ctx.stroke();
  ctx.fillStyle = OV.dim; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic'; ctx.fillText(COUNTER_LABEL, x + pad, y + 26);
  ctx.font = `800 40px ${FONT.mono}`; let xx = x + pad;
  parts.forEach((s, i) => { if (i) { ctx.fillStyle = OV.dim; ctx.fillText(arrow, xx, y + 78); xx += ctx.measureText(arrow).width; }
    const last = i === parts.length - 1; ctx.fillStyle = last ? OV.hot : OV.ink;
    if (last && p < 1) { ctx.save(); ctx.translate(xx, y + 78); ctx.scale(lerp(1.4, 1, back(p)), lerp(1.4, 1, back(p))); ctx.fillText(s, 0, 0); ctx.restore(); }
    else ctx.fillText(s, xx, y + 78); xx += ctx.measureText(s).width; });
  ctx.restore();
}
function nfa() { if (!NFA) return; ctx.save(); ctx.font = `700 18px ${FONT.mono}`; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  const s = 'NOT FINANCIAL ADVICE', w = ctx.measureText(s).width + 24; ctx.fillStyle = OV.panel; ctx.beginPath(); ctx.roundRect(SAFE.l, SAFE.b - 34, w, 34, 8); ctx.fill();
  ctx.fillStyle = OV.dim; ctx.fillText(s, SAFE.l + 12, SAFE.b - 11); ctx.restore(); }
// EXAMPLE tag: every illustration carries one
function example(x, y, a = 1, s = 'EXAMPLE') { if (a <= 0) return; ctx.save(); ctx.globalAlpha *= a; ctx.font = `800 28px ${FONT.mono}`; ctx.textAlign = "left"; ctx.textBaseline = "middle";
  const w = ctx.measureText(s).width + 28; ctx.fillStyle = OV.tag; ctx.beginPath(); ctx.roundRect(x, y - 23, w, 46, 6); ctx.fill();
  ctx.fillStyle = OV.tagInk; ctx.fillText(s, x + 14, y + 1); ctx.restore(); return w; }
// fake label: every shot that shows content made up for the test (a planted page, invented numbers, a made-up company)
// carries it, outside the fake itself, for as long as the fake is on screen. Set FAKE_LABEL in common.js.
let FAKE_LABEL = 'MADE UP FOR THIS TEST';
function fakeLabel(x, y, a = 1, size = 26, align = 'center', s = FAKE_LABEL) {
  if (a <= 0) return; ctx.save(); ctx.globalAlpha *= clamp(a); ctx.font = `800 ${size}px ${FONT.mono}`; ctx.textBaseline = 'middle';
  const w = ctx.measureText(s).width + size * 1.6, h = size * 1.9, x0 = align === 'center' ? x - w / 2 : align === 'right' ? x - w : x;
  ctx.fillStyle = OV.panel; ctx.beginPath(); ctx.roundRect(x0, y - h / 2, w, h, 8); ctx.fill();
  ctx.strokeStyle = OV.hot; ctx.lineWidth = 3; ctx.stroke(); ctx.fillStyle = OV.hot; ctx.textAlign = 'left'; ctx.fillText(s, x0 + size * .8, y + 1);
  ctx.restore();
}

/* ---------- slates: bright placeholders for the creator's own screen recordings ---------- */
function slate(id, what, hide, t0, t1, t) {
  const v0 = unwarp(t0), v1 = unwarp(t1), left = Math.max(0, v1 - TRAW), total = v1 - v0;   // in video time
  ctx.fillStyle = OV.slate; ctx.fillRect(0, 0, W, H);
  ctx.save(); ctx.globalAlpha = .12; ctx.fillStyle = OV.slateInk; for (let x = -H; x < W; x += 90) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x + 40, 0); ctx.lineTo(x + 40 + H, H); ctx.lineTo(x + H, H); ctx.fill(); } ctx.restore();
  ctx.fillStyle = OV.slate; ctx.fillRect(SAFE.l, SAFE.t, SAFE.r - SAFE.l, SAFE.b - SAFE.t);
  ctx.strokeStyle = OV.slateInk; ctx.lineWidth = 6; ctx.strokeRect(SAFE.l, SAFE.t, SAFE.r - SAFE.l, SAFE.b - SAFE.t);
  ctx.textBaseline = 'alphabetic'; ctx.textAlign = 'left'; ctx.fillStyle = OV.slateInk;
  ctx.font = `800 30px ${FONT.mono}`; ctx.fillText('YOUR SCREEN RECORDING GOES HERE · LAY IT OVER THIS SLATE IN CAPCUT', SAFE.l + 50, SAFE.t + 70);
  ctx.font = `900 190px ${FONT.sans}`; ctx.fillText(id, SAFE.l + 44, SAFE.t + 270);
  ctx.font = `800 54px ${FONT.sans}`; wrap(what, SAFE.l + 50, SAFE.t + 370, 1160, 66);
  ctx.font = `600 30px ${FONT.mono}`; ctx.fillStyle = OV.slateDim; wrap('HIDE: ' + hide, SAFE.l + 50, SAFE.t + 640, 1160, 40);
  ctx.textAlign = 'right'; ctx.fillStyle = OV.slateHot; ctx.font = `900 260px ${FONT.mono}`; ctx.fillText(left.toFixed(1), SAFE.r - 50, SAFE.t + 610);
  ctx.font = `800 34px ${FONT.mono}`; ctx.fillText('SECONDS LEFT', SAFE.r - 56, SAFE.t + 670);
  ctx.fillStyle = OV.slateInk; ctx.font = `700 28px ${FONT.mono}`; ctx.fillText(`SLOT LENGTH ${total.toFixed(2)} s · VOICE KEEPS PLAYING`, SAFE.r - 56, SAFE.b - 60);
  ctx.fillStyle = OV.slateDim; ctx.fillRect(SAFE.l + 50, SAFE.b - 40, (SAFE.r - SAFE.l - 100), 12);
  ctx.fillStyle = OV.slateHot; ctx.fillRect(SAFE.l + 50, SAFE.b - 40, (SAFE.r - SAFE.l - 100) * clamp((TRAW - v0) / total), 12);
}
function wrap(s, x, y, maxW, lh) { const words = s.split(' '); let line = '', yy = y;
  for (const w of words) { const tr = line ? line + ' ' + w : w; if (ctx.measureText(tr).width > maxW && line) { ctx.fillText(line, x, yy); line = w; yy += lh; } else line = tr; }
  ctx.fillText(line, x, yy); return yy; }
LOOKS.slate = { begin() {}, end() {}, dim: OV.slateDim };
// a hole where tools/build.sh lays real footage; sheets show the label instead
function clipHole(x, y, w, h, label) { ctx.fillStyle = OV.hole; ctx.fillRect(x, y, w, h); ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip(); ctx.font = `700 26px ${FONT.mono}`; ctx.fillStyle = OV.dim; ctx.textAlign = 'center';
  ctx.fillText('REAL FOOTAGE · ' + label, x + w / 2, y + h / 2); ctx.restore(); }

/* ---------- optional captions (?caps): white on a dark pill, bottom centre ---------- */
const QS = new URLSearchParams(location.search), CAP_ON = QS.has('caps');
function captions(t) {
  if (!CAP_ON || typeof CAPS === 'undefined') return; const c = CAPS.find((c, i) => t >= c[1] && t < Math.max(c[2] + .25, (CAPS[i + 1] || [0, 1e9])[1] - .02) && t < c[2] + .7); if (!c) return;
  ctx.save(); ctx.font = `700 40px ${FONT.sans}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; const w = ctx.measureText(c[0]).width + 60;
  ctx.fillStyle = 'rgba(8,8,8,.82)'; ctx.beginPath(); ctx.roundRect(960 - w / 2, 930, w, 64, 26); ctx.fill(); ctx.fillStyle = '#fff'; ctx.fillText(c[0], 960, 963); ctx.restore();
}

/* ---------- the frame ---------- */
let TRAW = 0;
const SNAP = Object.assign(document.createElement('canvas'), { width: W, height: H }).getContext('2d');
// a frame around a real clip: torn paper and tape on 'paper', a white rule on riso; the clip is laid in by tools/compose.py
function frame(x, y, w, h, label, seed = 0, look = 'paper') {
  if (look === 'paper') { PC.piece(() => PC.torn(x - 26, y - 26, w + 52, h + 52, seed + 5, 3, 16), PC.C.cream); PC.tape(x + w * .2, y - 22, 170, -.06); PC.tape(x + w * .8, y - 22, 170, .07); }
  else { ctx.lineWidth = 4; ctx.strokeStyle = R.C.white; ctx.strokeRect(x - 10, y - 10, w + 20, h + 20); }
  clipHole(x, y, w, h, label);
}
// a window's title above its clips: dymo tape on paper, mono print on riso
function winTitle(s, x, y, look, maxW = 1600) {
  ctx.save(); const size = look === 'paper' ? 30 : 32; ctx.font = `900 ${size}px ${FONT.sans}`; const k = Math.min(1, maxW / (ctx.measureText(s).width + 60)); ctx.restore();
  if (look === 'paper') PC.dymo(s, x, y, Math.floor(30 * k), -.01, 1); else R.mono(s, x, y, Math.floor(32 * k), R.C.white, 'center', 800);
}
// a window's frames and titles (the clips themselves are laid in by tools/compose.py)
function winFrames(w, t, p) {
  const look = winLook(w, SHOTS[shotAt(t)]);
  w.rects.forEach((r, i) => frame(r.x, r.y, r.w, r.h, w.items[i].title || 'real run', i + 3, look));
  if (w.title) winTitle(w.title, w.mode === 'split' ? 1214 + 323 : 960, (w.rects[0] ? Math.min(...w.rects.map(r => r.y)) : 140) - 46, look, w.mode === 'split' ? 600 : 1600);
}
function draw(traw) {
  TRAW = traw; const t = warp(traw); T = t; Q = Math.floor(t * 12);
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  const i = shotAt(t), s = SHOTS[i], lt = t - s.at, dur = (i < SHOTS.length - 1 ? SHOTS[i + 1].at : DUR) - s.at, L = LOOKS[s.look];
  const w = winAt(t), reset = () => { ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; };
  if (w && w.mode === 'full') {   // the shot's clock keeps running underneath; only the window is drawn
    const L2 = LOOKS[winLook(w, s)], wl = t - w.c0;
    L2.begin(wl, w.t1 - w.c0, {}); ctx.save(); winFrames(w, t, 1); ctx.restore(); reset(); L2.end(wl, w.t1 - w.c0, {}); reset();
  } else {
    L.begin(lt, dur, s); ctx.save(); s.draw(lt, t, dur); ctx.restore(); reset();
    L.end(lt, dur, s); reset();
    if (w && w.mode === 'split') {
      SNAP.drawImage(cv, 0, 0); const p = eo((t - w.c0) / .3), L2 = LOOKS[winLook(w, s)];
      L2.begin(9, 99, {}); reset();
      const x = lerp(0, SPLIT.x, p), y = lerp(0, SPLIT.y, p), ww = lerp(W, SPLIT.w, p), hh = lerp(H, SPLIT.h, p);
      ctx.save(); ctx.shadowColor = 'rgba(0,0,0,.5)'; ctx.shadowBlur = 30; ctx.drawImage(SNAP.canvas, x, y, ww, hh); ctx.restore();
      ctx.strokeStyle = OV.line; ctx.lineWidth = 2; ctx.strokeRect(x, y, ww, hh);
      ctx.save(); ctx.translate((1 - p) * 760, 0); winFrames(w, t, p); ctx.restore(); reset(); L2.end(9, 99, {}); reset();
    } else if (w && w.mode === 'punch') {   // push in on the finished frame, slowly drifting further
      SNAP.drawImage(cv, 0, 0); const k = lerp(1, w.k || 1.2, eo((t - w.t0) / .35)) * (1 + .012 * (t - w.t0)), cx = w.cx ?? 960, cy = w.cy ?? 540;
      ctx.drawImage(SNAP.canvas, cx - cx * k, cy - cy * k, W * k, H * k);
    } else if (w && w.mode === 'pip') { winFrames(w, t, 1); reset(); }
  }
  counter(t, s); nfa(); captions(t);
}

/* ---------- player (Space play/pause · R restart · ← → shot · H hide) ---------- */
let tt = 0, playing = false, prev = null, au = null, auOK = false;
function start() {
  SHOTS.sort((a, b) => a.at - b.at); if (QS.has('clean')) document.body.classList.add('clean');
  tt = QS.has('t') ? clamp(+QS.get('t'), 0, DUR - .001) : 0; playing = !QS.has('t') && !QS.has('clean');
  au = new Audio(typeof VOICE !== 'undefined' ? VOICE : ''); au.addEventListener('canplay', () => { auOK = true; }); au.addEventListener('error', () => { auOK = false; });
  const bar = document.getElementById('bar'), fillEl = document.getElementById('fill'), info = document.getElementById('info');
  SHOTS.slice(1).forEach(s => { const e = document.createElement('i'); e.className = 'tick'; e.style.left = (s.at / DUR * 100) + '%'; bar.appendChild(e); });
  const sync = () => { if (!auOK) return; if (playing) { if (au.paused) { au.currentTime = tt; au.play().catch(() => {}); } else if (Math.abs(au.currentTime - tt) > .15) au.currentTime = tt; } else if (!au.paused) au.pause(); };
  const frame = now => { if (playing && prev !== null) { tt += Math.min(.1, (now - prev) / 1000); if (tt >= DUR) { tt = 0; if (auOK) au.currentTime = 0; } }
    prev = now; draw(tt); sync(); fillEl.style.width = (tt / DUR * 100) + '%';
    info.textContent = `${TITLE} · ${tt.toFixed(1)} / ${DUR}s · ${SHOTS[shotAt(tt)].name}${auOK ? ' · voice ✓' : ''}${playing ? '' : ' · paused'}${ERRS.length ? ' · ERR ' + ERRS[0] : ''}`;
    if (!QS.has('clean')) requestAnimationFrame(frame); };
  addEventListener('keydown', e => { const k = e.key.toLowerCase(), i = shotAt(tt);
    if (k === ' ') { playing = !playing; e.preventDefault(); } else if (k === 'r') { tt = 0; playing = true; if (auOK) au.currentTime = 0; }
    else if (k === 'arrowright') tt = SHOTS[Math.min(SHOTS.length - 1, i + 1)].at; else if (k === 'arrowleft') tt = SHOTS[tt - SHOTS[i].at > .3 ? i : Math.max(0, i - 1)].at;
    else if (k === 'h') document.body.classList.toggle('clean'); });
  bar.onclick = e => { const r = bar.getBoundingClientRect(); tt = clamp((e.clientX - r.left) / r.width) * DUR * .9999; };
  cv.onclick = () => { playing = !playing; };
  window.seek = s => { tt = s; playing = false; draw(tt); };
  // everything handed to the mixer and compositor is in video time
  window.pageData = () => JSON.stringify({ DUR, ERRS, VOICE_END, SFX: SFX.map(([t, n, g]) => [+unwarp(t).toFixed(3), n, g]),
    CLIPS: CLIPS.map(c => ({ ...c, t0: unwarp(c.t0), t1: Math.min(DUR, unwarp(c.t1)) })), WINS: WINS.map(w => ({ mode: w.mode, t0: unwarp(w.t0), t1: Math.min(DUR, unwarp(w.t1)) })), SPANS: shotSpans().map(x => ({ ...x, t0: unwarp(x.t0), t1: unwarp(x.t1) })) });
  Promise.race([Promise.all(['900 64px Inter', '700 40px "JetBrains Mono"', '900 40px Inter'].map(f => document.fonts.load(f))), new Promise(r => setTimeout(r, 2500))])
    .finally(() => { window.READY = true; requestAnimationFrame(frame); draw(tt); });
}
// one call per recording slot: a slate shot from t0 to t1 (the next shot must start at t1)
function recSlot(id, what, hide, t0, t1) { shot(t0, 'slate', id, (lt, t) => slate(id, what, hide, t0, t1, t), { rec: { id, what, hide } }); }
