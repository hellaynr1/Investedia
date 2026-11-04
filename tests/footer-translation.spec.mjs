import assert from 'node:assert/strict';
import fs from 'node:fs';
import {launch,base,widths,viewport} from './browser-support.mjs';

const browser=await launch();
const shots=process.env.TEST_SCREENSHOT_DIR;
if(shots)fs.mkdirSync(shots,{recursive:true});
try {
  for(const width of widths){
    const context=await browser.newContext({viewport:viewport(width),isMobile:width===390,hasTouch:width===390,serviceWorkers:'block',reducedMotion:'reduce'});
    await context.route('**/*',route=>new URL(route.request().url()).origin===new URL(base).origin?route.continue():route.abort());
    await context.addInitScript(()=>{for(const key of ['inv-auth-seen','inv-pop','inv-app-x'])localStorage.setItem(key,'1');});
    const page=await context.newPage();page.setDefaultTimeout(8000);
    await page.goto(base+'/about.html?source=footer#team',{waitUntil:'domcontentloaded'});
    await page.locator('[data-consent=essential]').click();
    const control=page.locator('.ftr-lang summary'),menu=page.locator('.ftr-lang-menu');
    await control.scrollIntoViewIfNeeded();
    // A1: clicking the globe, text, or arrow opens a visible language list.
    for(const target of ['svg','.ftr-lang-current',null]){
      if(target)await control.locator(target)[width===390?'tap':'click']();
      else {const box=await control.boundingBox();if(width===390)await page.touchscreen.tap(box.x+box.width-12,box.y+box.height/2);else await page.mouse.click(box.x+box.width-12,box.y+box.height/2);}
      assert(await menu.isVisible());
      assert.equal(await menu.locator('a:visible').count(),7);
      const box=await menu.boundingBox();assert(box.x>=0&&box.y>=0&&box.x+box.width<=width);
      await control.press('Escape');assert(await menu.isHidden());
    }
    // A2: keyboard opening and dismissal restore focus; outside clicks close it.
    await control.focus();await page.keyboard.press('Enter');assert(await menu.isVisible());
    await page.keyboard.press('Tab');assert(await menu.locator('a').first().evaluate(e=>e===document.activeElement));
    await page.keyboard.press('Escape');assert(await menu.isHidden());assert(await control.evaluate(e=>e===document.activeElement));
    await control.click();await page.locator('.ftr-data').click();assert(await menu.isHidden());
    // A3: real translation links keep the page, query, and anchor for every language.
    for(const code of ['en','fr','nl','de','es','it','pt']){
      const url=new URL(await menu.locator(`a[lang="${code}"]`).getAttribute('href'));
      assert.equal(url.hostname,code==='en'?'investedia.com':'investedia-com.translate.goog');
      assert.equal(url.pathname,'/about.html');assert.equal(url.searchParams.get('source'),'footer');assert.equal(url.hash,'#team');
      assert.equal(url.searchParams.get('_x_tr_tl'),code==='en'?null:code);
    }
    // A4: both themes use contrasting menu text and every touch target is >=44px high.
    await control.click();
    for(const theme of ['dark','light']){
      await page.evaluate(t=>document.documentElement.dataset.theme=t,theme);
      const styles=await menu.locator('a[lang="fr"]').evaluate(e=>({fg:getComputedStyle(e).color,bg:getComputedStyle(e.parentElement).backgroundColor,height:e.getBoundingClientRect().height}));
      const luminance=color=>{const rgb=color.match(/[\d.]+/g).slice(0,3).map(v=>{v=Number(v)/255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;});return rgb[0]*.2126+rgb[1]*.7152+rgb[2]*.0722;};
      const fg=luminance(styles.fg),bg=luminance(styles.bg);assert((Math.max(fg,bg)+.05)/(Math.min(fg,bg)+.05)>=4.5);assert(styles.height>=44);
    }
    await page.evaluate(()=>document.documentElement.dataset.theme='dark');
    if(shots){
      await page.evaluate(w=>{const badge=document.createElement('div');badge.textContent=`New · ${w===390?'Phone 390':'PC 1440'} · Translation menu`;Object.assign(badge.style,{position:'fixed',top:'8px',left:'8px',padding:'10px 14px',background:'#ff7a1a',color:'#111',font:'bold 14px sans-serif',zIndex:999999});document.body.append(badge);},width);
      await page.screenshot({path:`${shots}/translation-${width}.png`});
    }
    // A5: a translated page shows its active language and English removes ALL proxy parameters.
    const translated='https://investedia-com.translate.goog/about.html?source=footer&_x_tr_sl=en&_x_tr_tl=fr&_x_tr_hl=fr&_x_tr_hist=true#team';
    await context.route('https://investedia-com.translate.goog/**',async route=>{
      const url=new URL(route.request().url());
      const response=await fetch(base+url.pathname+url.search);
      await route.fulfill({status:response.status,contentType:response.headers.get('content-type')||'text/plain',body:Buffer.from(await response.arrayBuffer())});
    });
    await menu.locator('a[lang="fr"]').click();
    await page.waitForURL('https://investedia-com.translate.goog/**');
    assert.equal(new URL(page.url()).searchParams.get('_x_tr_tl'),'fr');
    await page.goto(translated,{waitUntil:'domcontentloaded'});
    assert.equal(await page.locator('.ftr-lang-current').textContent(),'Français');
    assert.equal(await page.locator('.ftr-lang-menu a[aria-current]').textContent(),'Français');
    const english=new URL(await page.locator('.ftr-lang-menu a[lang="en"]').getAttribute('href'));
    assert.equal(english.href,'https://investedia.com/about.html?source=footer#team');
    console.log(`${width}: A1–A5 PASS`);
    await context.close();
  }
} finally {await browser.close();}
