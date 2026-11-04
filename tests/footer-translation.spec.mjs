import assert from 'node:assert/strict';
import fs from 'node:fs';
import {launch,base,widths,viewport} from './browser-support.mjs';

const browser=await launch();
const shots=process.env.TEST_SCREENSHOT_DIR;
if(shots)fs.mkdirSync(shots,{recursive:true});
try {
  for(const width of widths){
    const context=await browser.newContext({viewport:viewport(width),isMobile:width===390,hasTouch:width===390,serviceWorkers:'block',reducedMotion:'reduce'});
    await context.addInitScript(()=>{for(const key of ['inv-auth-seen','inv-pop','inv-app-x'])localStorage.setItem(key,'1');});
    await context.route('**/*',route=>new URL(route.request().url()).origin===new URL(base).origin?route.continue():route.abort());
    // Capture only the handoff. This fixture does not pretend to provide translated content.
    await context.route('https://translate.google.com/translate?**',route=>route.fulfill({contentType:'text/html',body:'<title>Translation handoff test fixture</title>'}));
    const page=await context.newPage();page.setDefaultTimeout(8000);
    async function open(url){
      await page.goto(url,{waitUntil:'domcontentloaded'});
      if(await page.locator('#inv-consent-panel:visible').count())await page.locator('[data-consent=essential]').click();
    }
    async function choose(label){
      const button=page.locator('.ftr-lang .csel-btn');
      await button[width===390?'tap':'click']();
      const option=page.getByRole('option',{name:label,exact:true});
      assert(await option.isVisible());
      await option[width===390?'tap':'click']();
    }
    // A1: selecting any supported language actually navigates through Google's normal entry point.
    for(const [code,label] of Object.entries({fr:'Français',nl:'Nederlands',de:'Deutsch',es:'Español',it:'Italiano',pt:'Português'})){
      await open(base+'/about.html?source=footer&search=oil%20%26%20gas#team');
      await choose(label);await page.waitForURL('https://translate.google.com/translate?**');
      const handoff=new URL(page.url());assert.equal(handoff.searchParams.get('sl'),'en');assert.equal(handoff.searchParams.get('tl'),code);assert.equal(handoff.searchParams.get('hl'),code);
      const original=new URL(handoff.searchParams.get('u'));
      assert.equal(original.hostname,'investedia.com');assert.equal(original.pathname,'/about.html');assert.equal(original.searchParams.get('source'),'footer');assert.equal(original.searchParams.get('search'),'oil & gas');assert.equal(original.hash,'#team');
    }
    // Serve actual local application files at the proxy origin to exercise existing translated-page behavior.
    await context.route('https://investedia-com.translate.goog/**',async route=>{
      const url=new URL(route.request().url()),response=await fetch(base+url.pathname+url.search);
      await route.fulfill({status:response.status,contentType:response.headers.get('content-type')||'text/plain',body:Buffer.from(await response.arrayBuffer())});
    });
    const translated='https://investedia-com.translate.goog/about.html?source=footer&_x_tr_sl=en&_x_tr_tl=fr&_x_tr_hl=fr&_x_tr_hist=true#team';
    // A2: the selector reflects the active language; another language translates the original, without nesting proxies.
    await open(translated);assert.equal(await page.locator('.ftr-lang select').inputValue(),'fr');
    await choose('Deutsch');await page.waitForURL('https://translate.google.com/translate?**');
    let handoff=new URL(page.url());assert.equal(handoff.searchParams.get('tl'),'de');assert.equal(handoff.searchParams.get('u'),'https://investedia.com/about.html?source=footer#team');
    // A3: English returns directly to the original page and removes every Google proxy parameter.
    await context.route('https://investedia.com/**',route=>route.fulfill({contentType:'text/html',body:'<title>English handoff test fixture</title>'}));
    await open(translated);await choose('English');await page.waitForURL('https://investedia.com/**');assert.equal(page.url(),'https://investedia.com/about.html?source=footer#team');
    // A4: the existing desktop popover / phone sheet remains visible and keyboard-accessible.
    await open(base+'/about.html');
    const control=page.locator('.ftr-lang .csel-btn');await control.focus();await page.keyboard.press('Enter');
    assert.equal(await page.getByRole('option').count(),7);assert(await page.getByRole('option',{name:'Français',exact:true}).isVisible());
    if(shots){
      await page.evaluate(w=>{const badge=document.createElement('div');badge.textContent=`New · ${w===390?'Phone 390':'PC 1440'} · Translation control`;Object.assign(badge.style,{position:'fixed',top:'8px',left:'8px',padding:'10px 14px',background:'#ff7a1a',color:'#111',font:'bold 14px sans-serif',zIndex:999999});document.body.append(badge);},width);
      await page.screenshot({path:`${shots}/translation-${width}.png`});
    }
    await page.keyboard.press('Escape');assert.equal(await control.getAttribute('aria-expanded'),'false');assert(await control.evaluate(e=>e===document.activeElement));
    console.log(`${width}: A1–A4 PASS (navigation fixtures; live translation not tested)`);
    await context.close();
  }
} finally {await browser.close();}
