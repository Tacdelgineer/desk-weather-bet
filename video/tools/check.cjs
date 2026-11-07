// node tools/check.cjs chapters/NN_name.html -> page errors (cues not found, exceptions) + shot list with lengths
const { chromium } = require('playwright'); const path = require('path');
(async () => { const b = await chromium.launch(); const p = await b.newPage(); const errs = [];
  p.on('pageerror', e => errs.push('pageerror ' + e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + path.resolve(process.argv[2]) + '?clean'); await p.waitForFunction(() => window.READY, null, { timeout: 15000 }).catch(() => errs.push('not READY'));
  const d = JSON.parse(await p.evaluate(() => pageData()));
  for (let t = 0; t < d.DUR; t += .5) await p.evaluate(t => seek(t), t).catch(e => errs.push('draw@' + t + ' ' + e.message));
  console.log(JSON.stringify({ DUR: d.DUR, errs: [...new Set(errs)].slice(0, 12), shots: d.SPANS.map(s => `${s.t0.toFixed(1)}-${s.t1.toFixed(1)} ${s.name}`) }, null, 1));
  await b.close(); })();
