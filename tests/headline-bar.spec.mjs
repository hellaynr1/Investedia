// Owner pick (2026-10-26): option A "Headline bar" replaces the scrolling strip under the homepage globe.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {launch,base,viewport,widths,fixtureExternal} from './browser-support.mjs';
const stories=JSON.parse(fs.readFileSync('assets/globe/news-live.json')).stories, byNew=[...stories].sort((a,b)=>Date.parse(b.published_at)-Date.parse(a.published_at));
const b=await launch(), results=[];
const check=async(width,id,fn)=>{try{await fn();results.push({width,id,pass:true});}catch(e){results.push({width,id,pass:false,error:e.message.split('\n')[0]});}};
const head=p=>p.locator('.hn-hbh').innerText();
const open=async(w,opts={})=>{const phone=w===390,ctx=await b.newContext({viewport:viewport(w),isMobile:phone,hasTouch:phone,serviceWorkers:'block',reducedMotion:opts.reduce?'reduce':'no-preference'});await fixtureExternal(ctx);await ctx.addInitScript(()=>{for(const k of ['inv-auth-seen','inv-pop','inv-app-x'])localStorage.setItem(k,'1');});const p=await ctx.newPage();await p.goto(base+'/index.html');try{await p.getByRole('button',{name:'Accept essential',exact:true}).click({timeout:2500});}catch{}await p.waitForSelector('.hn-hbh');return {ctx,p};};
for(const w of widths){
 const phone=w===390; const {ctx,p}=await open(w);
 await check(w,'H1 labelled region with a tag, flag, headline link, source and time',async()=>{assert.equal(await p.locator('#hnTick').getAttribute('aria-label'),'Latest articles');assert.match(await p.locator('.hn-hbtag').innerText(),/^(Breaking|Latest|Trending|Market moving)$/i);assert.match(await p.locator('.hn-hbh').getAttribute('href'),/news\.html\?story=/);assert.match(await p.locator('.hn-hbs').innerText(),/ · /);});
 await check(w,'H2 starts with the newest article',async()=>assert.equal(await head(p),byNew[0].headline));
 await check(w,'H3 six dots, the active one follows the article',async()=>{assert.equal(await p.locator('.hn-hbd i').count(),6);assert.equal(await p.locator('.hn-hbd i.on').count(),1);});
 await check(w,'H4 the bar sits under the globe copy and search box, inside the hero, without overflow',async()=>{const r=await p.evaluate(()=>{const t=document.querySelector('.hn-hbc').getBoundingClientRect(),s=document.querySelector('.hn-search').getBoundingClientRect();return {tt:t.top,sb:s.bottom,w:t.width,ov:document.documentElement.scrollWidth>innerWidth};});assert(r.tt>=r.sb-1,'below search');assert.equal(r.ov,false);});
 if(!phone){
  await check(w,'H5 arrows step through articles and wrap; dots follow',async()=>{const first=await head(p);await p.locator('[data-hb="1"]').click();assert.equal(await head(p),byNew[1].headline);assert.equal(await p.locator('.hn-hbd i').nth(1).getAttribute('class'),'on');await p.locator('[data-hb="-1"]').click();assert.equal(await head(p),first);await p.locator('[data-hb="-1"]').click();assert.equal(await head(p),byNew[5].headline);await p.locator('[data-hb="1"]').click();});
  await check(w,'H6 changes by itself after about 6 seconds',async()=>{await p.mouse.move(5,5);await p.evaluate(()=>document.activeElement&&document.activeElement.blur());await p.waitForTimeout(300);const a=await head(p);await p.waitForTimeout(6800);assert.notEqual(await head(p),a);});
  await check(w,'H7 Pause stops it (aria-pressed) and Play restarts it; the change is announced when paused',async()=>{const pb=p.locator('.hn-hbp');await pb.click();assert.equal(await pb.getAttribute('aria-pressed'),'true');const a=await head(p);await p.waitForTimeout(6800);assert.equal(await head(p),a);await p.locator('[data-hb="1"]').click();assert.match(await p.locator('.hn-hbl').innerText(),/:/);await pb.click();assert.equal(await pb.getAttribute('aria-pressed'),'false');});
  await check(w,'H8 hovering the bar pauses it',async()=>{await p.locator('.hn-hbc').hover();const a=await head(p);await p.waitForTimeout(6800);assert.equal(await head(p),a);});
 } else {
  await check(w,'H5 phone: arrows are hidden, pause button is at least 44px',async()=>{assert.equal(await p.locator('.hn-hbn').isVisible(),false);const r=await p.locator('.hn-hbp').boundingBox();assert(r.width>=44&&r.height>=44,JSON.stringify(r));});
  await check(w,'H6 phone: swiping left shows the next article, right goes back',async()=>{const a=await head(p);const sw=async(x0,x1)=>p.evaluate(({x0,x1})=>{const el=document.querySelector('.hn-hbc'),mk=x=>new Touch({identifier:1,target:el,clientX:x,clientY:300});el.dispatchEvent(new TouchEvent('touchstart',{touches:[mk(x0)],bubbles:true}));el.dispatchEvent(new TouchEvent('touchend',{changedTouches:[mk(x1)],bubbles:true}));},{x0,x1});await sw(300,100);assert.equal(await head(p),byNew[1].headline);await sw(100,300);assert.equal(await head(p),a);});
 }
 await ctx.close();
}
// reduced motion: starts paused and never changes by itself
for(const w of widths){const {ctx,p}=await open(w,{reduce:true});await check(w,'H9 reduced motion: starts paused and stays on the same article',async()=>{assert.equal(await p.locator('.hn-hbp').getAttribute('aria-pressed'),'true');const a=await head(p);await p.waitForTimeout(6800);assert.equal(await head(p),a);});await ctx.close();}
await b.close();
fs.writeFileSync('tests/headline-bar-results.json',JSON.stringify(results,null,1));
for(const r of results)if(!r.pass)console.log('FAIL',r.width,r.id,r.error);
console.log(`${results.filter(r=>r.pass).length}/${results.length} passed`);
process.exit(results.some(r=>!r.pass)?1:0);
