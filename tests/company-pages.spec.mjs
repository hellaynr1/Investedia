import {launch,base,viewport,fixtureExternal} from './browser-support.mjs';
import assert from 'node:assert/strict';
const b=await launch();let fail=0;
const t=async(n,f)=>{try{await f();}catch(e){fail++;console.log('FAIL',n,e.message.slice(0,300));}};
for(const w of [1440,390]){
  const c=await b.newContext({viewport:viewport(w),isMobile:w===390,hasTouch:w===390,serviceWorkers:'block'});await fixtureExternal(c);
  await c.addInitScript(()=>{for(const k of ['inv-auth-seen','inv-pop','inv-app-x'])localStorage.setItem(k,'1');});
  const open=async(u)=>{const p=await c.newPage();await p.goto(base+'/'+u);try{await p.getByRole('button',{name:'Accept essential',exact:true}).click({timeout:1500});}catch{}await p.waitForSelector('.cp');return p;};
  for(const [u,h,m] of [['jobs.html',/Build with us/,/^mailto:jobs@investedia\.com/],['partnerships.html',/Work with Investedia/,/^mailto:partners@investedia\.com/]]){
    const p=await open(u);
    await t(w+' '+u+' title, one clear button, no overflow',async()=>{assert.match(await p.locator('h1').innerText(),h);const a=p.locator('.cp-btn');assert.equal(await a.count(),1);assert.match(await a.getAttribute('href'),m);assert.ok((await a.boundingBox()).height>=44);assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));});
    await p.close();}
  let p=await open('feedback.html');
  await t(w+' feedback: empty submit asks for input',async()=>{await p.locator('#fb-go').click();assert.match(await p.locator('#fb-out').innerText(),/Add a message/);});
  await t(w+' feedback: bad email is refused',async()=>{await p.fill('#fb-msg','Hello');await p.fill('#fb-mail','nope');await p.locator('#fb-go').click();assert.match(await p.locator('#fb-out').innerText(),/email address/);});
  await t(w+' feedback: taps and topic buttons toggle, 44px targets',async()=>{await p.locator('[data-mood=good]').click();assert.equal(await p.locator('[data-mood=good]').getAttribute('aria-pressed'),'true');await p.locator('[data-cat=Bug]').click();assert.equal(await p.locator('[data-cat=Idea]').getAttribute('aria-pressed'),'false');assert.ok((await p.locator('[data-cat=Bug]').boundingBox()).height>=44);});
  let sent=null;await c.route('**/rest/v1/feedback',r=>{sent=JSON.parse(r.request().postData());r.fulfill({status:201,body:''});});
  await t(w+' feedback: a valid message is posted with the right fields and a thank-you shows',async()=>{await p.fill('#fb-mail','a@b.co');await p.locator('#fb-go').click();await p.waitForFunction(()=>/Thank you/.test(document.getElementById('fb-out').textContent));assert.equal(sent.category,'Bug');assert.equal(sent.mood,'good');assert.equal(sent.message,'Hello');assert.equal(sent.email,'a@b.co');});
  await t(w+' feedback: the spam trap sends nothing',async()=>{sent=null;await p.evaluate(()=>{localStorage.removeItem('inv-fb-last')});await p.fill('#fb-msg','spam');await p.evaluate(()=>{document.querySelector('[name=website]').value='x'});await p.locator('#fb-go').click();await p.waitForTimeout(400);assert.equal(sent,null);});
  await p.close();
  p=await open('feedback.html');await c.unroute('**/rest/v1/feedback');await c.route('**/rest/v1/feedback',r=>r.fulfill({status:404,body:'{}'}));
  await t(w+' feedback: if saving fails, the page says so and falls back to email',async()=>{await p.fill('#fb-msg','Please add dark mode');const nav=p.waitForEvent('framenavigated',{timeout:3000}).catch(()=>null);await p.locator('#fb-go').click();await p.waitForFunction(()=>/could not send/.test(document.getElementById('fb-out').textContent));});
  await t(w+' feedback: no horizontal overflow',async()=>assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)));
  await p.close();await c.close();}
await b.close();console.log(fail?fail+' failed':'all passed');process.exit(fail?1:0);
