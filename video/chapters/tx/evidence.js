/* evidence.js · the EVIDENCE look (project style, CLAUDE.md "Video pipeline"): a real document on warm paper, an
   animated yellow highlighter across one line or cell, a small source label in a corner, paper texture.
   Explainer-channel technique only; no channel's logo or branding. All EVIDENCE colours live here. */
const EV = (() => {
  const C = { paper: '#e8dfcc', sheet: '#fbf8f1', ink: '#1d1a16', dim: 'rgba(29,26,22,.55)', hi: '#ffe347', card: '#17130f', cardInk: '#f2eadd', red: '#c23a22' };
  const TEX = (() => { const g = document.createElement('canvas'); g.width = 960; g.height = 540; const x = g.getContext('2d'), im = x.createImageData(960, 540);
    for (let i = 0; i < im.data.length; i += 4) { const v = 90 + Math.random() * 120; im.data[i] = v; im.data[i + 1] = v * .95; im.data[i + 2] = v * .85; im.data[i + 3] = Math.random() < .5 ? 22 : 0; }
    x.putImageData(im, 0, 0); x.strokeStyle = 'rgba(120,100,70,.10)'; x.lineWidth = .7;
    for (let k = 0; k < 260; k++) { const a = Math.random() * 960, b = Math.random() * 540, r = Math.random() * 7; x.beginPath(); x.moveTo(a, b); x.quadraticCurveTo(a + r * 3, b + r, a + r * 6, b - r); x.stroke(); }
    return g; })();
  // a document sheet: drop shadow, slight tilt; fn draws in sheet coordinates
  function sheet(x, y, w, h, ang, fn) { ctx.save(); ctx.translate(x + w / 2, y + h / 2); ctx.rotate(ang); ctx.translate(-w / 2, -h / 2);
    ctx.shadowColor = 'rgba(40,30,15,.35)'; ctx.shadowBlur = 28; ctx.shadowOffsetY = 10; ctx.fillStyle = C.sheet; ctx.fillRect(0, 0, w, h); ctx.shadowColor = 'transparent';
    fn(); ctx.restore(); }
  // highlighter stroke across [x, x+w] at baseline y (size = text size), progress p
  function hilite(x, y, w, size, p) { if (p <= 0) return; ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = C.hi; ctx.globalAlpha = .9;
    const ww = (w + size * .6) * eo(p), x0 = x - size * .3, top = y - size * .95, hh = size * 1.25;
    ctx.beginPath(); ctx.moveTo(x0, top + 3); ctx.lineTo(x0 + ww, top); ctx.lineTo(x0 + ww - 3, top + hh); ctx.lineTo(x0 + 2, top + hh + 2); ctx.closePath(); ctx.fill(); ctx.restore(); }
  function source(s, x, y, align = 'left') { ctx.save(); ctx.font = `600 18px ${FONT.mono}`; ctx.textAlign = align; ctx.textBaseline = 'alphabetic';
    const w = ctx.measureText(s).width + 20, x0 = align === 'right' ? x - w : x; ctx.fillStyle = 'rgba(29,26,22,.82)'; ctx.fillRect(x0, y - 22, w, 30);
    ctx.fillStyle = C.sheet; ctx.fillText(s, align === 'right' ? x - 10 : x + 10, y); ctx.restore(); }
  function text(s, x, y, size, col = C.ink, wt = 500, font = FONT.mono, align = 'left') { ctx.font = `${wt} ${size}px ${font}`; ctx.fillStyle = col; ctx.textAlign = align; ctx.textBaseline = 'alphabetic'; ctx.fillText(s, x, y); }
  LOOKS.evidence = { dim: C.dim,
    begin(lt) { ctx.fillStyle = C.paper; ctx.fillRect(0, 0, W, H); ctx.globalAlpha = eo(lt / .2); },
    end() { ctx.globalAlpha = 1; ctx.drawImage(TEX, 0, 0, W, H); const g = ctx.createRadialGradient(960, 540, 650, 960, 540, 1200);
      g.addColorStop(0, 'rgba(60,40,20,0)'); g.addColorStop(1, 'rgba(60,40,20,.28)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); } };
  return { C, sheet, hilite, source, text };
})();
