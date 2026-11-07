/* 90 · Style preview (~41 s). Six shots, one per look, every number from DATA (preview/export.py) or GOES
   (preview/prep_goes.py). The hook line plays over the cold open. */
const S2 = 10, S3 = 15, S4 = 23, S5 = 27, S6 = 35;
const tag = (s, x, y) => example(x, y, 1, s);           // the PAPER MONEY / REAL MONEY label pill

/* ---------- 1 · cold open: real GOES-19 loop, the AI's track drawing on top in riso ink ---------- */
const G = window.GOES, IMG = Array.from({ length: G.frames }, (_, i) => Object.assign(new Image(), { src: window.GOES_IMG[i] }));
const SAT = { x: 420, y: 0, s: 1080 };
shot(0, 'riso', 'cold open: satellite + AI track', (lt) => {
  const k = SAT.s / G.px * (1 + .05 * lt / 10), cx = SAT.x + SAT.s / 2, cy = SAT.s / 2;
  const P = ([x, y]) => [cx + (x - G.px / 2) * k, cy + (y - G.px / 2) * k];
  const im = IMG[Math.min(G.frames - 1, Math.floor(lt / 10 * G.frames))];
  ctx.save(); ctx.beginPath(); ctx.rect(SAT.x, SAT.y, SAT.s, SAT.s); ctx.clip();
  if (im.complete && im.naturalWidth) ctx.drawImage(im, cx - G.px / 2 * k, cy - G.px / 2 * k, G.px * k, G.px * k);
  // what happened (IBTrACS), thin white, after the AI's line
  const pb = clamp((lt - 5.2) / 1.6), nb = Math.floor(pb * (G.best.length - 1));
  if (pb > 0) { ctx.save(); ctx.setLineDash([10, 9]); ctx.lineWidth = 5; ctx.strokeStyle = R.C.white; ctx.shadowColor = '#000'; ctx.shadowBlur = 6; ctx.beginPath();
    G.best.slice(0, nb + 1).forEach((b, i) => i ? ctx.lineTo(...P(b.px)) : ctx.moveTo(...P(b.px))); ctx.stroke(); ctx.restore(); }
  // the AI's forecast track, printed in riso ink: brick plate offset, orange on top, a dot every 6 h
  const pa = clamp((lt - .6) / 4.6), na = pa * (G.ai.length - 1), pts = G.ai.map(a => P(a.px));
  const path = off => { ctx.beginPath(); pts.forEach((p, i) => { if (i > Math.ceil(na)) return; const q = i <= na ? p : [lerp(pts[i - 1][0], p[0], na % 1), lerp(pts[i - 1][1], p[1], na % 1)];
    i ? ctx.lineTo(q[0] + off, q[1] + off) : ctx.moveTo(q[0] + off, q[1] + off); }); };
  if (pa > 0) { ctx.lineCap = ctx.lineJoin = 'round'; ctx.lineWidth = 11; ctx.strokeStyle = R.pat(R.P.b); path(6); ctx.stroke(); ctx.strokeStyle = R.C.orange; path(0); ctx.stroke();
    pts.forEach((p, i) => { if (i > na) return; ctx.beginPath(); ctx.arc(p[0], p[1], i % 4 ? 6 : 11, 0, 7); R.fills(R.C.paper, R.P.o); ctx.lineWidth = 3; ctx.strokeStyle = R.C.orange; ctx.stroke(); }); }
  const pr = clamp((lt - 6.6) / .4); if (pr > 0) { const [rx, ry] = P(G.ref_px); ctx.lineWidth = 4; ctx.strokeStyle = R.C.white; ctx.beginPath(); ctx.arc(rx, ry, 30 * back(pr), 0, 7); ctx.stroke(); }
  ctx.restore();
  ctx.strokeStyle = R.C.white; ctx.lineWidth = 3; ctx.strokeRect(SAT.x, SAT.y, SAT.s, SAT.s);
  R.mono(`${G.frame_times[Math.min(G.frames - 1, Math.floor(lt / 10 * G.frames))]} UTC`, SAT.x + SAT.s - 20, 40, 20, R.C.white, 'right', 600);
  // left column: what this is; right column: the payoff number first
  R.printLine(`HURRICANE ${G.storm}`, 60, 150, 40, R.C.white, lt / .5, 'left');
  R.fade((lt - .4) / .4, () => { R.mono('landfall, Jamaica', 62, 196, 22, R.C.dim, 'left', 600); });
  R.fade((lt - .8) / .4, () => { ctx.lineWidth = 9; ctx.strokeStyle = R.C.orange; ctx.beginPath(); ctx.moveTo(62, 300); ctx.lineTo(130, 300); ctx.stroke();
    R.mono('AI forecast', 145, 309, 24, R.C.orange, 'left', 800); R.mono(`made ${G.days_before} days before`, 145, 341, 20, R.C.dim, 'left', 600); });
  R.fade((lt - 5.2) / .4, () => { ctx.save(); ctx.setLineDash([10, 9]); ctx.lineWidth = 4; ctx.strokeStyle = R.C.white; ctx.beginPath(); ctx.moveTo(62, 410); ctx.lineTo(130, 410); ctx.stroke(); ctx.restore();
    R.mono('what happened', 145, 419, 24, R.C.white, 'left', 800); R.mono('IBTrACS best track', 145, 451, 20, R.C.dim, 'left', 600); });
  R.fade((lt - 2.2) / .3, () => R.mono('LANDFALL MISS', 1690, 420, 24, R.C.dim, 'center', 700));
  R.printLine(`${G.ref_error_km} km`, 1690, 500, 64, R.C.orange, (lt - 2.4) / .5, 'center');
  ctx.fillStyle = 'rgba(15,13,12,.85)'; ctx.fillRect(SAT.x, SAFE.b - 34, SAT.s, 44);
  R.src('NOAA GOES-19 ABI band 13 IR · track: ECMWF AIFS (archived run) vs IBTrACS', (lt - 1) / .5);
}, { noCounter: true });
sfx(.6, 'whoosh', .35); sfx(2.4, 'thunk', .5); sfx(6.6, 'tick', .4);

