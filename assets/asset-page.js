// Asset page: ?s=SYMBOL. Price, chart, volatility, big-move analysis, related articles. Crypto streams through our live relay when it is configured.
(() => {
  const root = document.getElementById('ap'), qs = new URLSearchParams(location.search);
  const ALIAS = { XAU: 'GC=F', XAG: 'SI=F', WTI: 'CL=F', BRENT: 'BZ=F', NG: 'NG=F', HG: 'HG=F', PL: 'PL=F', ZW: 'ZW=F', ZC: 'ZC=F', ZS: 'ZS=F', KC: 'KC=F', SB: 'SB=F', BTC: 'BTC-USD', ETH: 'ETH-USD', SOL: 'SOL-USD', XRP: 'XRP-USD', SPX: '^GSPC', NDX: '^NDX', DJI: '^DJI', FTSE: '^FTSE', DAX: '^GDAXI', N225: '^N225' };
  const esc = t => String(t ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const nf = v => v == null || !isFinite(v) ? '—' : v.toLocaleString('en-US', { maximumFractionDigits: Math.abs(v) >= 1 ? 2 : 4, minimumFractionDigits: Math.abs(v) >= 1 ? 2 : 4 });
  const money = v => window.InvPrefs ? InvPrefs.fmt(v, S.a) : nf(v);
  const fmt = v => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toFixed(Math.abs(v) >= 10 ? 1 : 2) + '%';
  const cls = v => v > 0.005 ? 'u' : v < -0.005 ? 'd' : 'o', arrow = v => v > 0.005 ? '↑' : v < -0.005 ? '↓' : '↔', col = v => v > 0.005 ? '#34d399' : v < -0.005 ? '#f87171' : '#8b8b94';
  const pc = (a, b) => b ? (a / b - 1) * 100 : 0;
  const S = { win: 'd', a: null, intra: {}, live: null };
  const std = sp => { const r = (sp || []).slice(-22).map((x, i, v) => i ? (x / v[i - 1] - 1) * 100 : null).slice(1); if (r.length < 8) return null; const m = r.reduce((t, x) => t + x, 0) / r.length; return Math.sqrt(r.reduce((t, x) => t + (x - m) ** 2, 0) / r.length); };
  const series = (a, k) => k === 'd' ? (S.intra[a.s]?.d1?.c?.length > 3 ? S.intra[a.s].d1.c : (a.sp || []).slice(-6)) : k === 'w' ? (a.sp || []).slice(-6) : (a.sp || []);
  const chg = (a, k) => k === 'd' ? a.d : k === 'w' ? a.w : pc((a.sp || [])[a.sp.length - 1], (a.sp || [])[0]);
  const area = (v, c, w = 600, h = 220) => { if (!v || v.length < 2) return ''; const lo = Math.min(...v), hi = Math.max(...v), r = hi - lo || 1, pts = v.map((y, i) => [i / (v.length - 1) * w, h - 6 - (y - lo) / r * (h - 12)]), d = pts.map((p, i) => (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join(''); return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none"><path d="${d}L${w} ${h}L0 ${h}Z" fill="${c}" opacity=".12"/><path d="${d}" fill="none" stroke="${c}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke"/></svg>`; };
  const find = (by, s) => by[s] || by[ALIAS[s]] || by[s + '-USD'] || by[s + '=F'] || by['^' + s] || Object.values(by).find(a => a.n && a.n.toLowerCase() === s.toLowerCase());
  function related(a, stories) {
    const sym = a.s.toUpperCase(), base = sym.replace('-USD', '').replace('=X', ''), name = (a.n || '').toLowerCase(), out = [];
    for (const s of stories) { const i = (s.impacts || []).find(i => { const t = String(i.ticker || '').toUpperCase(); return t === sym || t === base || (name.length > 3 && String(i.name || '').toLowerCase() === name); }); if (i) out.push({ s, i }); }
    return out.sort((x, y) => Date.parse(y.s.published_at) - Date.parse(x.s.published_at)).slice(0, 8);
  }
  if (window.InvPrefs) InvPrefs.onChange(() => { if (S.a) render(); });
  function render() {
    const a = S.a, live = S.live, price = live?.p ?? a.p, m = S.win === 'd' && live?.o ? pc(live.p, live.o) : chg(a, S.win), sd = std(a.sp), z = sd ? a.d / sd : null, rel = S.rel, an = S.an?.[a.s];
    const level = z == null ? null : Math.abs(z) >= 2 ? ['Unusually large move', 'big'] : Math.abs(z) >= 1.3 ? ['Notable move', 'mid'] : ['Within its normal range', 'ok'];
    const lo = Math.min(...(a.sp || [a.p])), hi = Math.max(...(a.sp || [a.p])), pos = hi === lo ? 50 : (price - lo) / (hi - lo) * 100;
    const sym = a.s.replace(/[=^]/g, '').replace('-USD', '');
    const base = z == null ? '' : `${a.n} is ${a.d > 0 ? 'up' : a.d < 0 ? 'down' : 'flat'} ${Math.abs(a.d).toFixed(2)}% today, ${Math.abs(z).toFixed(1)}× its typical daily move (21-day volatility ${sd.toFixed(2)}%).`;
    document.title = `${a.n} (${sym}) · Investedia`;
    root.innerHTML = `<a class="ap-back" href="markets.html">← Markets</a>
      <header class="ap-h"><span class="ap-ic">${window.AssetIcons ? AssetIcons.icon(a) : ''}</span><div><h1>${esc(a.n)}</h1><small>${esc(sym)} · ${({ stocks: a.g === 'Index' ? 'Index' : 'Stock', crypto: 'Crypto', cmd: 'Commodity', fx: 'Currency pair' })[a.t] || ''}</small></div><span class="ap-st ${live ? 'live' : ''}"><i></i>${live ? 'Live' : 'Delayed'}</span></header>
      <div class="ap-px"><span class="ap-p mono" data-k="p">${money(price)}</span><span class="ap-chip ${cls(m)}" data-k="c">${arrow(m)} ${fmt(m)}</span></div>
      <div class="ap-seg">${[['d', 'Today'], ['w', 'Week'], ['m', 'Month']].map(([k, l]) => `<button type="button" data-k="${k}" aria-pressed="${k === S.win}">${l}</button>`).join('')}</div>
      <div class="ap-ch">${area(series(a, S.win), col(m))}</div>
      <div class="ap-grid"><div><small>Day change</small><b class="mono ${cls(a.d)}">${arrow(a.d)} ${fmt(a.d)}</b></div><div><small>Week</small><b class="mono ${cls(a.w)}">${arrow(a.w)} ${fmt(a.w || 0)}</b></div><div><small>Month</small><b class="mono ${cls(chg(a, 'm'))}">${arrow(chg(a, 'm'))} ${fmt(chg(a, 'm'))}</b></div><div><small>Volatility (21d)</small><b class="mono">${sd ? sd.toFixed(2) + '% / day' : '—'}</b></div></div>
      <div class="ap-rg"><div class="mh-rg"><i style="left:${pos.toFixed(0)}%"></i></div><div class="ap-rgl"><span>${money(lo)}</span><span>1-month range</span><span>${money(hi)}</span></div></div>
      <section class="ap-card ${level ? level[1] : ''}"><div class="ap-ch2"><span class="nf-eb">Move analysis</span>${level ? `<span class="ap-lv">${level[0]}</span>` : ''}</div>
        <p class="ap-tx">${esc(an ? an.text : (base || 'Not enough price history to measure volatility yet.'))}</p>
        ${an ? `<small class="ap-meta">${an.ai ? 'Written with AI from the price data and the linked articles' : 'Generated from the price data and the linked articles'} · updated ${new Date(S.anAsof).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}</small>` : ''}
        <div class="ap-pro"><b>Live analysis is coming to Investedia Pro.</b> Real-time alerts the moment ${esc(a.n)} makes an unusual move, and deeper analysis of every catalyst. Free analysis refreshes about every 10 minutes.</div></section>
      <section class="ap-sec"><h2>Articles naming ${esc(a.n)}</h2>${rel.length ? `<ol class="ap-rail">${rel.map(({ s, i }, n) => `<li class="${cls(i.direction === 'up' ? 1 : i.direction === 'down' ? -1 : 0)}"><span class="ap-dot">${rel.length - n}</span><div><span class="nf-eb">${new Date(s.published_at).toLocaleString('en-GB', { weekday: 'short', hour: '2-digit', minute: '2-digit' })} · ${esc(s.source?.name || '')}</span><a href="story.html?id=${encodeURIComponent(s.id)}"><b>${esc(s.headline)}</b></a><p>${esc(i.why || s.why || '')}</p></div><span class="ap-ar ${cls(i.direction === 'up' ? 1 : i.direction === 'down' ? -1 : 0)}">${i.direction === 'up' ? '↑' : i.direction === 'down' ? '↓' : '↔'}</span></li>`).join('')}</ol><a class="ap-more" href="news.html?asset=${encodeURIComponent(a.s)}">See all articles on the News page →</a>` : '<p class="ap-none">No article in our feed names this asset right now. Coverage appears here as soon as it is published.</p>'}</section>
      <p class="mv-note">Prices are delayed up to 10–15 minutes unless marked Live. Analysis describes the news around a move, not proof it caused it. Not investment advice.</p>`;
  }
  const poll = () => { if (!window.INV_LIVE_URL || S.a.t !== 'crypto') return; const t = async () => { try { const j = await (await fetch(INV_LIVE_URL, { cache: 'no-store' })).json(), v = j.p?.[S.a.s]; if (v) { const first = !S.live; S.live = { p: v.p, o: v.o || v.p / (1 + (v.pc || 0) / 100) }; if (first) render(); else { const p = root.querySelector('[data-k=p]'), c = root.querySelector('[data-k=c]'); if (p) { p.textContent = money(v.p); p.classList.remove('flash'); void p.offsetWidth; p.classList.add('flash'); } const m = S.win === 'd' ? pc(S.live.p, S.live.o) : null; if (c && m != null) { c.className = 'ap-chip ' + cls(m); c.textContent = `${arrow(m)} ${fmt(m)}`; } } } } catch {} }; t(); setInterval(() => { if (!document.hidden) t(); }, 3000); };
  const s = qs.get('s') || qs.get('asset') || '';
  Promise.all([AssetIcons.ready, fetch('assets/globe/markets.json').then(r => r.json()), fetch('assets/globe/news-prices.json').then(r => r.json()).catch(() => ({ assets: {} })), fetch('assets/intraday.json').then(r => r.json()).catch(() => ({ s: {} })), fetch('assets/globe/news-archive.json').then(r => r.ok ? r.json() : null).catch(() => null), fetch('assets/globe/analysis.json', { cache: 'no-cache' }).then(r => r.ok ? r.json() : null).catch(() => null)])
    .then(([, m, np, i, arc, an]) => {
      const by = Object.fromEntries((m.assets || []).map(a => [a.s, a])); Object.assign(by, np.assets || {});
      const a = s && find(by, s); if (!a) { root.innerHTML = `<a class="ap-back" href="markets.html">← Markets</a><div class="nb-none">We couldn’t find “${esc(s)}”. Try the search in the News menu.</div>`; return; }
      S.a = a; S.intra = i.s || {}; S.an = an?.items || {}; S.anAsof = an?.asof; S.rel = related(a, (arc && arc.stories) || []); render(); poll();
      root.addEventListener('click', e => { const b = e.target.closest('.ap-seg button'); if (b) { S.win = b.dataset.k; render(); } });
    }).catch(e => { console.error('asset', e); root.innerHTML = '<div class="nb-none">Asset data could not load. Please refresh.</div>'; });
})();
