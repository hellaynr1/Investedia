import assert from 'node:assert/strict';
import fs from 'node:fs';
import {launch,base,viewport,widths} from './browser-support.mjs';
const browser=await launch();
for(const width of widths){
 const context=await browser.newContext({viewport:viewport(width),serviceWorkers:'block'}), page=await context.newPage();
 await page.goto(base+'/index.html');await page.getByRole('button',{name:'Accept essential',exact:true}).click();
 await page.waitForTimeout(600);
 assert.equal(await page.locator('.hn-search:visible').count(),1,'one home search');
 assert.equal(await page.getByText('Which markets are open',{exact:false}).count(),0);
 assert.equal(await page.locator('.hn-ent code').count(),0);
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'home overflow');
 await page.evaluate(()=>InvPeek.search());await page.waitForTimeout(900);
 assert.equal(await page.locator('.pk-in input').getAttribute('placeholder'),'Search assets, countries & articles');
 assert.equal(await page.getByRole('button',{name:'Pages',exact:true}).count(),0);
 for(const filter of ['stocks','crypto','idx','cmd','fx','countries','articles']){await page.locator(`[data-f=${filter}]`).click();assert(await page.locator('.pk-r .pk-i').count()>=10,filter);assert(!/No result/.test(await page.locator('.pk-r').innerText()));}
 assert(await page.evaluate(()=>{const c=getComputedStyle(document.querySelector('.pk-sb'));return Number(c.backgroundColor.match(/[\d.]+/g).at(-1))<=.5 && getComputedStyle(document.querySelector('.pk')).backdropFilter!=='none';}));
 await page.keyboard.press('Escape');await page.waitForTimeout(250);await page.locator('#notif-btn').click();assert(await page.locator('.notif-source').count()>0);await page.locator('#notif-read').click();assert.equal(await page.locator('.notif-item.unread').count(),0);
 const data=JSON.parse(fs.readFileSync('assets/calendar-live.json'));
 await page.goto(base+'/calendar.html?date=custom&from=2026-01-01&to=2026-12-31&type=economic&impact=2&region=USD');await page.waitForTimeout(500);
 const expected=data.events.filter(e=>e.imp===2&&e.c==='USD'&&e.at.startsWith('2026')).length;assert.equal(await page.locator('tr[data-impact]').count(),expected);
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'calendar overflow');
 await page.goto(base+'/assets/globe/news.html');await page.waitForTimeout(1600);assert(Number(await page.locator('#cv').getAttribute('data-arc-count'))>0);
 await context.close();console.log(`${width}: batch 2 checks passed`);
}await browser.close();