/* ---------- 2 · EVIDENCE: the NWS forecast with a highlighter, next to the bot's v1 number ---------- */
shot(S2, 'evidence', 'evidence: NWS vs bot', (lt) => {
  const P = DATA.pfm, V = DATA.v1, lines = P.lines.slice(0, P.lines.findIndex(l => l.startsWith('QPF 12hr')) + 1), size = 18, lh = 25;
  EV.sheet(90, 120, 1010, lines.length * lh + 90, -.008, () => {
    ctx.font = `500 ${size}px ${FONT.mono}`; const cw = ctx.measureText('0').width;
    lines.forEach((l, i) => { if (i === P.row) EV.hilite(40 + cw * P.col, 60 + i * lh, cw * P.val.length, size, (lt - .9) / .5);
      EV.text(l, 40, 60 + i * lh, size, EV.C.ink, i === P.row ? 700 : 500); });
    // a circle around the highlighted max, drawn by hand
    const pc = clamp((lt - 1.5) / .5); if (pc > 0) { const x = 40 + cw * (P.col + P.val.length / 2), y = 60 + P.row * lh - size * .35;
      ctx.lineWidth = 3.5; ctx.strokeStyle = EV.C.red; ctx.beginPath(); ctx.ellipse(x, y, 34, 22, -.1, -1.4, -1.4 + 6.4 * eo(pc)); ctx.stroke(); }
  });
  // the bot's dry-run log line, as a card
  const pb = eo((lt - 1.8) / .45), bx = lerp(1300, 1160, pb);
  if (pb > 0) { ctx.save(); ctx.globalAlpha *= pb; ctx.fillStyle = EV.C.card; ctx.shadowColor = 'rgba(40,30,15,.4)'; ctx.shadowBlur = 24; ctx.fillRect(bx, 250, 680, 400); ctx.shadowColor = 'transparent';
    EV.text(`BOT v1 · ${DATA.v1.mode} LOG · market day ${V.market_day}`, bx + 30, 300, 18, 'rgba(242,234,221,.6)', 600);
    EV.text(`KPHX raw AIFS   ${V.raw.toFixed(2)}°F`, bx + 30, 360, 24, EV.C.cardInk, 600);
    EV.text(`v1 corrected    ${V.corrected.toFixed(2)}°F`, bx + 30, 405, 24, EV.C.cardInk, 800);
    EV.text(`${V.pick.ticker}`, bx + 30, 470, 20, 'rgba(242,234,221,.75)', 500);
    EV.text(`${V.pick.side} "${V.pick.bracket}" @ $${V.pick.price.toFixed(2)}`, bx + 30, 505, 20, EV.C.cardInk, 600);
    EV.text(`edge ${V.pick.edge}`, bx + 30, 540, 20, EV.C.cardInk, 600);
    const ph = clamp((lt - 2.6) / .4); if (ph > 0) { ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.fillStyle = 'rgba(255,227,71,.55)'; ctx.font = `800 24px ${FONT.mono}`;
      ctx.fillRect(bx + 26, 380, ctx.measureText(`v1 corrected    ${V.corrected.toFixed(2)}°F`).width * eo(ph) + 8, 34); ctx.restore(); }
    ctx.restore(); }
  // the comparison, big
  const pv = clamp((lt - 3.1) / .4);
  if (pv > 0) { ctx.save(); ctx.globalAlpha *= pv; EV.text(`NWS ${V.nws}°F`, 1200, 760, 52, EV.C.ink, 900, FONT.sans); EV.text('vs', 1478, 760, 30, EV.C.dim, 700, FONT.sans);
    EV.text(`BOT ${V.corrected}°F`, 1545, 760, 52, EV.C.red, 900, FONT.sans); ctx.restore(); }
  EV.source(`SOURCE: ${P.product} · ${P.issued.split('(')[1].replace(')', '')}`, 96, 1010);
  EV.source(`SOURCE: bot dry-run log, ${V.log_day} (no money)`, 1824, 1010, 'right');
}, { noCounter: true });
sfx(S2, 'paper', .5); sfx(S2 + .9, 'swish', .35); sfx(S2 + 1.8, 'paper', .4); sfx(S2 + 3.1, 'thunk', .5);

