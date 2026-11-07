// Project copy of tacdel-shorts tools/render.cjs (waits for window.READY).
// node render.cjs <page.html> <out.mp4> <seconds> [voice.mp3 or -] [nocaps]  -> frame-exact 1080x1920 30 fps H.264 (+ AAC voice)
const { chromium } = require('playwright'); const { spawn } = require('child_process'); const path = require('path');
(async () => {
  const [file, out, secs, audio, extra] = process.argv.slice(2); const N = Math.round(+secs * 30);
  const args = ['-v', 'error', '-y', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', '30', '-i', '-'];
  const AU = audio && audio !== '-'; if (AU) args.push('-i', audio);
  args.push('-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', '30');
  if (AU) args.push('-c:a', 'aac', '-b:a', '192k', '-af', 'apad', '-t', String(N / 30));
  args.push('-movflags', '+faststart', out);
  const ff = spawn('ffmpeg', args, { stdio: ['pipe', 'inherit', 'inherit'] });
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 600, height: 1000 } });
  p.on('pageerror', e => console.error('pageerror', e.message));
  await p.goto('file://' + path.resolve(file) + '?clean' + (extra ? '&' + extra : '')); await p.waitForFunction(() => window.READY, null, { timeout: 120000 }); await p.waitForTimeout(500);   // project copy: wait for READY (frames decoded), not a fixed 1.8 s
  for (let k = 0; k < N; k++) {
    const url = await p.evaluate(k => { seek(k / 30); return document.getElementById('c').toDataURL('image/jpeg', .92); }, k);
    if (!ff.stdin.write(Buffer.from(url.slice(23), 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (k % 300 === 0) console.log(`${path.basename(out)} ${k}/${N}`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); console.log('done', out);
})();
