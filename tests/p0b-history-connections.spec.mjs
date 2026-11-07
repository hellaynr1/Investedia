import assert from 'node:assert/strict';
import fs from 'node:fs';
import {launch,base,fixtureExternal,viewport} from './browser-support.mjs';
const out=process.env.P0B_EVIDENCE_DIR||'/tmp/p0b-results';fs.mkdirSync(out,{recursive:true});
const b=await launch(),results={devices:{},checks:[]};
const check=(name,pass,data)=>{results.checks.push({name,pass,data});assert.ok(pass,name+': '+JSON.stringify(data));};
async function shot(p,name){await p.evaluate(label=>{const e=document.createElement('div');e.id='capture-label';e.textContent=label;e.style.cssText='position:fixed;top:64px;left:12px;z-index:999999;background:#ff7a1a;color:#111;padding:6px;font:700 12px sans-serif';document.body.append(e);},name);await p.screenshot({path:out+'/'+name+'.png'});await p.locator('#capture-label').evaluate(e=>e.remove());}
try{for(const w of [1440,390]){
const c=await b.newContext({viewport:viewport(w),hasTouch:w===390,isMobile:w===390,serviceWorkers:'block'});await fixtureExternal(c);await c.addInitScript(()=>{const N=Date;window.Date=class extends N{constructor(...a){super(...(a.length?a:['2026-11-07T03:00:00Z']));}static now(){return N.parse('2026-11-07T03:00:00Z');}};const raf=requestAnimationFrame;window._frameTimes=[];window._costs=[];window.requestAnimationFrame=fn=>raf.call(window,t=>{let s=performance.now();fn(t);if(fn.name==='frame'){window._frameTimes.push(t);window._costs.push(performance.now()-s);}});});
const p=await c.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(base+'/assets/globe/news.html',{waitUntil:'domcontentloaded'});await p.waitForFunction(()=>stories.length>0&&CONN);await p.locator('[data-consent=essential]').click({timeout:2500}).catch(()=>{});
await p.evaluate(()=>Promise.all([setWin('7d'),setWin('30d')]));check('A7 overlapping windows do not duplicate articles '+w,await p.evaluate(()=>new Set(stories.map(s=>s.id)).size===stories.length));await p.evaluate(()=>setWin('48h'));
const counts={};for(const win of ['24h','48h','30d','7d','48h','24h']){
await p.evaluate(w=>setWin(w),win);await p.waitForTimeout(450);
const actual=await p.evaluate(()=>({win:F.win,shown:shown.length,events:events.length,hist:events.filter(e=>e.historical).length,available:CONN_HIST.length,drawn:arcHits.filter(h=>h.historical).length,visibleEndpoints:arcHits.filter(h=>h.historical).every(h=>[h.points[0],h.points.at(-1)].every(p=>p[2]&&p[0]>=globeBox.left&&p[0]<=globeBox.right&&p[1]>=globeBox.top&&p[1]<=globeBox.bottom)),ids:events.filter(e=>e.historical).map(e=>({id:e.conn.id,event:e.article.id,day:e.conn.day})),sourceIds:shown.map(s=>s.id)}));
check('A7 no unloaded source '+w+' '+win,actual.ids.every(x=>actual.sourceIds.includes(x.event)),actual.ids.length);
if(['24h','48h'].includes(win)){check('A4 no historical lines in '+w+' '+win,actual.hist===0,actual);if(counts[win])check('A4 live count restored '+w+' '+win,counts[win].events===actual.events,{before:counts[win].events,after:actual.events});else counts[win]=actual;}
else{check('A3 historical connections loaded '+w+' '+win,actual.hist>0,actual.hist);const expected=await p.evaluate(()=>{const byId=new Map(shown.map(a=>[a.id,a]));const seen=new Set();let n=0;for(const conn of [...CONN.connections,...CONN_HIST].sort((a,b)=>b.score-a.score || String(a.published_at).localeCompare(String(b.published_at)))){const a=byId.get(conn.event);if(!a)continue;const k=geoKey(a)+'>'+geoKey({phi:conn.dest.lat*rad,lam:conn.dest.lon*rad});if(seen.has(k))continue;seen.add(k);if(conn.day)n++;}return n;});check('A3 eligible deduplicated count '+w+' '+win,actual.hist===expected,{actual:actual.hist,expected});counts[win]=actual;}
if(win==='30d'){check('A3 history included in rendered budget '+w,actual.drawn>0,actual.drawn);check('A3 rendered endpoints visible '+w,actual.visibleEndpoints);}if(win==='30d'||win==='48h')await shot(p,'New-'+w+'-'+win);
}
await p.evaluate(()=>{$('play').click();});await p.waitForFunction(()=>play!==null);await p.waitForTimeout(2500);check('A5 replay filters by time '+w,await p.evaluate(()=>!!play&&events.every(e=>e.article.t<=play.cur)));await p.evaluate(()=>setWin('48h'));
check('A5 no exceptions '+w,errors.length===0,errors);results.devices[w]={counts,errors};await c.close();
}}finally{fs.writeFileSync(out+'/results.json',JSON.stringify(results,null,2));await b.close();console.log(results.checks.filter(c=>c.pass).length+' passing checks');}
