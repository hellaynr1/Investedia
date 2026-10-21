// News-first homepage: live news (assets/globe/news-live.json) rendered as cards, rows and "why it moved" explainers.
const BF = '1idNJqyfpKbma454ae4';
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const NAME = { 'United States of America': 'United States', 'Dem. Rep. Congo': 'DR Congo', 'Bosnia and Herz.': 'Bosnia and Herzegovina', 'Dominican Rep.': 'Dominican Republic' };
const nm = c => NAME[c] || c;
const CAT = { markets: 'Markets', companies: 'Companies', economy: 'Economy', technology: 'Technology', crypto: 'Crypto', commodities: 'Commodities', geopolitics: 'Geopolitics' };
const FLAG = { breaking: 'Breaking', trending: 'Trending', moving: 'Market moving' };
let ISO = {};
function ago(t) { const m = Math.max(1, Math.round((Date.now() - Date.parse(t)) / 60000)); return m < 60 ? m + ' min ago' : m < 1440 ? Math.round(m / 60) + ' h ago' : Math.round(m / 1440) + ' d ago'; }
const flagSrc = c => ISO[c] ? `assets/globe/flags/${ISO[c].toLowerCase()}.svg` : '';
const company = e => e.ticker && !/[\^=]/.test(e.ticker) && !/-USD$/.test(e.ticker);
const logoSrc = e => company(e) ? `https://cdn.brandfetch.io/ticker/${encodeURIComponent(e.ticker)}/w/256/h/256/fallback/404?c=${BF}` : '';
const url = s => `assets/globe/news.html?story=${encodeURIComponent(s.id)}`;
const tags = s => `${s.flag ? `<span class="hn-tag">${FLAG[s.flag]}</span>` : ''}<span class="hn-eyebrow">${esc(CAT[s.category] || '')} · ${esc(s.location.place.split(',')[0])}</span>`;
const hideBad = `onerror="this.remove()"`;

function img(s) {
  const e = (s.entities || []).find(company), f = flagSrc(s.location.country);
  if (s.image) return `<div class="hn-img"><img class="hn-ph" src="assets/globe/${esc(s.image.file)}" alt="${esc(s.image.alt || '')}" loading="lazy"><span class="hn-il">${s.image.kind === 'place' ? 'Photo' : 'Illustration'} · ${esc(s.image.source || '')}</span>${e ? `<img class="hn-lg" src="${logoSrc(e)}" alt="" ${hideBad}>` : ''}${f ? `<img class="hn-fl" src="${f}" alt="">` : ''}</div>`;
  if (e) return `<div class="hn-img"><img class="hn-big" src="${logoSrc(e)}" alt="${esc(e.name)}" style="background:#fff;border-radius:16px;padding:10px" ${hideBad}>${f ? `<img class="hn-fl" src="${f}" alt="">` : ''}</div>`;
  return `<div class="hn-img">${f ? `<img class="hn-bigfl" src="${f}" alt="${esc(nm(s.location.country))}">` : ''}</div>`;
}
const card = (s, sum = true) => `<a class="hn-card" href="${url(s)}">${img(s)}<div>${tags(s)}</div><h3>${esc(s.headline)}</h3>${sum ? `<p>${esc(s.summary)}</p>` : ''}<span class="hn-meta">${ago(s.published_at)} · <b>${esc(s.source?.name || '')}</b>${s.sources?.length > 1 ? ` + ${s.sources.length - 1} more` : ''}</span></a>`;
function thumb(s) {
  const e = (s.entities || []).find(company), f = flagSrc(s.location.country);
  return s.image ? `<img src="assets/globe/${esc(s.image.file)}" alt="">` : e ? `<img class="hn-lgo" src="${logoSrc(e)}" alt="" ${hideBad}>` : f ? `<img class="hn-flg" src="${f}" alt="">` : '';
}
const row = s => `<a class="hn-row" href="${url(s)}"><span class="hn-th">${thumb(s)}</span><span><span>${tags(s)}</span><h4>${esc(s.headline)}</h4><span class="hn-meta">${ago(s.published_at)} · ${esc(nm(s.location.country))}</span></span></a>`;
const why = (s, i) => `<a class="hn-why" href="${url(s)}"><span class="hn-n">0${i + 1}</span><div>${tags(s)}</div><h3>${esc(s.headline)}</h3><div class="hn-wl">What happened</div><p>${esc(s.summary)}</p><div class="hn-wl">Why it matters</div><p>${esc(s.why)}</p>
  ${(s.entities || []).length ? `<div class="hn-ents">${s.entities.map(e => `<span class="hn-ent">${company(e) ? `<img src="${logoSrc(e)}" alt="" ${hideBad}>` : ''}${esc(e.name)}${e.ticker ? `<code>${esc(e.ticker)}</code>` : ''}</span>`).join('')}</div>` : ''}</a>`;
function countries(list) {
  const c = {}; for (const s of list) c[s.location.country] = (c[s.location.country] || 0) + 1;
  return Object.entries(c).sort((a, b) => b[1] - a[1]).slice(0, 14).map(([k, n]) => `<a class="hn-cty" href="assets/globe/news.html?country=${encodeURIComponent(k)}">${flagSrc(k) ? `<img src="${flagSrc(k)}" alt="">` : ''}<span><b>${esc(nm(k))}</b><small>${n} ${n === 1 ? 'story' : 'stories'}</small></span></a>`).join('');
}
// rank: importance, then sources, then recency
const rank = (a, b) => (b.importance - a.importance) || ((b.sources?.length || 1) - (a.sources?.length || 1)) || (Date.parse(b.published_at) - Date.parse(a.published_at));
async function loadNews() {
  const [n, iso] = await Promise.all([fetch('assets/globe/news-live.json', { cache: 'no-cache' }).then(r => r.json()), fetch('assets/globe/iso.json').then(r => r.json()).catch(() => ({}))]);
  ISO = iso; const stories = n.stories || [];
  return { stories, top: [...stories].sort(rank), latest: [...stories].sort((a, b) => Date.parse(b.published_at) - Date.parse(a.published_at)), updated: n.updated_at,
    moved: [...stories].filter(s => s.market_moving || s.importance === 3).sort(rank) };
}
const updatedText = t => 'Live · updated ' + new Date(t).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
