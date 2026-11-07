// node preview/still_vertical.cjs <out.png> [seconds]  -> the 1080x1920 frame of preview/vertical.html
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => { const [out, t] = process.argv.slice(2); const b = await chromium.launch(); const p = await b.newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => m.type() === 'error' && errs.push(m.text()));
  await p.goto('file://' + path.resolve(__dirname, 'vertical.html')); await p.waitForFunction(() => window.READY, null, { timeout: 15000 });
  const url = await p.evaluate(t => { seekV(+t); return document.getElementById('c').toDataURL('image/png'); }, t || 8);
  fs.writeFileSync(out, Buffer.from(url.split(',')[1], 'base64')); await b.close(); console.log(errs.length ? 'errors: ' + errs.join(' | ') : 'ok', out); })();
