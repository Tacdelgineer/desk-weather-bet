// node tools/sheet.cjs <page.html> <sheet.png> t1 t2 ...  -> one contact sheet, 3 columns x 640 px, time + shot under each,
// plus any page errors and cue errors. Wide copy of tacdel-shorts tools/sheet.cjs (that one scales to 270 px).
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const { execFileSync } = require('child_process');
(async () => {
  const [file, out, ...ts] = process.argv.slice(2); const tmp = fs.mkdtempSync(path.join(require('os').tmpdir(), 'sheet-'));
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1000, height: 700 } }); const errs = [];
  p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + path.resolve(file) + '?clean'); await p.waitForFunction(() => window.READY, null, { timeout: 15000 });
  const frames = [];
  for (const t of ts) { const [url, name] = await p.evaluate(t => { seek(+t); return [document.getElementById('c').toDataURL('image/png'), SHOTS[shotAt(warp(+t))].name]; }, t);
    const f = path.join(tmp, `f_${t}.png`); fs.writeFileSync(f, Buffer.from(url.split(',')[1], 'base64')); frames.push([f, `${t}s  ${name}`.replace(/[:']/g, ' ')]); }
  await b.close();
  const cols = 3, inputs = frames.flatMap(([f]) => ['-i', f]);
  const lab = frames.map(([, l], i) => `[${i}]scale=640:-1,pad=640:396:0:0:black,drawtext=text='${l}':x=8:y=366:fontsize=20:fontcolor=white[v${i}]`).join(';');
  while (frames.length % cols) { inputs.push('-f', 'lavfi', '-i', 'color=black:s=640x396:d=1'); frames.push([null, '']); }
  const n = frames.length, real = ts.length, rows = n / cols;
  const pads = frames.slice(real).map((_, j) => `[${real + j}]null[v${real + j}]`).join(';');
  const layout = Array.from({ length: n }, (_, i) => `${(i % cols) * 640}_${Math.floor(i / cols) * 396}`).join('|');
  const filt = lab + (pads ? ';' + pads : '') + ';' + frames.map((_, i) => `[v${i}]`).join('') + `xstack=inputs=${n}:layout=${layout}`;
  execFileSync('ffmpeg', ['-v', 'error', '-y', ...inputs, '-filter_complex', n > 1 ? filt : lab.replace(`[v0]`, ''), '-frames:v', '1', out]);
  console.log(errs.length ? 'page errors:\n' + [...new Set(errs)].join('\n') : 'no page errors', '->', out);
})();
