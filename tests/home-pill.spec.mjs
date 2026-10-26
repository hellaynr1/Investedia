import {launch,base,viewport,fixtureExternal} from './browser-support.mjs';
import assert from 'node:assert/strict';
const b=await launch();let fail=0;
for(const w of [1440,390]){
  const c=await b.newContext({viewport:viewport(w),isMobile:w===390,hasTouch:w===390,serviceWorkers:'block'});await fixtureExternal(c);
  await c.addInitScript(()=>{for(const k of ['inv-auth-seen','inv-pop','inv-app-x'])localStorage.setItem(k,'1');});
  const p=await c.newPage();await p.goto(base+'/index.html');
  try{await p.getByRole('button',{name:'Accept essential',exact:true}).click({timeout:2500});}catch{}
  await p.waitForTimeout(2500);
  const t=async(n,f)=>{try{await f();}catch(e){fail++;console.log('FAIL',w,n,e.message.slice(0,300));}};
  if(w===1440){
    await t('P1 PC shows the slim pill, not the scrolling strip',async()=>{assert.ok(await p.locator('#hnPillBtn').isVisible());assert.equal(await p.locator('.hn-tick').isVisible(),false);});
    await t('P2 the pill is one line, 46px tall, and clear of the Open globe button',async()=>{const a=await p.locator('#hnPillBtn').boundingBox(),o=await p.locator('.hn-open').boundingBox();assert.ok(Math.abs(a.height-46)<2);assert.ok(o.y+o.height<=a.y-8);});
    await t('P3 tapping opens 6 headlines upward, Escape closes and returns focus',async()=>{await p.locator('#hnPillBtn').click();assert.equal(await p.locator('#hnPillList li').count(),6);assert.equal(await p.locator('#hnPillBtn').getAttribute('aria-expanded'),'true');const l=await p.locator('#hnPillList').boundingBox(),a=await p.locator('#hnPillBtn').boundingBox();assert.ok(l.y+l.height<=a.y);await p.keyboard.press('Escape');assert.equal(await p.locator('#hnPillList').isVisible(),false);assert.equal(await p.evaluate(()=>document.activeElement.id),'hnPillBtn');});
  } else {
    await t('P4 phone keeps the existing strip, no pill',async()=>{assert.equal(await p.locator('#hnPillBtn').isVisible(),false);assert.ok(await p.locator('.hn-tick').isVisible());});
  }
  await t('P5 no horizontal overflow',async()=>assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)));
  await c.close();}
await b.close();console.log(fail?fail+' failed':'all passed');process.exit(fail?1:0);
