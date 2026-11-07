// 8.3 · Playwright captures of public pages: a 1920x1080 screenshot (for EVIDENCE shots, with the highlight phrase's
// box) and a slow-scroll recording (for footage). Public pages only, no logins.
//   NODE_PATH=~/ai-dev-skills/node_modules node video/rec/capture_pages.cjs [name ...]
// Writes results/evidence/web/<name>.png + <name>.json and video/work/rec/<name>.webm. Safe to re-run.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const ROOT = path.resolve(__dirname, '../..'), OUT = path.join(ROOT, 'results/evidence/web'), REC = path.join(ROOT, 'video/work/rec');
const PAGES = require('./pages.json');
// names to blur live in blur.local.json (gitignored), so the repo never holds them
const BLUR = fs.existsSync(path.join(__dirname, 'blur.local.json')) ? require('./blur.local.json') : {};
PAGES.forEach(p => { p.blur = BLUR[p.name] || []; if (p.blur_local && !p.blur.length) throw new Error(p.name + ': blur.local.json missing'); });
(async () => {
  fs.mkdirSync(OUT, { recursive: true }); fs.mkdirSync(REC, { recursive: true });
  const want = process.argv.slice(2), b = await chromium.launch();
  for (const P of PAGES.filter(p => !want.length || want.includes(p.name))) {
    const ctx = await b.newContext({ viewport: { width: 1920, height: 1080 }, recordVideo: { dir: REC, size: { width: 1920, height: 1080 } },
      userAgent: 'Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36', locale: 'en-US' });
    const pg = await ctx.newPage(); let ok = true;
    try { await pg.goto(P.url, { waitUntil: 'domcontentloaded', timeout: 45000 }); await pg.waitForTimeout(P.wait || 5000); }
    catch (e) { ok = false; console.log(P.name, 'load failed', e.message.split('\n')[0]); }
    if (ok) {
      await pg.keyboard.press('Escape').catch(() => {}); await pg.waitForTimeout(400);
      // hide cookie banners / overlays by selector, blur what must not show (e.g. a seller's name)
      await pg.evaluate(({ hide, blur }) => {
        for (const s of hide || []) document.querySelectorAll(s).forEach(e => e.style.setProperty('display', 'none', 'important'));
        const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        const hits = []; while (walk.nextNode()) { const n = walk.currentNode; if ((blur || []).some(t => n.textContent.includes(t))) hits.push(n.parentElement); }
        hits.forEach(e => e.style.setProperty('filter', 'blur(9px)', 'important'));
        (blur || []).length && document.querySelectorAll('img').forEach(i => { const a = (i.alt || '') + ' ' + (i.src || ''); if ((blur || []).some(t => a.toLowerCase().includes(t.toLowerCase())) || /avatar|profile|user/i.test(a)) i.style.setProperty('filter', 'blur(14px)', 'important'); });
      }, P);
      // scroll the phrase into view, then measure its box
      const rect = await pg.evaluate((phrase) => {
        if (!phrase) return null; const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        while (walk.nextNode()) { const n = walk.currentNode, i = n.textContent.indexOf(phrase); if (i < 0) continue;
          n.parentElement.scrollIntoView({ block: 'center' }); const r = document.createRange(); r.setStart(n, i); r.setEnd(n, i + phrase.length);
          const rs = [...r.getClientRects()].map(q => [q.x, q.y, q.width, q.height]); return rs; }
        return null; }, P.phrase || null);
      await pg.waitForTimeout(800);
      const rect2 = P.phrase ? await pg.evaluate((phrase) => { const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        while (walk.nextNode()) { const n = walk.currentNode, i = n.textContent.indexOf(phrase); if (i < 0) continue;
          const r = document.createRange(); r.setStart(n, i); r.setEnd(n, i + phrase.length); return [...r.getClientRects()].map(q => [q.x, q.y, q.width, q.height]); } return null; }, P.phrase) : null;
      await pg.screenshot({ path: path.join(OUT, P.name + '.png') });
      fs.writeFileSync(path.join(OUT, P.name + '.json'), JSON.stringify({ name: P.name, url: P.url, label: P.label, captured_utc: new Date().toISOString(),
        title: await pg.title(), phrase: P.phrase || null, rects: rect2, blurred_items: (P.blur || []).length, found: !!rect }, null, 1));
      // slow scroll for the footage recording
      await pg.evaluate(() => window.scrollTo(0, 0)); await pg.waitForTimeout(1200);
      for (let k = 0; k < (P.scrollSteps ?? 30); k++) { await pg.mouse.wheel(0, P.scrollPx || 25); await pg.waitForTimeout(100); }
      await pg.waitForTimeout(800);
      console.log(P.name, 'ok', rect2 ? 'phrase found' : (P.phrase ? 'PHRASE NOT FOUND' : ''), await pg.title());
    }
    const v = pg.video(); await ctx.close(); if (v) { const f = await v.path(); if (P.blur_local) fs.unlinkSync(f); else fs.renameSync(f, path.join(REC, P.name + '.webm')); }   // a blurred page's recording would show the name before the blur lands
  }
  await b.close();
})();