/* ---------- 3 · the bug: Phoenix TRAIN scatter, the v1 line extended to the October day (riso) ---------- */
shot(S3, 'riso', 'the bug: extrapolation', (lt) => {
  R.printLine('THE BUG · PHOENIX', 96, 110, 44, R.C.white, lt / .5, 'left');
  bugScatter(lt, { x: 300, y: 170, w: 1400, h: 700 }, 1);
  tag('PAPER MONEY', 1580, 92);
  R.src(`results/evidence/v1-bug/summary.json · TRAIN ${DATA.v1.train_from} → ${DATA.v1.train_to}`, (lt - .5) / .5);
}, { noCounter: true });
sfx(S3, 'whoosh', .3); sfx(S3 + 1.9, 'swish', .4); sfx(S3 + 4.3, 'thunk', .6);

/* ---------- 4 · CRT: the real AIFS run log scrolling ---------- */
shot(S4, 'crt', 'crt: AIFS run log', (lt) => {
  const A = DATA.aifs, n = Math.min(A.lines.length, Math.floor(lt * A.lines.length / 3.2) + 1), vis = 22, first = Math.max(0, n - vis);
  CR.statusBar('AIFS SINGLE v2 · 10-DAY RUN · DGX SPARK', 'REAL LOG');
  A.lines.slice(first, n).forEach((l, i) => CR.tx(l.slice(0, 100), 16, 46 + i * 12.6, 10, l.startsWith('saved') || l.startsWith('WALL') ? CR.C.gh : CR.C.g));
  if (lt > 3.3) CR.tx(`10-DAY FORECAST · ${Math.round(A.wall_s)} s`, 320, 338, 16, CR.C.gh, { wt: 700, align: 'center', inv: true });
}, { boot: true, noCounter: true });

