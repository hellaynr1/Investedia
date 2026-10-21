// Shared helpers for the News concept previews. Reads the real live feed (../globe/news-live.json).
const BF = '1idNJqyfpKbma454ae4';
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const NM = { 'United States of America': 'United States' };
const nm = c => NM[c] || c;
const CATS = [['all', 'All'], ['markets', 'Markets'], ['companies', 'Companies'], ['economy', 'Economy'], ['technology', 'Technology'], ['crypto', 'Crypto'], ['commodities', 'Commodities'], ['geopolitics', 'Geopolitics']];
const CL = Object.fromEntries(CATS);
let ISO = {};
const ago = t => { const m = Math.max(1, Math.round((Date.now() - Date.parse(t)) / 6e4)); return m < 60 ? m + ' min ago' : m < 1440 ? Math.round(m / 60) + ' h ago' : Math.round(m / 1440) + ' d ago'; };
const flag = (iso2, cls = 'fl') => iso2 ? `<img class="${cls}" src="../globe/flags/${iso2.toLowerCase()}.svg" alt="" onerror="this.remove()">` : '';
const sflag = s => flag(ISO[s.location.country], 'fl');
const logo = (t, cls = 'lg') => t && !/[\^=]/.test(t) ? `<img class="${cls}" src="https://cdn.brandfetch.io/${/-USD$/.test(t) ? 'crypto/' + encodeURIComponent(t.split('-')[0]) : 'ticker/' + encodeURIComponent(t)}/w/96/h/96/fallback/404?c=${BF}" alt="" onerror="this.remove()">` : '';
const icon = i => i.kind === 'country' || !i.ticker ? flag(i.country) : logo(i.ticker) || flag(i.country);
const arrow = d => `<span class="dir ${d}">${d === 'up' ? '↑' : d === 'down' ? '↓' : d === 'mixed' ? '↔' : '·'}</span>`;
const url = s => `../globe/news.html?story=${encodeURIComponent(s.id)}`;
const rank = (a, b) => (b.importance - a.importance) || (Date.parse(b.published_at) - Date.parse(a.published_at));
async function load() {
  const [n, iso] = await Promise.all([fetch('../globe/news-live.json', { cache: 'no-cache' }).then(r => r.json()), fetch('../globe/iso.json').then(r => r.json()).catch(() => ({}))]);
  ISO = iso; return n.stories;
}
const HEADER = `<header class="hdr"><div class="w"><a class="wm" href="#">Invested<i>i</i>a</a><nav class="nav"><a href="#">Home</a><a href="#">Globe</a><a class="on" href="#">News</a><a href="#">Learn</a><a href="#">Tools</a><a href="#">About</a></nav><span class="sp"></span><a class="btn p" href="#">Sign up</a></div></header>`;
const FOOTER = `<div class="w"><p class="ft">Summaries are written with the help of AI from each source's own reporting. Every story links to its source. Not investment advice.</p></div>`;
