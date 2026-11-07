/* evweb.js · EVIDENCE shot of a real public web page (prep_web.py): the screenshot on a sheet, pushing in on the
   highlighted phrase, a yellow highlighter across it, the URL and capture date as the source label.
   o.zoom = final zoom on the phrase (1 = whole page); o.t = [push start, highlight start]; o.note = a caption line. */
const WEBIMG = {};
(() => { const ps = []; for (const [k, v] of Object.entries(window.WEB || {})) { const im = new Image(); im.src = v.img; WEBIMG[k] = im; ps.push(im.decode().catch(() => {})); }
  const s0 = start; start = () => Promise.all(ps).finally(s0); })();
function evWeb(lt, name, o = {}) {
  const P = window.WEB[name], im = WEBIMG[name], box = o.box || { x: 160, y: 70, w: 1600, h: 820 }, [t0, th] = o.t || [.6, 1.6];
  const r = (P.rects || [])[0], cx = r ? r[0] + r[2] / 2 : 960, cy = r ? r[1] + r[3] / 2 : 540;
  const z = lerp(1, o.zoom || (r ? 1.8 : 1.15), eio((lt - t0) / 1.2)) * (1 + .01 * lt);
  const fit = Math.min(box.w / 1920, box.h / 1080), sw = box.w / (fit * z), sh = box.h / (fit * z);
  const sx = clamp(cx - sw / 2, 0, 1920 - sw), sy = clamp(cy - sh / 2, 0, 1080 - sh), k = box.w / sw;
  EV.sheet(box.x, box.y, box.w, box.h, o.ang ?? -.004, () => {
    ctx.save(); ctx.beginPath(); ctx.rect(0, 0, box.w, box.h); ctx.clip();
    if (im.complete && im.naturalWidth) ctx.drawImage(im, sx, sy, sw, sh, 0, 0, box.w, box.h);
    (P.rects || []).forEach(q => EV.hilite((q[0] - sx) * k, (q[1] - sy + q[3] * .82) * k, q[2] * k, q[3] * k * .9, (lt - th) / .6));
    ctx.restore(); });
  if (o.note) R.fade((lt - th - .8) / .4, () => { ctx.save(); ctx.font = `800 34px ${FONT.sans}`; const w = ctx.measureText(o.note).width + 50;
    ctx.fillStyle = EV.C.card; ctx.fillRect(960 - w / 2, 918, w, 64); ctx.restore(); EV.text(o.note, 960, 961, 34, EV.C.cardInk, 800, FONT.sans, 'center'); });
  EV.source(`SOURCE: ${P.label} · ${P.url.replace(/^https?:\/\//, '')} · captured ${P.captured}${P.blurred ? ' · seller name blurred' : ''}`, 96, 1018);
}
