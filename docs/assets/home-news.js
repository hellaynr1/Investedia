// News-first homepage: live news (assets/globe/news-live.json) rendered as cards, rows and "why it moved" explainers.
const BF = '1idNJqyfpKbma454ae4';
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const NAME = { 'United States of America': 'United States', 'Dem. Rep. Congo': 'DR Congo', 'Bosnia and Herz.': 'Bosnia and Herzegovina', 'Dominican Rep.': 'Dominican Republic' };
const nm = c => NAME[c] || c;
const CAT = { markets: 'Markets', companies: 'Companies', economy: 'Economy', technology: 'Technology', crypto: 'Crypto', commodities: 'Commodities', geopolitics: 'Geopolitics' };
const FLAG = { breaking: 'Breaking', trending: 'Trending', moving: 'Market moving' };
let ISO = {}, ENTITY_LOGOS = {};
function ago(t) { const m = Math.max(1, Math.round((Date.now() - Date.parse(t)) / 60000)); return m < 60 ? m + ' min ago' : m < 1440 ? Math.round(m / 60) + ' h ago' : Math.round(m / 1440) + ' d ago'; }
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
const row = s => `<a class="hn-row" href="${url(s)}"><span class="hn-th">${thumb(s)}</span><span><span>${tags(s)}</span><h4>${esc(s.headline)}</h4><span class="hn-meta">${ago(s.published_at)} · ${esc(nm(s.location.country))}</span></span></a>`;
function impactChips(s) {
  const rows = (Array.isArray(s.impacts) ? s.impacts : []).filter(i => i && typeof i.name === 'string' && ['up', 'down', 'mixed', 'unclear'].includes(i.direction) && Object.values(ISO).includes(i.country)).slice(0, 2);
  const arrow = { up: '↑', down: '↓', mixed: '↔', unclear: '→' };
  return rows.length ? `<div class="hn-ents hn-impacts" aria-label="AI-assisted analysis">${rows.map(i => `<span class="hn-ent"><img src="assets/globe/flags/${i.country.toLowerCase()}.svg" alt="" ${hideBad}><span class="hn-impact-${i.direction}">${arrow[i.direction]}</span>${esc(i.name)}</span>`).join('')}</div>` : '';
}
const why = (s, i) => `<a class="hn-why" href="${url(s)}"><span class="hn-n">0${i + 1}</span><div>${tags(s)}</div><h3>${esc(s.headline)}</h3><div class="hn-wl">What happened</div><p>${esc(s.summary)}</p><div class="hn-wl">Why it matters</div><p>${esc(s.why)}</p>${impactChips(s)}
  ${(s.entities || []).length ? `<div class="hn-ents">${s.entities.map(e => `<span class="hn-ent"${e.ticker ? ` title="${esc(e.ticker)}"` : ''}>${entityImage(e, s.location.country)}<span>${esc(e.name)}</span></span>`).join('')}</div>` : ''}</a>`;
function countries(list) {
  const c = {}; for (const s of list) c[s.location.country] = (c[s.location.country] || 0) + 1;
  return Object.entries(c).sort((a, b) => b[1] - a[1]).slice(0, 14).map(([k, n]) => `<a class="hn-cty" href="assets/globe/news.html?country=${encodeURIComponent(k)}">${flagSrc(k) ? `<img src="${flagSrc(k)}" alt="">` : ''}<span><b>${esc(nm(k))}</b><small>${n} ${n === 1 ? 'article' : 'articles'}</small></span></a>`).join('');
}
// rank: importance, then sources, then recency
const rank = (a, b) => (b.importance - a.importance) || ((b.sources?.length || 1) - (a.sources?.length || 1)) || (Date.parse(b.published_at) - Date.parse(a.published_at));
async function loadNews() {
  const [n, iso, logos] = await Promise.all([fetch('assets/globe/news-live.json', { cache: 'no-cache' }).then(r => r.json()), fetch('assets/globe/iso.json').then(r => r.json()).catch(() => ({})), fetch('assets/globe/logos.json').then(r => r.json()).catch(() => ({}))]);
  ISO = iso; ENTITY_LOGOS = Object.fromEntries(Object.entries(logos).map(([k, v]) => [k, v.replace('../logos/', 'assets/logos/')])); const stories = n.stories || [];
  return { stories, top: [...stories].sort(rank), latest: [...stories].sort((a, b) => Date.parse(b.published_at) - Date.parse(a.published_at)), updated: n.updated_at,
    moved: [...stories].filter(s => s.market_moving || s.importance === 3).sort(rank) };
}
const updatedText = t => 'Live · updated ' + new Date(t).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
