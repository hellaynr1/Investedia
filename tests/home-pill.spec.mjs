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
    await t('P1 PC shows the headline pill with side arrows, not the scrolling strip or a dropdown',async()=>{assert.ok(await p.locator('#hnPillA').isVisible());assert.ok(await p.locator('#hnPrev').isVisible()&&await p.locator('#hnNext').isVisible());assert.equal(await p.locator('.hn-tick').isVisible(),false);assert.equal(await p.locator('#hnPillList').count(),0);});
    await t('P2 the pill shows the headline and its summary sentence, stays one size and clear of Open globe',async()=>{const a=await p.locator('.hn-pillbox').boundingBox(),o=await p.locator('.hn-open').boundingBox();assert.ok(a.width<=620&&a.height<=80);assert.ok(o.y+o.height<=a.y-8);assert.ok((await p.locator('#hnPillS').innerText()).length>10);});
    await t('P3 the right side moves to the next headline, the left goes back, it wraps, arrows are 44px, keys work',async()=>{
      const h=()=>p.locator('#hnPillH').innerText();const h0=await h();assert.equal(await p.locator('#hnPillN').innerText(),'1 / 6');
      for(const b of ['#hnPrev','#hnNext'])assert.ok((await p.locator(b).boundingBox()).width>=44);
      await p.locator('#hnNext').click();assert.notEqual(await h(),h0);assert.equal(await p.locator('#hnPillN').innerText(),'2 / 6');
      await p.locator('#hnPrev').click();assert.equal(await h(),h0);await p.locator('#hnPrev').click();assert.equal(await p.locator('#hnPillN').innerText(),'6 / 6');
      await p.locator('#hnNext').focus();await p.keyboard.press('ArrowRight');assert.equal(await p.locator('#hnPillN').innerText(),'1 / 6');});
    await t('P3b the headline links to the article',async()=>{assert.match(await p.locator('#hnPillA').getAttribute('href'),/story=/);});
  } else {
    await t('P4 phone keeps the existing strip, no pill',async()=>{assert.equal(await p.locator('#hnPillA').isVisible(),false);assert.ok(await p.locator('.hn-tick').isVisible());});
  }
  await t('P5 no horizontal overflow',async()=>assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)));
  await c.close();}
await b.close();console.log(fail?fail+' failed':'all passed');process.exit(fail?1:0);
