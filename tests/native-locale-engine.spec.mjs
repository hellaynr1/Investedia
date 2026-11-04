// Unit-level DOM fixture: the full native-translation suite separately checks actual generated site packs.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {launch,base,widths,viewport} from './browser-support.mjs';
const browser=await launch();
try{for(const width of widths){const c=await browser.newContext({viewport:viewport(width),serviceWorkers:'block'});
await c.route('**/locale-engine.html',r=>r.fulfill({contentType:'text/html',body:'<!doctype html><html lang="en"><head><script src="/assets/locale.js"></script></head><body><h1>Invest with clarity.</h1><button id="control">Markets</button><input id="input" placeholder="Markets" value="Private user text"><p class="brand">Markets</p><p id="amount">$1,234.56</p><div id="dynamic"></div></body></html>'}));
await c.route('**/locales/fr.json',r=>r.fulfill({contentType:'application/json',body:JSON.stringify({language:'fr',strings:{'Invest with clarity.':'Investissez en toute clarté.','Markets':'Marchés','New article':'Nouvel article'}})}));
await c.route('**/locales/de.json',r=>r.fulfill({status:503,body:'unavailable'}));
const p=await c.newPage();await p.goto(base+'/locale-engine.html');await p.locator('#control').evaluate(e=>e.onclick=()=>e.dataset.clicked='yes');
await p.evaluate(()=>InvLocale.setLanguage('fr'));assert.equal(await p.locator('h1').innerText(),'Investissez en toute clarté.');assert.equal(await p.locator('input').getAttribute('placeholder'),'Marchés');assert.equal(await p.locator('input').inputValue(),'Private user text');assert.equal(await p.locator('.brand').innerText(),'Markets');assert.equal(await p.locator('#amount').innerText(),'$1,234.56');await p.locator('#control').click();assert.equal(await p.locator('#control').getAttribute('data-clicked'),'yes');
await p.evaluate(()=>document.querySelector('#dynamic').textContent='New article');await p.waitForFunction(()=>document.querySelector('#dynamic').textContent==='Nouvel article');
await p.evaluate(()=>InvLocale.setLanguage('en'));assert.equal(await p.locator('#dynamic').innerText(),'New article');assert.equal(await p.locator('h1').innerText(),'Invest with clarity.');
await p.evaluate(()=>InvLocale.setLanguage('fr'));await p.reload();await p.waitForFunction(()=>InvLocale.language==='fr');assert.equal(await p.locator('h1').innerText(),'Investissez en toute clarté.');
assert.equal(await p.evaluate(()=>InvLocale.setLanguage('de').then(()=>false,()=>true)),true);assert.equal(await p.locator('html').getAttribute('lang'),'fr');assert.equal(await p.locator('h1').innerText(),'Investissez en toute clarté.');
await p.evaluate(()=>{document.querySelector('#dynamic').textContent='Markets';});await p.waitForFunction(()=>document.querySelector('#dynamic').textContent==='Marchés');
await p.evaluate(()=>InvLocale.setLanguage('en'));assert.equal(await p.locator('#dynamic').innerText(),'Markets');console.log(width+': native locale engine PASS');await c.close();}}finally{await browser.close();}
