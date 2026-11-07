import assert from 'node:assert/strict';
import fs from 'node:fs';
import {launch,base,fixtureExternal,viewport} from './browser-support.mjs';
const out=process.env.P11_EVIDENCE_DIR||'/tmp/p11-evidence';fs.mkdirSync(out,{recursive:true});
const results=[];const browser=await launch();
const check=(name,pass)=>{results.push({name,pass});assert.ok(pass,name);};
async function shot(p,name){await p.evaluate(text=>{const e=document.createElement('div');e.id='test-label';e.textContent=text;e.style.cssText='position:fixed;top:60px;left:12px;z-index:999999;background:#ff7a1a;color:#111;padding:6px;font:700 12px sans-serif';document.body.append(e);},'Built · '+name);await p.screenshot({path:`${out}/${name}.png`});await p.locator('#test-label').evaluate(e=>e.remove());}
try{for(const width of [390,1440]){
const c=await browser.newContext({viewport:viewport(width),hasTouch:width===390,isMobile:width===390,serviceWorkers:'block'});await fixtureExternal(c);await c.addInitScript(()=>{localStorage.setItem('inv-consent',JSON.stringify({essential:true,analytics:false}));localStorage.setItem('inv-auth-seen','1');});
const p=await c.newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(base+'/assets/globe/news.html');await p.locator('[data-consent=essential]').click({timeout:3000}).catch(()=>{});await p.waitForFunction(()=>typeof stories!=='undefined'&&stories.length>0);await p.waitForTimeout(800);
if(width===390){
await p.locator('[data-v=news]').click();check('first News tap leaves globe',await p.evaluate(()=>phoneView==='news'&&sheetState==='closed'&&!MARKET.on));await shot(p,'phone-news-globe');
await p.locator('[data-v=news]').click();check('second News tap opens sheet',await p.evaluate(()=>sheetState!=='closed'));await shot(p,'phone-news-sheet');
await p.locator('[data-panel-tab=latest]').click();await p.locator('#sheet-close').click();await p.locator('[data-v=news]').click();check('News tab survives close',await p.evaluate(()=>panelTab==='latest'));await p.keyboard.press('Escape');check('Escape dismisses phone sheet',await p.evaluate(()=>sheetState==='closed'));
await p.locator('[data-v=markets]').click();check('Markets mode with dock',await p.evaluate(()=>MARKET.on&&sheetState==='closed')&&await p.locator('#dock').isVisible());await p.locator('[data-v=markets]').click();check('Markets second tap opens sheet',await p.evaluate(()=>sheetState!=='closed'));await shot(p,'phone-markets-sheet');
await p.locator('#sheet-close').click();const h=await p.locator('#nav-grab').boundingBox();await p.mouse.move(h.x+h.width/2,h.y+h.height/2);await p.mouse.down();await p.mouse.move(h.x+h.width/2,h.y-80,{steps:6});await p.mouse.up();check('upward handle opens',await p.evaluate(()=>sheetState!=='closed'));
const grab=await p.locator('#grab').boundingBox();await p.mouse.move(grab.x+grab.width/2,grab.y+8);await p.mouse.down();await p.mouse.move(grab.x+grab.width/2,820,{steps:12});await p.mouse.up();check('downward handle dismisses',await p.evaluate(()=>sheetState==='closed'));
await p.locator('[data-v=globe]').click();check('Globe restores plain news globe',await p.evaluate(()=>phoneView==='globe'&&!MARKET.on&&sheetState==='closed'));check('grab hidden for Globe',await p.locator('#nav-grab').isHidden());
}else{
await p.locator('#sheet-close').click();check('desktop close',await p.locator('#panel').isHidden());await p.evaluate(()=>openCountry(byName.Nigeria));await p.keyboard.press('Escape');check('desktop Escape',await p.locator('#panel').isHidden());
}
await p.evaluate(()=>{marketSetMode('markets');marketSelect('Nigeria');MARKET.tab='sectors';marketRender();});await p.locator('.market-close').click();await p.evaluate(()=>marketSelect('Nigeria'));check('market state preserved '+width,await p.evaluate(()=>MARKET.tab==='sectors'));const tabs=await p.locator('.market-tabs').evaluate(e=>getComputedStyle(e).gap);check('momentum gap '+width,tabs==='8px');await p.keyboard.press('Escape');check('market Escape '+width,await p.locator('.market-panel').isHidden());
check('no exceptions '+width,errors.length===0);await p.goto(base+'/index.html');await p.waitForTimeout(700);check('no caption '+width,await p.locator('.hn-map-caption').count()===0);
if(width===390)check('no phone switch',await p.locator('.hn-mode-row').isHidden());else{const box=await p.locator('.hn-modes').boundingBox();check('slim desktop switch',box.height===34);await shot(p,'desktop-switch');}
await c.close();
}}finally{fs.writeFileSync(out+'/results.json',JSON.stringify(results,null,2));await browser.close();console.log(results.filter(x=>x.pass).length+' assertions passed');}
