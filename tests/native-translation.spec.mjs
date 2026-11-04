import assert from 'node:assert/strict';
import fs from 'node:fs';
import {launch,base,widths,viewport} from './browser-support.mjs';
const browser=await launch();
try{for(const width of widths){
 const context=await browser.newContext({viewport:viewport(width),isMobile:width===390,hasTouch:width===390,serviceWorkers:'block',reducedMotion:'reduce'});
 await context.addInitScript(()=>{for(const k of ['inv-auth-seen','inv-pop','inv-app-x'])localStorage.setItem(k,'1');});
 const external=[];await context.route('https://**/*',route=>{if(new URL(route.request().url()).origin===new URL(base).origin)return route.continue();external.push(route.request().url());return route.abort();});
 const page=await context.newPage();page.setDefaultTimeout(10000);
 const english='Investing should be clear, not complicated.';
 await page.goto(base+'/about.html',{waitUntil:'domcontentloaded'});await page.locator('[data-consent=essential]').click();
 // A1: native French, normal DOM, no Google script/widget/toolbar or outbound translation requests.
 await page.locator('.ftr-lang .csel-btn')[width===390?'tap':'click']();await page.getByRole('option',{name:'Français',exact:true})[width===390?'tap':'click']();
 await page.waitForFunction(()=>InvLocale.language==='fr');
 assert.notEqual(await page.locator('h1').first().innerText(),english);assert.equal(await page.locator('html').getAttribute('lang'),'fr');
 assert.equal(await page.locator('iframe[src*="translate"],script[src*="translate.google"],.goog-te-banner-frame,.goog-te-gadget,#inv-google-translate').count(),0);
 assert(!external.some(u=>/translate\.google|translate-pa\.google|translate\.goog/.test(u)));
 assert.equal(await page.locator('.brand b').first().innerText(),'Investedia');
 // A2: actual pack strings apply to dynamically inserted articles; code and prices are untouched.
 const pack=JSON.parse(fs.readFileSync('assets/locales/fr.json'));const headline=Object.keys(pack.strings).find(s=>s.length>70&&!s.includes('<')&&pack.strings[s]!==s);assert(headline);
 await page.evaluate(source=>{const section=document.createElement('section');section.id='locale-dynamic';const b=document.createElement('button');b.textContent=source;b.onclick=()=>b.dataset.clicked='yes';section.append(b);const code=document.createElement('code');code.textContent=source;section.append(code);const price=document.createElement('span');price.id='price-test';price.textContent='$1,234.56';section.append(price);document.querySelector('main').append(section);},headline);
 await page.waitForFunction(expected=>document.querySelector('#locale-dynamic button').textContent===expected,pack.strings[headline]);
 assert.equal(await page.locator('#locale-dynamic code').innerText(),headline);assert.equal(await page.locator('#price-test').innerText(),'$1,234.56');await page.locator('#locale-dynamic button').click();assert.equal(await page.locator('#locale-dynamic button').getAttribute('data-clicked'),'yes');
 // A3: page reload remembers the requested language, and English reverses translations without reloading.
 await page.reload({waitUntil:'domcontentloaded'});await page.waitForFunction(()=>InvLocale.language==='fr');
 const loaded=page.url();await page.evaluate(()=>InvLocale.setLanguage('en'));assert.equal(page.url(),loaded);assert.equal(await page.locator('h1').first().innerText(),english);assert.equal(await page.locator('html').getAttribute('lang'),'en');
 // A4: repeated switches and updated text nodes do not corrupt source strings or duplicate markup.
 await page.evaluate(()=>InvLocale.setLanguage('fr'));await page.evaluate(()=>InvLocale.setLanguage('en'));assert.equal(await page.locator('h1').first().innerText(),english);assert.equal(await page.locator('.ftr-lang').count(),1);
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false,'No horizontal page overflow');
 // A5: every offered language has a complete pack for the published source catalogue.
 const sources=JSON.parse(fs.readFileSync('assets/locales/source.json'));
 for(const lang of ['fr','nl','de','es','it','pt']){const p=JSON.parse(fs.readFileSync(`assets/locales/${lang}.json`));assert.equal(p.language,lang);assert(sources.every(s=>typeof p.strings[s]==='string'&&p.strings[s].length>0),lang+' pack incomplete');}
 // A6: a failed pack fetch preserves the current language and never navigates away.
 await context.route('**/locales/de.json',r=>r.fulfill({status:503,body:'unavailable'}));
 await page.locator('.ftr-lang .csel-btn').click();await page.getByRole('option',{name:'Deutsch',exact:true}).click();await page.locator('.ftr-translate-status').filter({hasText:'unavailable'}).waitFor();assert.equal(await page.locator('h1').first().innerText(),english);assert.equal(page.url(),loaded);
 if(process.env.TEST_SCREENSHOT_DIR){await context.unroute('**/locales/de.json');await page.evaluate(()=>InvLocale.setLanguage('fr'));await page.locator('h1').first().scrollIntoViewIfNeeded();await page.evaluate(w=>{const b=document.createElement('div');b.setAttribute('data-i18n-skip','');b.textContent=`New · ${w===390?'Phone':'PC'} · Native French`;Object.assign(b.style,{position:'fixed',top:'8px',left:'8px',background:'#ff7a1a',color:'#111',padding:'10px',font:'bold 13px sans-serif',zIndex:99999});document.body.append(b)},width);fs.mkdirSync(process.env.TEST_SCREENSHOT_DIR,{recursive:true});await page.screenshot({path:`${process.env.TEST_SCREENSHOT_DIR}/native-${width}.png`});}
 console.log(width+': A1–A6 PASS using actual first-party packs');await context.close();
}}finally{await browser.close();}
