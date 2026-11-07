/* sattrack.js · a real GOES-19 loop (prep_goes.py) with AIFS's forecast track printed on top in riso ink and the
   IBTrACS best track as a thin white dash. Used by the cold open, the hurricanes chapter and the style preview.
   box = {x, y, s} square on screen; o.loop = seconds the loop takes; o.ai = [t0, t1] track draw; o.best = [t0, t1];
   o.ref = time the landfall / closest-approach ring lands; o.zoom = slow push per second. */
function satTrack(lt, name, box, o = {}) {
  const G = window.GOES[name], IM = satTrack.img[name] || (satTrack.img[name] = window.GOES_IMG[name].map(src => Object.assign(new Image(), { src })));
  const loop = o.loop || 10, fi = Math.min(G.frames - 1, Math.floor(clamp(lt / loop) * (G.frames - 1)));
  const k = box.s / G.px * (1 + (o.zoom ?? .005) * lt), cx = box.x + box.s / 2, cy = box.y + box.s / 2;
  const P = ([x, y]) => [cx + (x - G.px / 2) * k, cy + (y - G.px / 2) * k];
  ctx.save(); ctx.beginPath(); ctx.rect(box.x, box.y, box.s, box.s); ctx.clip();
  ctx.fillStyle = '#000'; ctx.fillRect(box.x, box.y, box.s, box.s);
  const im = IM[fi]; if (im.complete && im.naturalWidth) ctx.drawImage(im, cx - G.px / 2 * k, cy - G.px / 2 * k, G.px * k, G.px * k);
  const [b0, b1] = o.best || [5.2, 6.8], pb = clamp((lt - b0) / (b1 - b0)), nb = Math.floor(pb * (G.best.length - 1));
  if (pb > 0) { ctx.save(); ctx.setLineDash([10, 9]); ctx.lineWidth = 5; ctx.strokeStyle = R.C.white; ctx.shadowColor = '#000'; ctx.shadowBlur = 6; ctx.beginPath();
    G.best.slice(0, nb + 1).forEach((b, i) => i ? ctx.lineTo(...P(b.px)) : ctx.moveTo(...P(b.px))); ctx.stroke(); ctx.restore(); }
  const [a0, a1] = o.ai || [.6, 5.2], pa = clamp((lt - a0) / (a1 - a0)), na = pa * (G.ai.length - 1), pts = G.ai.map(a => P(a.px));
  const path = off => { ctx.beginPath(); pts.forEach((p, i) => { if (i > Math.ceil(na)) return; const q = i <= na ? p : [lerp(pts[i - 1][0], p[0], na % 1), lerp(pts[i - 1][1], p[1], na % 1)];
    i ? ctx.lineTo(q[0] + off, q[1] + off) : ctx.moveTo(q[0] + off, q[1] + off); }); };
  if (pa > 0) { ctx.lineCap = ctx.lineJoin = 'round'; ctx.lineWidth = 11; ctx.strokeStyle = R.pat(R.P.b); path(6); ctx.stroke(); ctx.strokeStyle = R.C.orange; path(0); ctx.stroke();
    pts.forEach((p, i) => { if (i > na) return; ctx.beginPath(); ctx.arc(p[0], p[1], i % 4 ? 6 : 11, 0, 7); R.fills(R.C.paper, R.P.o); ctx.lineWidth = 3; ctx.strokeStyle = R.C.orange; ctx.stroke(); }); }
  const pr = clamp((lt - (o.ref ?? 6.6)) / .4); if (pr > 0) { const [rx, ry] = P(G.ref_px); ctx.lineWidth = 4; ctx.strokeStyle = R.C.white; ctx.beginPath(); ctx.arc(rx, ry, 30 * back(pr), 0, 7); ctx.stroke(); }
  ctx.restore();
  ctx.strokeStyle = R.C.white; ctx.lineWidth = 3; ctx.strokeRect(box.x, box.y, box.s, box.s);
  R.mono(`${G.frame_times[fi]} UTC`, box.x + box.s - 20, box.y + 40, 20, R.C.white, 'right', 600);
  return G;
}
satTrack.img = {};
// decode every loaded storm's frames before the page reports READY (a first draw with undecoded frames comes out black)
(() => { const ps = []; for (const [name, srcs] of Object.entries(window.GOES_IMG || {})) {
    satTrack.img[name] = srcs.map(src => { const im = new Image(); im.src = src; ps.push(im.decode().catch(() => {})); return im; }); }
  const start0 = start; start = () => Promise.all(ps).finally(start0); })();
// the legend column beside a satellite box (left side), each line fading in at its own time
function satLegend(lt, G, x, t = { title: 0, ai: .8, best: 5.2 }) {
  R.printLine(`HURRICANE ${G.storm}`, x, 150, 40, R.C.white, (lt - t.title) / .5, 'left');
  R.fade((lt - t.title - .4) / .4, () => R.mono(G.ref_event.split(' (')[0], x + 2, 196, 20, R.C.dim, 'left', 600));
  R.fade((lt - t.ai) / .4, () => { ctx.lineWidth = 9; ctx.strokeStyle = R.C.orange; ctx.beginPath(); ctx.moveTo(x + 2, 300); ctx.lineTo(x + 70, 300); ctx.stroke();
    R.mono('AI forecast', x + 85, 309, 24, R.C.orange, 'left', 800); R.mono(`made ${G.days_before} days before`, x + 85, 341, 20, R.C.dim, 'left', 600); });
  R.fade((lt - t.best) / .4, () => { ctx.save(); ctx.setLineDash([10, 9]); ctx.lineWidth = 4; ctx.strokeStyle = R.C.white; ctx.beginPath(); ctx.moveTo(x + 2, 410); ctx.lineTo(x + 70, 410); ctx.stroke(); ctx.restore();
    R.mono('what happened', x + 85, 419, 24, R.C.white, 'left', 800); R.mono('IBTrACS best track', x + 85, 451, 20, R.C.dim, 'left', 600); });
}
