import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import fs from 'fs'; import { execSync } from 'child_process';
const dir = new URL('./', import.meta.url).pathname, keys = process.argv.slice(2);
const b = await chromium.launch({ executablePath:'/opt/pw-browsers/chromium' });
const p = await b.newPage({ viewport:{ width:1080, height:1920 } });
for (const k of keys) {
  await p.goto('file://' + dir + 'kit.html#' + k); await p.reload(); await p.waitForLoadState('networkidle'); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(300);
  const T = await p.evaluate(k=>DUR[k], k), N = Math.ceil(T * 60), fd = `/tmp/claude-0/-home-user/170e9188-4963-5685-bb7e-199c7760b034/scratchpad/fr_${k}/`;
  fs.rmSync(fd, { recursive: true, force: true }); fs.mkdirSync(fd, { recursive: true });
  for (let f = 0; f < N; f++) { await p.evaluate(([k, t]) => ANIM[k](t), [k, f / 60]); await p.screenshot({ path: `${fd}${String(f).padStart(4, '0')}.jpg`, type: 'jpeg', quality: 93, clip:{x:0,y:0,width:1080,height:1920} }); }
  fs.mkdirSync(dir + 'out', { recursive: true });
  execSync(`ffmpeg -y -loglevel error -framerate 60 -i ${fd}%04d.jpg -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -movflags +faststart ${dir}out/${k}.mp4`);
  console.log('video', k, T + 's');
}
await b.close();
