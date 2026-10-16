import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
const dir = new URL('./', import.meta.url).pathname;
const b = await chromium.launch({ executablePath:'/opt/pw-browsers/chromium' });
const p = await b.newPage({ viewport:{ width:1179, height:2556 } });
await p.goto('file://' + dir + 'profile.html'); await p.waitForLoadState('networkidle'); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(400);
await p.screenshot({ path: dir + 'out/profile_mockup.png' }); await b.close();
