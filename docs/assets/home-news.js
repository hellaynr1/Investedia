// News-first homepage: live news (assets/globe/news-live.json) rendered as cards, rows and "why it moved" explainers.
const BF = '1idNJqyfpKbma454ae4';
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const NAME = { 'United States of America': 'United States', 'Dem. Rep. Congo': 'DR Congo', 'Bosnia and Herz.': 'Bosnia and Herzegovina', 'Dominican Rep.': 'Dominican Republic' };
const nm = c => NAME[c] || c;
const CAT = { markets: 'Markets', companies: 'Companies', economy: 'Economy', technology: 'Technology', crypto: 'Crypto', commodities: 'Commodities', geopolitics: 'Geopolitics' };
const FLAG = { breaking: 'Breaking', trending: 'Trending', moving: 'Market moving' };
let ISO = {}, ENTITY_LOGOS = {};
function ago(t) { const m = Math.round((Date.parse(t)-Date.now())/60000), r = new Intl.RelativeTimeFormat(undefined,{numeric:'auto'}); return Math.abs(m)<60 ? r.format(m,'minute') : Math.abs(m)<1440 ? r.format(Math.round(m/60),'hour') : r.format(Math.round(m/1440),'day'); }
const flagSrc = c => ISO[c] ? `assets/globe/flags/${ISO[c].toLowerCase()}.svg` : '';
const company = e => e.ticker && !/[\^=]/.test(e.ticker) && !/-USD$/.test(e.ticker);
const localLogo = e => ENTITY_LOGOS[e.sym] || ENTITY_LOGOS[e.ticker] || 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="8" fill="#f4f4f5"/><text x="32" y="39" text-anchor="middle" font-family="sans-serif" font-size="24" fill="#18181b">' + esc((e.name || e.ticker || 'I').slice(0,2).toUpperCase()) + '</text></svg>');
const logoSrc = e => !window.InvConsent?.allows('images') ? localLogo(e) : company(e) ? `https://cdn.brandfetch.io/ticker/${encodeURIComponent(e.ticker)}/w/256/h/256/fallback/404?c=${BF}` : '';
const url = s => `assets/globe/news.html?story=${encodeURIComponent(s.id)}`;
const tags = s => `${s.flag ? `<span class="hn-tag">${FLAG[s.flag]}</span>` : ''}<span class="hn-eyebrow">${esc(CAT[s.category] || '')} · ${esc(s.location.place.split(',')[0])}</span>`;
const hideBad = `onerror="this.remove()"`;
function entityImage(e, country) {
  const asset = /[\^=]/.test(e.ticker || '') || ['index', 'currency', 'future'].includes(e.type);
  if (asset) { const f = flagSrc(country); return f ? `<img src="${f}" alt="" ${hideBad}>` : ''; }
  const local = ENTITY_LOGOS[e.sym] || ENTITY_LOGOS[e.ticker];
  const remote = !window.InvConsent?.allows('images') ? '' : company(e) ? logoSrc(e) : /-USD$/.test(e.ticker || '') ? `https://cdn.brandfetch.io/crypto/${encodeURIComponent(e.ticker.split('-')[0])}/w/256/h/256/fallback/404?c=${BF}` : '';
  const src = local?.endsWith('.svg') ? local : remote || local;
  if (!src) return '';
  const fb = remote && local && src !== local ? ` data-fb="${esc(local)}"` : '';
  return `<img src="${esc(src)}" alt=""${fb} onerror="if(this.dataset.fb){this.src=this.dataset.fb;delete this.dataset.fb}else{this.remove()}" loading="lazy">`;
}


