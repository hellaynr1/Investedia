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
  const rxRow = ({ i, a }) => a ? (() => { const m = move(a, S.win); return `<div class="nf-rx" data-s="${esc(a.s)}" role="button" tabindex="0"><span>${aIcon(a)}</span><b>${esc(a.n)}</b>${arrow(i.direction)}${line(series(a, S.win), 60, 20, col(m))}<span class="mono ${cls(m)}">${fmt(m)}</span></div>`; })() : `<div class="nf-rx" style="grid-template-columns:auto 1fr auto"><span>${iIcon(i)}</span><b>${esc(i.name)}</b>${arrow(i.direction)}</div>`;
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
    $('nf-strip').innerHTML = L.map(a => `<button type="button" class="nf-t" data-s="${esc(a.s)}"><small>${aIcon(a)}<span>${esc(a.n)}</span></small><span class="mono ${cls(a.d)}">${fmt(a.d)}</span>${line(series(a, 'd'), 100, 28, col(a.d))}</button>`).join('');
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

  // ---- Mover detail: chart with numbered pins + story rail (what happened, how much it gained or lost) ----
  const DAY = 864e5;
  const tradingDates = (a, n) => { const out = []; let d = new Date(); d.setUTCHours(12, 0, 0, 0); const wk = x => x.getUTCDay() % 6 === 0; if (a.t !== 'crypto') while (wk(d)) d = new Date(d - DAY); while (out.length < n) { out.unshift(d.toISOString().slice(0, 10)); d = new Date(d - DAY); if (a.t !== 'crypto') while (wk(d)) d = new Date(d - DAY); } return out; };
  function steps(a, k) {
    const days = WIN.find(w => w[0] === k)[2], list = S.stories.filter(st => Date.now() - Date.parse(st.published_at) <= days * DAY && (st.impacts || []).some(i => find(i.ticker) === a)).sort((x, y) => Date.parse(x.published_at) - Date.parse(y.published_at));
    const v = series(a, k), intra = k === 'd' && S.intra[a.s]?.d1;
    const dates = intra ? null : tradingDates(a, (a.sp || []).length).slice(-v.length);
    return list.map((st, n) => {
      const t = Date.parse(st.published_at); let x, m, unit;
      if (intra) { const [t0, t1] = intra.t.map(z => z * 1000); x = Math.min(1, Math.max(0, (t - t0) / (t1 - t0))); const j = Math.round(x * (v.length - 1)); m = pc(v[v.length - 1], v[j]); unit = 'since'; }
      else { const ds = new Date(t).toISOString().slice(0, 10); let j = dates.findIndex(z => z >= ds); if (j < 0) j = v.length - 1; if (j < 1) j = 1; x = j / (v.length - 1); m = pc(v[j], v[j - 1]); unit = 'that day'; }
      return { st, x, m, unit, n: n + 1, j: Math.round(x * (v.length - 1)), i: st.impacts.find(i => find(i.ticker) === a) };
    });
  }
  function sheet(a, k) {
    const m = move(a, k), v = series(a, k), st = steps(a, k), up = m >= 0;
    const lo = Math.min(...v), hi = Math.max(...v), r = hi - lo || 1;
    const pins = st.map(z => { const j = Math.round(z.x * (v.length - 1)); const y = 1 - (v[j] - lo) / r; return `<button type="button" class="nf-pin ${cls(z.m)}" data-n="${z.n}" style="left:${(z.x * 100).toFixed(1)}%;top:${(y * 88 + 6).toFixed(1)}%">${z.n}</button>`; }).join('');
    const best = st.length ? st.reduce((b, z) => Math.abs(z.m) > Math.abs(b.m) ? z : b) : null;
    const gapOf = (z, nx) => { const to = nx ? v[nx.j] : v[v.length - 1], g = pc(to, v[z.j]); return `<li class="nf-gap ${cls(g)}"><span>${g > 0.005 ? '↑' : g < -0.005 ? '↓' : '↔'} then ${fmt(g)} ${nx ? 'until step ' + nx.n : 'until now'}</span></li>`; };
    const mx = Math.max(0.01, ...st.map(z => Math.abs(z.m)));
    const rail = st.length ? st.map((z, q) => `<li class="nf-step ${cls(z.m)}" data-n="${z.n}"><span class="nf-dot">${z.n}</span><div><span class="nf-eb">${new Date(z.st.published_at).toLocaleString('en-GB', { weekday: 'short', hour: '2-digit', minute: '2-digit' })} · ${ago(z.st.published_at)}</span><a href="story.html?id=${encodeURIComponent(z.st.id)}"><b>${esc(z.st.headline)}</b></a><p>${esc(z.i?.why || z.st.why || '')}</p><div class="nf-bar2"><i style="width:${Math.max(4, Math.abs(z.m) / mx * 100).toFixed(0)}%"></i><span class="mono ${cls(z.m)}">${fmt(z.m)}<small> ${z.unit}</small></span></div></div></li>`).join('') : '<li class="nf-quiet">No story in our feed names this asset in this window, so there is no news to point to for this move.</li>';
    return `<div class="nf-sh0"><span class="nf-lg">${aIcon(a)}</span><div><b class="nf-nm">${esc(a.n)}</b><span class="nf-sy">${esc(a.s.replace(/[=^]/g, ''))}</span></div><button class="nf-close" type="button" aria-label="Close">×</button></div>
      <div class="nf-tot"><span class="mono ${cls(m)}">${fmt(m)}</span><div class="nb-seg nf-wtabs">${WIN.map(([kk, l]) => `<button type="button" data-k="${kk}" aria-pressed="${kk === k}">${l}</button>`).join('')}</div></div>
      <div class="nf-chart">${line(v, 300, 120, col(m))}${pins}</div>
      <div class="nf-sum">${st.length ? `<b>${st.length}</b> ${st.length === 1 ? 'story' : 'stories'} named it${best ? ` · biggest move <b class="${cls(best.m)}">${fmt(best.m)}</b> at step ${best.n}` : ''}` : 'Quiet window'}</div>
      <ol class="nf-rail">${rail}</ol>
      <p class="mv-note">Moves shown are the asset's price change on the day of each story (or since it, for 24h). They show the news around a move, not proof it caused it. Not investment advice.</p>`;
  }
  let cur = null;
  function openSheet(sym, k) {
    const a = S.by[sym]; if (!a) return; cur = { a, k: k || S.win };
    let el = $('nf-sheet'); if (!el) { el = document.createElement('div'); el.id = 'nf-sheet'; el.className = 'nf-sheet'; el.innerHTML = '<div class="nf-bg"></div><aside class="nf-pane" role="dialog" aria-modal="true"></aside>'; document.body.append(el); el.addEventListener('click', e => { if (e.target.closest('.nf-bg,.nf-close')) closeSheet(); const w = e.target.closest('.nf-wtabs button'); if (w) { cur.k = w.dataset.k; paint(); } const p = e.target.closest('.nf-pin'); if (p) { el.querySelectorAll('.nf-step').forEach(x => x.classList.toggle('on', x.dataset.n === p.dataset.n)); el.querySelectorAll('.nf-pin').forEach(x => x.classList.toggle('on', x === p)); const t = el.querySelector(`.nf-step[data-n="${p.dataset.n}"]`); t && t.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); } }); }
    paint(); el.hidden = false; document.documentElement.classList.add('nf-lock'); el.querySelector('.nf-pane').scrollTop = 0;
  }
  const paint = () => { $('nf-sheet').querySelector('.nf-pane').innerHTML = sheet(cur.a, cur.k); };
  function closeSheet() { const el = $('nf-sheet'); if (el) el.hidden = true; document.documentElement.classList.remove('nf-lock'); }
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeSheet(); });
  $('nf-win').innerHTML = WIN.map(([k, l]) => `<button type="button" data-k="${k}" aria-pressed="false">${l}</button>`).join('');
  $('nf-sort').innerHTML = SORT.map(([k, l]) => `<button type="button" data-k="${k}" aria-pressed="false">${l}</button>`).join('');
  $('nf-win').onclick = e => { const b = e.target.closest('button'); if (b) { S.win = b.dataset.k; S.shown = 10; draw(); } };
  $('nf-sort').onclick = e => { const b = e.target.closest('button'); if (b) { S.sort = b.dataset.k; S.shown = 10; draw(); } };
  $('nf-q').addEventListener('input', e => { S.q = e.target.value; S.shown = 10; draw(); });
  $('nf-more').onclick = () => { S.shown += 10; draw(); };
  $('nf-chip').onclick = () => { S.q = ''; $('nf-q').value = ''; draw(); };
  $('nf-strip').onclick = e => { const t = e.target.closest('.nf-t'); if (t) openSheet(t.dataset.s, 'w'); };
  $('nf-list').addEventListener('click', e => { const r = e.target.closest('.nf-rx[data-s]'); if (r) openSheet(r.dataset.s); });
  document.addEventListener('keydown', e => { if (e.key === '/' && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) { e.preventDefault(); $('nf-q').focus(); } });
  Promise.all([AssetIcons.ready, loadNews(), fetch('assets/globe/markets.json', { cache: 'no-cache' }).then(r => r.json()).catch(() => ({ assets: [] })), fetch('assets/globe/news-prices.json', { cache: 'no-cache' }).then(r => r.json()).catch(() => ({ assets: {} })), fetch('assets/intraday.json', { cache: 'no-cache' }).then(r => r.json()).catch(() => ({ s: {} }))])
    .then(([, n, m, np, i]) => { S.stories = n.stories || []; S.mk = m.assets || []; S.by = Object.fromEntries(S.mk.map(a => [a.s, a])); for (const [k, a] of Object.entries(np.assets || {})) S.by[k] = a; S.intra = i.s || {}; $('nf-up').textContent = 'Updated ' + new Date(n.updated).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }); hero(); strip(); draw(); })
    .catch(e => { console.error('news', e); $('nf-list').innerHTML = '<div class="nf-none">News could not load. Please refresh.</div>'; });
})();
