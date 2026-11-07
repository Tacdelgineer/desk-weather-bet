/* crt.js · wide green-phosphor terminal look (from tacdel-shorts styles/crt.html): scenes draw into a 640x360 screen
   buffer (CR.b) in screen pixels, then the look adds glow, scanlines, a roll bar, curved glass and power on/off.
   CR.glow() writes phosphor text straight onto other looks ("CRT text on riso"). All CRT colours live here. */
const CR = (() => {
  const C = { g: '#4dff86', gd: '#1f8a45', gh: '#d4ffe0', bg: '#03120a', bezel: '#050605', amber: '#ffb347', orange: '#ff4a0e' };   // orange: reads as orange after the green bloom
  const mk = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };
  const BW = 640, BH = 360, buf = mk(BW, BH), b = buf.getContext('2d'), blm = mk(160, 90), bl = blm.getContext('2d'), comp = mk(W, H), cc = comp.getContext('2d');
  const SCAN = (() => { const s = mk(1, 3), g = s.getContext('2d'); g.fillStyle = 'rgba(0,0,0,.55)'; g.fillRect(0, 2, 1, 1); return cc.createPattern(s, 'repeat'); })();
  function tx(s, x, y, size = 12, col = C.g, o = {}) {
    b.font = `${o.wt || 400} ${size}px ${FONT.mono}`; b.letterSpacing = '0.3px'; b.textAlign = o.align || 'left'; b.textBaseline = 'alphabetic';   // non-zero spacing turns ligatures off: code shows as typed (=> !==)
    const w = b.measureText(s).width, x0 = o.align === 'center' ? x - w / 2 : o.align === 'right' ? x - w : x;
    if (o.inv) { b.fillStyle = col; b.fillRect(x0 - 3, y - size * .86, w + 6, size * 1.1); b.fillStyle = C.bg; b.textAlign = 'left'; b.fillText(s, x0, y); } else { b.fillStyle = col; b.fillText(s, x, y); }
    return x0 + w; }
  const typed = (s, t, t0, cps = 40) => s.slice(0, clamp(Math.floor((t - t0) * cps), 0, s.length));
  function cursor(x, y, size = 12) { if ((T * 2.6) % 1 < .55) { b.fillStyle = C.g; b.fillRect(x + 1, y - size * .82, size * .58, size); } }
  const pad = (n, k = 2) => String(n).padStart(k, '0');
  function statusBar(title, right) { tx(title, 14, 20, 10, C.gd); if (right) tx(right, BW - 14, 20, 10, C.gd, { align: 'right' }); b.fillStyle = C.gd; b.fillRect(14, 27, BW - 28, 1); b.fillRect(14, BH - 22, BW - 28, 1); }
  function bigType(lines, t, t0, cps, x0, y0, size, lh) { let left = Math.floor((t - t0) * cps), cx = x0, cy = y0;
    lines.forEach((l, i) => { const s = l.s, part = s.slice(0, clamp(left, 0, s.length)); left -= s.length; if (!part) return; cy = y0 + i * lh;
      cx = tx(part, l.x ?? x0, cy, l.size || size, l.col || C.gh, { wt: 700, inv: l.inv && part.length === s.length, align: l.align }); });
    cursor(cx + 4, cy, size); }
  function bar(v, n) { const k = Math.round(clamp(v) * n); return '█'.repeat(k) + '░'.repeat(n - k); }
  // phosphor text drawn directly on the main canvas, over another look
  function glow(s, x, y, size, p = 1, align = 'center') { if (p <= 0) return; const part = s.slice(0, Math.ceil(s.length * clamp(p)));
    ctx.save(); ctx.font = `700 ${size}px ${FONT.mono}`; ctx.textAlign = align; ctx.textBaseline = 'alphabetic';
    ctx.shadowColor = C.g; ctx.shadowBlur = size * .5; ctx.fillStyle = C.g; ctx.fillText(part, x, y); ctx.shadowBlur = 0; ctx.fillStyle = C.gh; ctx.globalAlpha *= .55; ctx.fillText(part, x, y); ctx.restore(); }
  // a CRT monitor frame on another look (for real footage laid in by ffmpeg)
  function monitor(x, y, w, h) { ctx.fillStyle = C.bezel; ctx.beginPath(); ctx.roundRect(x - 34, y - 34, w + 68, h + 68, 46); ctx.fill(); ctx.strokeStyle = C.gd; ctx.lineWidth = 3; ctx.stroke();
    ctx.fillStyle = C.bg; ctx.fillRect(x, y, w, h); }
  const LOOK = { dim: C.gd,
    begin() { b.setTransform(1, 0, 0, 1, 0, 0); b.clearRect(0, 0, BW, BH); b.globalAlpha = 1; },
    end(lt, dur, s) {
      cc.globalCompositeOperation = 'source-over'; cc.globalAlpha = 1; cc.fillStyle = C.bg; cc.fillRect(0, 0, W, H);
      bl.clearRect(0, 0, 160, 90); bl.imageSmoothingEnabled = true; bl.drawImage(buf, 0, 0, 160, 90);
      cc.globalCompositeOperation = 'lighter'; cc.imageSmoothingEnabled = true; cc.globalAlpha = .75; cc.drawImage(blm, 0, 0, W, H);
      cc.globalAlpha = 1; cc.imageSmoothingEnabled = false; cc.drawImage(buf, 0, 0, W, H);
      cc.globalCompositeOperation = 'source-over'; cc.fillStyle = SCAN; cc.fillRect(0, 0, W, H);
      const by = ((T * .42) % 1.25) * H - 240, g = cc.createLinearGradient(0, by, 0, by + 300);
      g.addColorStop(0, 'rgba(110,255,150,0)'); g.addColorStop(.5, 'rgba(110,255,150,.06)'); g.addColorStop(1, 'rgba(110,255,150,0)'); cc.fillStyle = g; cc.fillRect(0, by, W, 300);
      ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, H);
      const on = s.boot ? eo(lt / .35) : 1, off = s.powerOff ? 1 - eio((lt - (dur - .4)) / .35) : 1, k = Math.min(on, off), sy = Math.max(.003, k);
      const glitch = lt < .12 && !s.boot, flick = .94 + rnd(Math.floor(T * 60)) * .06;
      ctx.save(); ctx.translate(0, H / 2); ctx.scale(1, sy); ctx.translate(0, -H / 2); ctx.globalAlpha = flick;
      for (let y = 0; y < H; y += 6) { const nx = (y + 3 - H / 2) / (H / 2), w = W * (1 - .03 * nx * nx), jx = glitch && rnd(y * .01 + Math.floor(T * 60)) > .7 ? (rnd(y + T) - .5) * 60 : 0;
        ctx.drawImage(comp, 0, y, W, 6, (W - w) / 2 + jx, y, w, 6); }
      ctx.restore();
      if (k < .98) { ctx.fillStyle = `rgba(220,255,230,${(1 - k) * .9})`; ctx.fillRect(W * .1 * (1 - k), H / 2 - 3, W - W * .2 * (1 - k), 6); }
      const v = ctx.createRadialGradient(960, 540, 560, 960, 540, 1150); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,.72)'); ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
      const gl = ctx.createLinearGradient(0, 0, W * .6, H); gl.addColorStop(0, 'rgba(255,255,255,.05)'); gl.addColorStop(.35, 'rgba(255,255,255,0)'); ctx.fillStyle = gl; ctx.fillRect(0, 0, W, H);
      ctx.beginPath(); ctx.rect(0, 0, W, H); ctx.roundRect(20, 20, W - 40, H - 40, 70); ctx.fillStyle = C.bezel; ctx.fill('evenodd');
    } };
  LOOKS.crt = LOOK;
  return { C, BW, BH, b, tx, typed, cursor, pad, statusBar, bigType, bar, glow, monitor, LOOK };
})();