function img(s) {
  const e = (s.entities || []).find(company), f = flagSrc(s.location.country);
  if (s.image) return `<div class="hn-img"><img class="hn-ph" src="assets/globe/${esc(s.image.file)}" alt="${esc(s.image.alt || '')}" loading="lazy"><span class="hn-il">${s.image.kind === 'place' ? 'Photo' : 'Illustration'} · ${esc(s.image.source || '')}</span>${e ? `<img class="hn-lg" src="${logoSrc(e)}" alt="" ${hideBad}>` : ''}${f ? `<img class="hn-fl" src="${f}" alt="">` : ''}</div>`;
  if (e) return `<div class="hn-img"><img class="hn-big" src="${logoSrc(e)}" alt="${esc(e.name)}" style="background:rgba(255,255,255,.07);border-radius:16px;padding:10px" ${hideBad}>${f ? `<img class="hn-fl" src="${f}" alt="">` : ''}</div>`;
  return `<div class="hn-img">${f ? `<img class="hn-bigfl" src="${f}" alt="${esc(nm(s.location.country))}">` : ''}</div>`;
}
const card = (s, sum = true) => `<a class="hn-card" href="${url(s)}">${img(s)}<div>${tags(s)}</div><h3>${esc(s.headline)}</h3>${sum ? `<p>${esc(s.summary)}</p>` : ''}<span class="hn-meta">${ago(s.published_at)} · <b>${esc(s.source?.name || '')}</b>${s.sources?.length > 1 ? ` + ${s.sources.length - 1} more` : ''}</span></a>`;
function thumb(s) {
  const e = (s.entities || []).find(company), f = flagSrc(s.location.country);
  return s.image ? `<img src="assets/globe/${esc(s.image.file)}" alt="${esc(s.image.alt || 'Topic photograph')}"><span class="hn-thumb-label">Illustration</span>` : e ? `<img class="hn-lgo" src="${logoSrc(e)}" alt="" ${hideBad}>` : f ? `<img class="hn-flg" src="${f}" alt="">` : '';
}
const row = s => `<a class="hn-row hn-news-card" href="${url(s)}"><span class="hn-source">${esc((s.source?.name || 'N').slice(0,2).toUpperCase())}</span><span><h4>${esc(s.headline)}</h4>${impactChips(s)}<span class="hn-meta">${esc(s.source?.name || '')} · ${ago(s.published_at)}</span></span></a>`;
function impactChips(s) {
  const rows = (Array.isArray(s.impacts) ? s.impacts : []).filter(i => i && typeof i.name === 'string' && ['up', 'down', 'mixed', 'unclear'].includes(i.direction) && Object.values(ISO).includes(i.country)).slice(0, 2);
  const arrow = { up: '↑', down: '↓', mixed: '↔', unclear: '↔' };
  return rows.length ? `<div class="hn-ents hn-impacts" aria-label="AI-assisted analysis">${rows.map(i => `<span class="hn-ent"><img src="assets/globe/flags/${i.country.toLowerCase()}.svg" alt="" ${hideBad}><span class="hn-impact-${i.direction}">${arrow[i.direction]}</span>${esc(i.name)}</span>`).join('')}</div>` : '';
}
// "Why it moved": real price moves next to what the article implies. Numbers come from assets/globe/markets.json only.
let MARKETS = [];
const mkOf = i => i && MARKETS.find(a => a.s === i.ticker || a.site === i.ticker);
const primary = s => { for (const i of Array.isArray(s.impacts) ? s.impacts : []) { const a = mkOf(i); if (a && Number.isFinite(a.d)) return { a, i }; } return null; };
const pctPill = v => `<span class="hn-pct ${v > 0 ? 'up' : v < 0 ? 'down' : 'flat'}">${v > 0 ? '↑' : v < 0 ? '↓' : '↔'} ${Math.abs(v).toFixed(2)}%</span>`;
const IMPLIES = { up: '↑ up', down: '↓ down', mixed: '↔ mixed', unclear: 'unclear' };
const implies = i => `<span class="hn-impl">Article implies ${IMPLIES[i.direction] || 'unclear'}</span>`;
const sign = v => (v > 0 ? '+' : '') + v.toFixed(2) + '%';
function spark(a, mark, up) {
  const sp = a.sp || []; if (sp.length < 2) return '';
  const mn = Math.min(...sp), mx = Math.max(...sp), X = k => k / (sp.length - 1) * 420, Y = v => 92 - (v - mn) / ((mx - mn) || 1) * 84;
  const d = sp.map((v, k) => `${k ? 'L' : 'M'}${X(k).toFixed(1)} ${Y(v).toFixed(1)}`).join(''), c = up ? '#34d399' : '#f87171';
  return `<div class="hn-chart" aria-hidden="true"><svg viewBox="0 0 420 96" preserveAspectRatio="none"><path d="${d}L420 96L0 96Z" fill="${c}" opacity=".12"/><path d="${d}" fill="none" stroke="${c}" stroke-width="2" vector-effect="non-scaling-stroke" stroke-linejoin="round"/></svg><i class="hn-mark" style="left:${(X(mark) / 4.2).toFixed(1)}%"></i><b class="hn-dot" style="left:${(X(mark) / 4.2).toFixed(1)}%;top:${(Y(sp[mark]) / 96 * 100).toFixed(1)}%"></b></div>`;
}
const markIndex = (s, a, asof) => { const days = Math.max(0, (Date.parse(asof) - Date.parse(s.published_at)) / 864e5); return Math.max(0, Math.min(a.sp.length - 1, a.sp.length - 1 - Math.round(days * 5 / 7))); };
const whyFeatured = (s, asof) => { const m = primary(s), t = s.why_moved || s.summary;
  const body = m ? `<div class="hn-wrow"><div class="hn-wbig"><span class="hn-wl">${esc(m.a.n)} · today</span><strong class="${m.a.d > 0 ? 'up' : m.a.d < 0 ? 'down' : 'flat'}">${m.a.d > 0 ? '↑' : m.a.d < 0 ? '↓' : '↔'} ${Math.abs(m.a.d).toFixed(2)}%</strong><span class="hn-wl">7 days ${sign(m.a.w)}</span></div><div class="hn-wchart">${spark(m.a, markIndex(s, m.a, asof), m.a.w >= 0)}<div class="hn-wcap"><span>22 sessions ago</span><span class="hn-wmk">● article published</span><span>now</span></div></div></div>` : '';
  return `<a class="hn-wf" href="${url(s)}"><div class="hn-wtop">${tags(s)}${m ? implies(m.i) : ''}</div><h3>${esc(s.headline)}</h3><p>${esc(t)}</p>${body}${impactChips(s)}</a>`; };
