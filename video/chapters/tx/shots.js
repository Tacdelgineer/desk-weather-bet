/* shots.js · shots shared by the style preview (90) and the chapters. Every number from DATA (export.py). */
const tag = (s, x, y) => example(x, y, 1, s);           // the PAPER MONEY / REAL MONEY label pill
const COL = { gfs: () => R.C.dim, aifs_raw: () => R.C.brick, aifs_cor: () => R.C.white, aifs_cor_judge: () => R.C.orange };
function evNwsBot(lt) {
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
}
function crtAifsLog(lt) {
  const A = DATA.aifs, n = Math.min(A.lines.length, Math.floor(lt * A.lines.length / 3.2) + 1), vis = 22, first = Math.max(0, n - vis);
  CR.statusBar('AIFS SINGLE v2 · 10-DAY RUN · DGX SPARK', 'REAL LOG');
  A.lines.slice(first, n).forEach((l, i) => CR.tx(l.slice(0, 100), 16, 46 + i * 12.6, 10, l.startsWith('saved') || l.startsWith('WALL') ? CR.C.gh : CR.C.g));
  if (lt > 3.3) CR.tx(`10-DAY FORECAST · ${Math.round(A.wall_s)} s`, 320, 338, 16, CR.C.gh, { wt: 700, align: 'center', inv: true });
}
function backtestRace(lt) {
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
}
function liveCard(lt) {
  const L = DATA.live, v = L.pnl * eo((lt - .5) / 1.6);
  tag('REAL MONEY · $10 TEST', 760, 160);
  R.mono('THE LIVE WEEK', 960, 300, 30, R.C.dim, 'center', 800);
  R.printLine(`${v < 0 ? '−' : '+'}$${Math.abs(v).toFixed(2)}`, 960, 520, 200, L.pnl < 0 ? R.C.orange : R.C.white, lt / .4, 'center');
  R.fade((lt - 2.3) / .4, () => R.mono(`${L.n_orders} real orders · ${L.won} won · ${L.lost} lost · fees $${L.fees.toFixed(2)}`, 960, 640, 34, R.C.white, 'center', 700));
  R.fade((lt - 3.3) / .4, () => R.mono(`the bot crashed on day ${L.runs_completed + 1}: ${L.runs_completed} of ${L.runs_completed + L.runs_crashed} days traded`, 960, 710, 28, R.C.dim, 'center', 600));
  R.src('results/live.json · settled from Kalshi’s own records', (lt - .5) / .5);
}
function bugShot(lt) {
  R.printLine('THE BUG · PHOENIX', 96, 110, 44, R.C.white, lt / .5, 'left');
  bugScatter(lt, { x: 300, y: 170, w: 1400, h: 700 }, 1);
  tag('PAPER MONEY', 1580, 92);
  R.src(`results/evidence/v1-bug/summary.json · TRAIN ${DATA.v1.train_from} → ${DATA.v1.train_to}`, (lt - .5) / .5);
}

/* ---------- small shared builders ---------- */
const money = v => `${v < 0 ? '−' : '+'}$${Math.abs(v).toFixed(2)}`;
function head(lt, s, sub) { R.printLine(s, 96, 110, 44, R.C.white, lt / .5, 'left'); if (sub) R.fade((lt - .3) / .4, () => R.mono(sub, 98, 152, 22, R.C.dim, 'left', 600)); }
// horizontal bar groups (riso): rows = [{label, bars: [{v, col, txt}]}], max = value at full width; row i starts at t0 + i*stag
function hbars(lt, rows, box, max, o = {}) {
  const rh = box.h / rows.length, nb = rows[0].bars.length, bh = Math.min(30, (rh - 24) / nb);
  rows.forEach((r, i) => { const y = box.y + i * rh, p = eo((lt - (o.t0 ?? .5) - i * (o.stag ?? .25)) / .6);
    R.fade(p * 2, () => R.mono(r.label, box.x - 20, y + rh / 2 + 8, 24, R.C.white, 'right', 700));
    r.bars.forEach((b, k) => { const yy = y + (rh - nb * (bh + 8)) / 2 + k * (bh + 8), w = Math.max(2, box.w * Math.min(1, b.v / max) * p);
      ctx.beginPath(); ctx.rect(box.x + 5, yy + 5, w, bh); R.fills(R.P.b); ctx.beginPath(); ctx.rect(box.x, yy, w, bh); R.fills(b.col);
      R.fade((p - .7) * 4, () => R.mono(b.txt, box.x + w + 14, yy + bh * .78, Math.min(24, bh * .9), b.col === R.C.dim ? R.C.white : b.col, 'left', 800)); }); });
}
function legend(items, x, y, a = 1) { R.fade(a, () => items.forEach(([s, col], i) => { const xx = x + i * 330; ctx.fillStyle = col; ctx.fillRect(xx, y - 18, 40, 22);
  R.mono(s, xx + 54, y, 22, col === R.C.dim ? R.C.white : col, 'left', 700); })); }
