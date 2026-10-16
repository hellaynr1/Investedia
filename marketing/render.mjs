import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import fs from 'fs';
const dir = new URL('./', import.meta.url).pathname, only = process.argv.slice(2);
const b = await chromium.launch({ executablePath:'/opt/pw-browsers/chromium' });
const p = await b.newPage({ viewport:{ width:1080, height:1920 } });
await p.goto('file://' + dir + 'kit.html#p1'); await p.waitForLoadState('networkidle');
const keys = only.length ? only : await p.evaluate(()=>KEYS);
fs.mkdirSync(dir + 'out', { recursive: true });
for (const k of keys) {
  await p.goto('file://' + dir + 'kit.html#' + k); await p.reload(); await p.waitForLoadState('networkidle'); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(250);
  const [w, h] = await p.evaluate(()=>SIZE); await p.setViewportSize({ width:w, height:h });
  await p.screenshot({ path: `${dir}out/${k}.png`, clip:{ x:0, y:0, width:w, height:h } });
}
console.log('rendered', keys.length);
await b.close();