const whySmall = s => { const m = primary(s); return `<a class="hn-wc" href="${url(s)}"><div class="hn-wtop">${tags(s)}</div><h4>${esc(s.headline)}</h4>${m ? `<div class="hn-wasset"><b>${esc(m.a.n)}</b>${pctPill(m.a.d)}${implies(m.i)}</div>` : impactChips(s)}</a>`; };
const whySection = (list, asof) => list.length ? whyFeatured(list[0], asof) + `<div class="hn-wside">${list.slice(1, 3).map(whySmall).join('')}</div>` : '';
// Headline bar under the globe: one article at a time (Breaking/Latest tag, flag, headline, source and time).
// Auto-advances every 6 s; pauses on hover, focus and when hidden; a Pause button, arrows (wide) and swipe (phone) let people control it.
function headlineBar(el, list) {
  const items = list.slice(0, 6); if (!items.length) { el.innerHTML = ''; return; }
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let i = 0, timer = 0, paused = reduce, hover = false;
  el.setAttribute('role', 'region'); el.setAttribute('aria-roledescription', 'carousel'); el.setAttribute('aria-label', 'Latest articles');
  el.innerHTML = '<div class="hn-hbc"><span class="hn-hbtag"></span><img class="hn-hbf" alt="" hidden><a class="hn-hbh"></a><span class="hn-hbs"></span><span class="hn-hbn"><button type="button" class="hn-hbb" data-hb="-1" aria-label="Previous article">‹</button><button type="button" class="hn-hbb" data-hb="1" aria-label="Next article">›</button></span><span class="hn-hbd" aria-hidden="true"></span><button type="button" class="hn-hbp" aria-label="Pause automatic changes"></button></div><span class="hn-hbl" aria-live="off"></span>';
  const q = c => el.querySelector(c), live = q('.hn-hbl'), pbtn = q('.hn-hbp'), body = q('.hn-hbc');
  const show = (k, announce) => {
    i = (k + items.length) % items.length; const s = items[i], f = flagSrc(s.location.country), tag = FLAG[s.flag] || 'Latest';
    q('.hn-hbtag').textContent = tag; q('.hn-hbtag').dataset.t = s.flag || 'latest';
    const img = q('.hn-hbf'); img.hidden = !f; if (f) img.src = f;
    const h = q('.hn-hbh'); h.href = url(s); h.textContent = s.headline;
    q('.hn-hbs').textContent = (s.source?.name || '') + ' · ' + ago(s.published_at);
    q('.hn-hbd').innerHTML = items.map((_, n) => `<i class="${n === i ? 'on' : ''}"></i>`).join('');
    el.dataset.index = i; if (announce) live.textContent = `${tag}: ${s.headline}`;
  };
  const tick = () => { clearTimeout(timer); if (!paused && !hover && !document.hidden) timer = setTimeout(() => { show(i + 1); tick(); }, 6000); };
  const setPaused = v => { paused = v; pbtn.textContent = v ? '▶' : '❚❚'; pbtn.setAttribute('aria-label', v ? 'Play automatic changes' : 'Pause automatic changes'); pbtn.setAttribute('aria-pressed', String(v)); live.setAttribute('aria-live', v ? 'polite' : 'off'); tick(); };
  el.addEventListener('click', e => { const b = e.target.closest('[data-hb]'); if (b) { show(i + Number(b.dataset.hb), true); tick(); } });
  pbtn.onclick = () => setPaused(!paused);
  body.addEventListener('mouseenter', () => { hover = true; clearTimeout(timer); }); body.addEventListener('mouseleave', () => { hover = false; tick(); });
  el.addEventListener('focusin', () => { hover = true; clearTimeout(timer); }); el.addEventListener('focusout', () => { hover = false; tick(); });
  document.addEventListener('visibilitychange', tick);
  let x0 = null; body.addEventListener('touchstart', e => { x0 = e.touches[0].clientX; }, { passive: true });
  body.addEventListener('touchend', e => { if (x0 == null) return; const dx = e.changedTouches[0].clientX - x0; x0 = null; if (Math.abs(dx) > 40) { show(i + (dx < 0 ? 1 : -1), true); tick(); } }, { passive: true });
  show(0); setPaused(reduce);
}
function countries(list) {
  const c = {}; for (const s of list) c[s.location.country] = (c[s.location.country] || 0) + 1;
  return Object.entries(c).sort((a, b) => b[1] - a[1]).slice(0, 14).map(([k, n]) => `<a class="hn-cty" href="assets/globe/news.html?country=${encodeURIComponent(k)}">${flagSrc(k) ? `<img src="${flagSrc(k)}" alt="">` : ''}<span><b>${esc(nm(k))}</b><small>${n} ${n === 1 ? 'article' : 'articles'}</small></span></a>`).join('');
}
// rank: importance, then sources, then recency
const rank = (a, b) => (b.importance - a.importance) || ((b.sources?.length || 1) - (a.sources?.length || 1)) || (Date.parse(b.published_at) - Date.parse(a.published_at));
async function loadNews() {
  const [n, iso, logos, mk] = await Promise.all([fetch('assets/globe/news-live.json', { cache: 'no-cache' }).then(r => r.json()), fetch('assets/globe/iso.json').then(r => r.json()).catch(() => ({})), fetch('assets/globe/logos.json').then(r => r.json()).catch(() => ({})), fetch('assets/globe/markets.json').then(r => r.json()).catch(() => ({ assets: [] }))]);
  MARKETS = mk.assets || [];
  ISO = iso; ENTITY_LOGOS = Object.fromEntries(Object.entries(logos).map(([k, v]) => [k, v.replace('../logos/', 'assets/logos/')])); const stories = n.stories || [];
  return { stories, top: [...stories].sort(rank), latest: [...stories].sort((a, b) => Date.parse(b.published_at) - Date.parse(a.published_at)), updated: n.updated_at,
    moved: (() => { const all = [...stories].filter(s => s.market_moving || s.importance === 3).sort(rank), seen = new Set(), out = []; for (const s of all) { const m = primary(s); if (m && !seen.has(m.a.s)) { seen.add(m.a.s); out.push(s); } } for (const s of all) if (!out.includes(s) && !primary(s)) out.push(s); return out; })(), asof: mk.asof };
}
const updatedText = t => 'Live · updated ' + new Date(t).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