/* ---------- 5 · backtest: the four players' paper P&L lines racing ---------- */
const COL = { gfs: () => R.C.dim, aifs_raw: () => R.C.brick, aifs_cor: () => R.C.white, aifs_cor_judge: () => R.C.orange };
shot(S5, 'riso', 'backtest race (PAPER MONEY)', (lt) => {
  const B = DATA.bt.players, b = { x: 200, y: 200, w: 1180, h: 700 }, lo = -110, hi = 10;
  const ds = B.flatMap(p => p.curve.map(c => Date.parse(c[0]))), d0 = Math.min(...ds), d1 = Math.max(...ds);
  const X = d => b.x + (Date.parse(d) - d0) / (d1 - d0) * b.w, Y = v => b.y + (hi - v) / (hi - lo) * b.h, now = lerp(d0, d1, eio((lt - .6) / 5.6));
  R.printLine('BACKTEST · TEST WINDOW', 96, 110, 44, R.C.white, lt / .5, 'left');
  R.mono(DATA.bt.split, 98, 150, 20, R.C.dim, 'left', 600); tag('PAPER MONEY', 1580, 92);
  ctx.lineWidth = 2; ctx.strokeStyle = R.C.faint; for (let v = -100; v <= 0; v += 25) { ctx.beginPath(); ctx.moveTo(b.x, Y(v)); ctx.lineTo(b.x + b.w, Y(v)); ctx.stroke(); R.mono(v ? `−$${-v}` : '$0', b.x - 14, Y(v) + 7, 20, R.C.dim, 'right', 600); }
  ctx.lineWidth = 3; ctx.strokeStyle = R.C.white; ctx.beginPath(); ctx.moveTo(b.x, Y(0)); ctx.lineTo(b.x + b.w, Y(0)); ctx.stroke();
  B.forEach((p, k) => { const pts = [[p.curve[0][0], 0], ...p.curve].filter(([d]) => Date.parse(d) <= now); if (pts.length < 1) return;
    const c = COL[p.key](), last = pts[pts.length - 1];
    ctx.lineCap = ctx.lineJoin = 'round'; ctx.lineWidth = 6; ctx.strokeStyle = c; ctx.beginPath(); pts.forEach(([d, v], i) => i ? ctx.lineTo(X(d), Y(v)) : ctx.moveTo(X(d), Y(v))); ctx.stroke();
    ctx.beginPath(); ctx.arc(X(last[0]), Y(last[1]), 10, 0, 7); R.fills(c);
    // the legend on the right counts with each line
    const ly = 260 + k * 150; ctx.lineWidth = 8; ctx.strokeStyle = c; ctx.beginPath(); ctx.moveTo(1430, ly - 8); ctx.lineTo(1475, ly - 8); ctx.stroke();
    R.mono(p.label, 1490, ly, 20, c === R.C.dim ? R.C.white : c, 'left', 700);
    R.mono(`${sgn(last[1])}`.replace(/^([+−])/, '$1$'), 1490, ly + 50, 40, c === R.C.dim ? R.C.white : c, 'left', 800);
    if (lt > 6.3) R.mono(`${p.bets} bets`, 1820, ly + 50, 20, R.C.dim, 'right', 600); });
  R.src('results/backtest.json · results/judge.json (TEST window only)', (lt - .5) / .5);
}, { noCounter: true });
sfx(S5, 'whoosh', .3); sfx(S5 + 6.2, 'thunk', .5);

/* ---------- 6 · stat card: the live-week result ---------- */
shot(S6, 'riso', 'stat card (REAL MONEY)', (lt) => {
  const L = DATA.live, v = L.pnl * eo((lt - .5) / 1.6);
  tag('REAL MONEY · $10 TEST', 760, 160);
  R.mono('THE LIVE WEEK', 960, 300, 30, R.C.dim, 'center', 800);
  R.printLine(`${v < 0 ? '−' : '+'}$${Math.abs(v).toFixed(2)}`, 960, 520, 200, L.pnl < 0 ? R.C.orange : R.C.white, lt / .4, 'center');
  R.fade((lt - 2.3) / .4, () => R.mono(`${L.orders} real orders · ${L.won} won · ${L.lost} lost · fees $${L.fees.toFixed(2)}`, 960, 640, 34, R.C.white, 'center', 700));
  R.fade((lt - 3.3) / .4, () => R.mono(`the bot crashed on day ${L.runs_completed + 1}: ${L.runs_completed} of ${L.runs_completed + L.runs_crashed} days traded`, 960, 710, 28, R.C.dim, 'center', 600));
  R.src('results/live.json · settled from Kalshi’s own records', (lt - .5) / .5);
}, { noCounter: true });
for (let i = 0; i < 8; i++) sfx(S6 + .5 + i * .2, 'tick', .25);
sfx(S6 + 2.1, 'thunk', .6);
