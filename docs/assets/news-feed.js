// News page: story of the day, biggest movers, and "event -> reaction" cards. Helpers (esc, ago, loadNews, BF, flagSrc, company, logoSrc) come from home-news.js.
(() => {
  const $ = id => document.getElementById(id);
  const WIN = [['d', 'Today', 1], ['w', 'Week', 7], ['m', 'Month', 30]];
  const SORT = [['new', 'Newest'], ['big', 'Biggest reaction']];
  const CATN = { markets: 'Markets', companies: 'Companies', economy: 'Economy', technology: 'Technology', crypto: 'Crypto', commodities: 'Commodities', geopolitics: 'Geopolitics' };
  const S = { win: 'w', sort: 'new', q: '', shown: 10, stories: [], by: {}, intra: {}, mk: [] };
  const pc = (a, b) => b ? (a / b - 1) * 100 : 0;
  const move = (a, k) => k === 'd' ? a.d : k === 'w' ? a.w : (a.sp && a.sp.length > 1 ? pc(a.sp[a.sp.length - 1], a.sp[0]) : 0);
  const fmt = v => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toFixed(Math.abs(v) >= 10 ? 1 : 2) + '%';
  const cls = v => v > 0.005 ? 'u' : v < -0.005 ? 'd' : 'o';
  const col = v => v > 0.005 ? '#34d399' : v < -0.005 ? '#f87171' : '#8b8b94';
  const series = (a, k) => k === 'd' ? (S.intra[a.s]?.d1?.c || (a.sp || []).slice(-2)) : k === 'w' ? (a.sp || []).slice(-6) : (a.sp || []);
  const line = (v, w, h, c) => { if (v.length < 2) return ''; const lo = Math.min(...v), hi = Math.max(...v), r = hi - lo || 1; return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none"><path d="${v.map((y, i) => (i ? 'L' : 'M') + (i / (v.length - 1) * w).toFixed(1) + ' ' + (h - 3 - (y - lo) / r * (h - 6)).toFixed(1)).join('')}" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke"/></svg>`; };
  const arrow = d => `<span class="nf-ar ${d === 'up' ? 'u' : d === 'down' ? 'd' : 'o'}">${d === 'up' ? '↑' : d === 'down' ? '↓' : d === 'mixed' ? '↔' : '–'}</span>`;
  const bf = a => a.t === 'crypto' ? `https://cdn.brandfetch.io/crypto/${encodeURIComponent(a.s.split('-')[0])}/w/96/h/96/fallback/404?c=${BF}` : a.t === 'stocks' && !/[\^=]/.test(a.s) ? `https://cdn.brandfetch.io/ticker/${encodeURIComponent(a.s)}/w/96/h/96/fallback/404?c=${BF}` : '';
  const aIcon = a => AssetIcons.icon(a);
  const iIcon = i => i.kind === 'country' ? (flagSrc(i.country) ? `<img class="nb-fl" src="${flagSrc(i.country)}" alt="" onerror="this.remove()">` : AssetIcons.icon({ n: i.name })) : AssetIcons.icon({ s: i.ticker || '', n: i.name, t: /-USD$/.test(i.ticker || '') ? 'crypto' : 'stocks', cc: i.country ? String(i.country).toLowerCase() : '' });
  // The reactions of one story: priced assets first, then other touched names with just the arrow.
  const find = t => t && (S.by[t] || S.by[t.replace(/-USD$/, '')] || S.by[t.replace(/=X$/, '')]) || null;
  const reactions = s => { const seen = new Set(), out = []; for (const i of s.impacts || []) { const k = i.ticker || i.name.toLowerCase(); if (seen.has(k)) continue; seen.add(k); out.push({ i, a: find(i.ticker) }); } return out.sort((x, y) => !!y.a - !!x.a).slice(0, 4); };
  const biggest = s => Math.max(0, ...reactions(s).filter(r => r.a).map(r => Math.abs(move(r.a, S.win))));
  const rxRow = ({ i, a }) => a ? (() => { const m = move(a, S.win); return `<div class="nf-rx"><span>${aIcon(a)}</span><b>${esc(a.n)}</b>${arrow(i.direction)}${line(series(a, S.win), 60, 20, col(m))}<span class="mono ${cls(m)}">${fmt(m)}</span></div>`; })() : `<div class="nf-rx" style="grid-template-columns:auto 1fr auto"><span>${iIcon(i)}</span><b>${esc(i.name)}</b>${arrow(i.direction)}</div>`;
  const thumbOf = s => s.image ? `assets/globe/${esc(s.image.file)}` : '';
  const hit = (s, q) => !q || [s.headline, s.summary, ...(s.entities || []).map(e => e.name), ...(s.impacts || []).map(i => i.name), s.location?.country, s.location?.place].some(t => String(t || '').toLowerCase().includes(q));
  function hero() {
    const day = S.stories.filter(s => Date.now() - Date.parse(s.published_at) < 36 * 36e5);
    const pool = (day.length ? day : S.stories).map(s => ({ s, sc: (s.importance || 1) * 10 + (s.market_moving ? 8 : 0) + reactions(s).filter(r => r.a).length * 3 + (Date.parse(s.published_at) - Date.now()) / 36e5 })).sort((a, b) => b.sc - a.sc);
    const s = pool[0] && pool[0].s; if (!s) { $('nf-hero').innerHTML = ''; return; }
    const th = thumbOf(s), e = (s.entities || []).find(company);
    const chips = reactions(s).map(({ i, a }) => a ? `<span class="nf-chip">${aIcon(a)}<b>${esc(a.n)}</b>${arrow(i.direction)}<span class="mono ${cls(move(a, 'd'))}">${fmt(move(a, 'd'))}</span></span>` : `<span class="nf-chip">${iIcon(i)}<b>${esc(i.name)}</b>${arrow(i.direction)}</span>`).join('');
    $('nf-hero').innerHTML = `<a class="nf-hero" href="story.html?id=${encodeURIComponent(s.id)}"><div class="im"${th ? ` style="background-image:url('${th}')"` : ''}>${e ? `<img class="nb-lg" src="${logoSrc(e)}" alt="" onerror="this.remove()">` : ''}</div><div class="tx"><span class="nf-eb">Story of the day · ${esc(CATN[s.category] || '')} · ${ago(s.published_at)}</span><h2>${esc(s.headline)}</h2><p>${esc(s.why || s.summary || '')}</p><div class="nf-chips">${chips}</div><span class="nf-go">Read the story →</span></div></a>`;
  }
  function strip() {
    const known = a => !/[.\d]/.test(a.s.replace(/[=^-]/g, '')) && a.t !== 'fx' && (a.m || a.t === 'crypto' || a.t === 'cmd' || S.intra[a.s]);
    const L = S.mk.filter(known).filter(a => isFinite(a.d) && Math.abs(a.d) < 40 && series(a, 'd').length >= (a.t === 'stocks' ? 6 : 2)).sort((x, y) => Math.abs(y.d) - Math.abs(x.d)).slice(0, 10);
    $('nf-strip').innerHTML = L.map(a => `<button type="button" class="nf-t" data-n="${esc(a.n)}"><small>${aIcon(a)}<span>${esc(a.n)}</span></small><span class="mono ${cls(a.d)}">${fmt(a.d)}</span>${line(series(a, 'd'), 100, 28, col(a.d))}</button>`).join('');
  }
  function draw() {
    const cut = Date.now() - WIN.find(w => w[0] === S.win)[2] * 864e5, q = S.q.trim().toLowerCase();
    let L = S.stories.filter(s => Date.parse(s.published_at) >= cut && hit(s, q));
    L = S.sort === 'big' ? L.sort((a, b) => biggest(b) - biggest(a) || Date.parse(b.published_at) - Date.parse(a.published_at)) : L.sort((a, b) => Date.parse(b.published_at) - Date.parse(a.published_at));
    $('nf-list').innerHTML = L.slice(0, S.shown).map(s => { const th = thumbOf(s), rx = reactions(s); return `<article class="nf-ev${rx.length ? '' : ' solo'}"><div class="l"><span class="nf-eb">${esc(CATN[s.category] || '')} · ${esc((s.location?.place || '').split(',')[0])} · ${ago(s.published_at)}</span><h3><a href="story.html?id=${encodeURIComponent(s.id)}">${esc(s.headline)}</a></h3><p>${esc(s.why || s.summary || '')}</p>${th ? `<div class="ph" style="background-image:url('${th}')"></div>` : ''}</div>${rx.length ? `<div class="r"><span class="nf-eb">What moved</span>${rx.map(rxRow).join('')}</div>` : ''}</article>`; }).join('') || '<div class="nf-none">No stories match. Try a wider window or another search.</div>';
    $('nf-more').hidden = L.length <= S.shown;
    document.querySelectorAll('#nf-win button').forEach(b => b.setAttribute('aria-pressed', b.dataset.k === S.win));
    document.querySelectorAll('#nf-sort button').forEach(b => b.setAttribute('aria-pressed', b.dataset.k === S.sort));
    $('nf-chip').hidden = !q; $('nf-chip').className = 'nf-x'; $('nf-chip').innerHTML = q ? `<button type="button">${esc(S.q)} <span aria-hidden="true">×</span></button>` : '';
  }
  $('nf-win').innerHTML = WIN.map(([k, l]) => `<button type="button" data-k="${k}" aria-pressed="false">${l}</button>`).join('');
  $('nf-sort').innerHTML = SORT.map(([k, l]) => `<button type="button" data-k="${k}" aria-pressed="false">${l}</button>`).join('');
  $('nf-win').onclick = e => { const b = e.target.closest('button'); if (b) { S.win = b.dataset.k; S.shown = 10; draw(); } };
  $('nf-sort').onclick = e => { const b = e.target.closest('button'); if (b) { S.sort = b.dataset.k; S.shown = 10; draw(); } };
  $('nf-q').addEventListener('input', e => { S.q = e.target.value; S.shown = 10; draw(); });
  $('nf-more').onclick = () => { S.shown += 10; draw(); };
  $('nf-chip').onclick = () => { S.q = ''; $('nf-q').value = ''; draw(); };
  $('nf-strip').onclick = e => { const t = e.target.closest('.nf-t'); if (t) { S.q = t.dataset.n; $('nf-q').value = S.q; S.win = 'm'; S.shown = 10; draw(); $('nf-list').scrollIntoView({ behavior: 'smooth', block: 'start' }); } };
  document.addEventListener('keydown', e => { if (e.key === '/' && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) { e.preventDefault(); $('nf-q').focus(); } });
  Promise.all([AssetIcons.ready, loadNews(), fetch('assets/globe/markets.json', { cache: 'no-cache' }).then(r => r.json()).catch(() => ({ assets: [] })), fetch('assets/globe/news-prices.json', { cache: 'no-cache' }).then(r => r.json()).catch(() => ({ assets: {} })), fetch('assets/intraday.json', { cache: 'no-cache' }).then(r => r.json()).catch(() => ({ s: {} }))])
    .then(([, n, m, np, i]) => { S.stories = n.stories || []; S.mk = m.assets || []; S.by = Object.fromEntries(S.mk.map(a => [a.s, a])); for (const [k, a] of Object.entries(np.assets || {})) S.by[k] = a; S.intra = i.s || {}; $('nf-up').textContent = 'Updated ' + new Date(n.updated).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }); hero(); strip(); draw(); })
    .catch(e => { console.error('news', e); $('nf-list').innerHTML = '<div class="nf-none">News could not load. Please refresh.</div>'; });
})();
