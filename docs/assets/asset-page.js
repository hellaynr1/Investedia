// Asset page: ?s=SYMBOL. Price, chart, volatility, big-move analysis, related articles. Crypto streams through our live relay when it is configured.
(() => {
  const root = document.getElementById('ap'), qs = new URLSearchParams(location.search), EMB = qs.get('embed') === '1';
  const ALIAS = { XAU: 'GC=F', XAG: 'SI=F', WTI: 'CL=F', BRENT: 'BZ=F', NG: 'NG=F', HG: 'HG=F', PL: 'PL=F', ZW: 'ZW=F', ZC: 'ZC=F', ZS: 'ZS=F', KC: 'KC=F', SB: 'SB=F', BTC: 'BTC-USD', ETH: 'ETH-USD', SOL: 'SOL-USD', XRP: 'XRP-USD', SPX: '^GSPC', NDX: '^NDX', DJI: '^DJI', FTSE: '^FTSE', DAX: '^GDAXI', N225: '^N225' };
  const esc = t => String(t ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const nf = v => v == null || !isFinite(v) ? '—' : v.toLocaleString('en-US', { maximumFractionDigits: Math.abs(v) >= 1 ? 2 : 4, minimumFractionDigits: Math.abs(v) >= 1 ? 2 : 4 });
  const money = v => window.InvPrefs ? InvPrefs.fmt(v, S.a) : nf(v);
  const fmt = v => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toFixed(Math.abs(v) >= 10 ? 1 : 2) + '%';
  const cls = v => v > 0.005 ? 'u' : v < -0.005 ? 'd' : 'o', arrow = v => v > 0.005 ? '↑' : v < -0.005 ? '↓' : '↔', col = v => v > 0.005 ? '#34d399' : v < -0.005 ? '#f87171' : '#8b8b94';
  const pc = (a, b) => b ? (a / b - 1) * 100 : 0;
  const S = { win: 'd', a: null, intra: {}, live: null, hist: null };
  const std = sp => { const r = (sp || []).slice(-22).map((x, i, v) => i ? (x / v[i - 1] - 1) * 100 : null).slice(1); if (r.length < 8) return null; const m = r.reduce((t, x) => t + x, 0) / r.length; return Math.sqrt(r.reduce((t, x) => t + (x - m) ** 2, 0) / r.length); };
  const series = (a, k) => k === 'd' ? (S.intra[a.s]?.d1?.c?.length > 3 ? S.intra[a.s].d1.c : (a.sp || []).slice(-6)) : k === 'w' ? (a.sp || []).slice(-6) : (a.sp || []);
  const chg = (a, k) => k === 'd' ? a.d : k === 'w' ? a.w : pc((a.sp || [])[a.sp.length - 1], (a.sp || [])[0]);
  const area = (v, c, w = 600, h = 220) => { if (!v || v.length < 2) return ''; const lo = Math.min(...v), hi = Math.max(...v), r = hi - lo || 1, pts = v.map((y, i) => [i / (v.length - 1) * w, h - 6 - (y - lo) / r * (h - 12)]), d = pts.map((p, i) => (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join(''); return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none"><path d="${d}L${w} ${h}L0 ${h}Z" fill="${c}" opacity=".12"/><path d="${d}" fill="none" stroke="${c}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke"/></svg>`; };
  // News pins on the chart: each article that names the asset sits on the line at its publication time; same numbers as the list below
  function pins(a, rel, v) {
    if (!v || v.length < 2 || !rel.length) return '';
    const t = S.intra[a.s]?.d1?.t, end = S.win === 'd' && t?.length ? t[t.length - 1] * 1000 : Date.now(), start = S.win === 'd' ? (t?.length ? t[0] * 1000 : end - 864e5) : end - (S.win === 'w' ? 7 : 30) * 864e5;
    const lo = Math.min(...v), hi = Math.max(...v), r = hi - lo || 1, big = a.m === 1 || a.t !== 'stocks' || a.g === 'Index', max = big ? 8 : 3, used = [];
    const L = rel.map(({ s, i }, n) => ({ s, i, num: rel.length - n })).filter(x => { const ts = Date.parse(x.s.published_at); return ts >= start && ts <= end + 36e5; }).slice(0, max).map(x => ({ ...x, f: Math.round(Math.max(0, Math.min(1, (Date.parse(x.s.published_at) - start) / (end - start))) * (v.length - 1)) / (v.length - 1) })).sort((p, q) => p.f - q.f);
    let prev = -9; for (const x of L) { x.left = Math.max(x.f * 100, prev + 5); prev = x.left; }
    for (let k = L.length - 1, lim = 96; k >= 0; k--) { if (L[k].left > lim) L[k].left = lim; lim = L[k].left - 5; }
    return L.map(x => { const y = v[Math.round(x.f * (v.length - 1))], top = (214 - (y - lo) / r * 208) / 220 * 100;
      return `<button type="button" class="ap-pin ${cls(x.i.direction === 'up' ? 1 : x.i.direction === 'down' ? -1 : 0)}" style="left:${Math.max(2, x.left).toFixed(1)}%;top:${top.toFixed(1)}%" data-n="${x.num}" aria-label="Article ${x.num}: ${esc(x.s.headline)}">${x.num}</button>`;
    }).join('');
  }
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
    const sym = a.s.replace(/=F$/, '').replace(/^\^/, '').replace(/=X$/, '').replace('-USD', '');
    const base = z == null ? '' : `${a.n} is ${a.d > 0 ? 'up' : a.d < 0 ? 'down' : 'flat'} ${Math.abs(a.d).toFixed(2)}% today, ${Math.abs(z).toFixed(1)}× its typical daily move (21-day volatility ${sd.toFixed(2)}%).`;
    const cell = (l, v, bar) => `<div><small>${l}</small><b class="mono">${v}</b>${bar != null ? `<div class="mh-rg"><i style="left:${bar}%"></i></div>` : ''}</div>`;
    const rgc = (l, lo, hi, cur) => isFinite(lo) && isFinite(hi) && hi > lo ? cell(l, `${money(lo)} – ${money(hi)}`, Math.max(0, Math.min(100, (cur - lo) / (hi - lo) * 100)).toFixed(0)) : '';
    const d1 = (S.intra[a.s]?.d1?.c || []).filter(isFinite), H = S.hist, lastD = H?.daily?.[H.daily.length - 1];
    const dayLo = live?.l ?? (d1.length > 3 ? Math.min(...d1) : null), dayHi = live?.h ?? (d1.length > 3 ? Math.max(...d1) : null);
    const vol = live?.v ? (window.InvPrefs ? InvPrefs.compact(live.v, { t: 'crypto' }) : null) : (lastD && lastD[5] ? new Intl.NumberFormat(window.InvPrefs ? undefined : 'en', { notation: 'compact', maximumFractionDigits: 1 }).format(lastD[5]) : null);
    const figs = [rgc('Day range', dayLo, dayHi, price), rgc('52-week range', H?.lo52, H?.hi52, price), rgc('1-month range', lo, hi, price), vol ? cell('Volume', vol) : '', cell('Week', `<span class="${cls(a.w)}">${arrow(a.w)} ${fmt(a.w || 0)}</span>`), cell('Month', `<span class="${cls(chg(a, 'm'))}">${arrow(chg(a, 'm'))} ${fmt(chg(a, 'm'))}</span>`)].filter(Boolean);
    document.title = `${a.n} (${sym}) · Investedia`;
    root.innerHTML = `<a class="ap-back" href="markets.html">← Markets</a>
      <header class="ap-h"><span class="ap-ic">${window.AssetIcons ? AssetIcons.icon(a) : ''}</span><div><h1>${esc(a.n)}</h1><small>${esc(sym)} · ${({ stocks: a.g === 'Index' ? 'Index' : 'Stock', crypto: 'Crypto', cmd: 'Commodity', fx: 'Currency pair' })[a.t] || ''}</small></div><span class="ap-st ${live ? 'live' : ''}"><i></i>${live ? 'Live' : 'Delayed'}</span></header>
      <div class="ap-px"><span class="ap-p mono" data-k="p">${money(price)}</span><span class="ap-chip ${cls(m)}" data-k="c">${arrow(m)} ${fmt(m)}</span></div>
      <div class="ap-seg">${[['d', 'Today'], ['w', 'Week'], ['m', 'Month']].map(([k, l]) => `<button type="button" data-k="${k}" aria-pressed="${k === S.win}">${l}</button>`).join('')}</div>
      <div class="ap-ch"><div class="ap-cv">${area(series(a, S.win), col(m))}${pins(a, rel, series(a, S.win))}<div class="ap-tip" hidden></div></div></div>
      <div class="ap-fig">${figs.join('')}</div>
      <div class="ap-act">${tvSym(a) ? '<button type="button" class="ap-btn p" id="ap-full">Full chart</button>' : ''}<button type="button" class="ap-btn" id="ap-watch" aria-pressed="false">☆ Watch</button></div>
      <section class="ap-card ${level ? level[1] : ''}"><div class="ap-ch2"><span class="nf-eb">Move analysis</span>${level ? `<span class="ap-lv">${level[0]}</span>` : ''}</div>
        <p class="ap-tx">${esc(an ? an.text : (base || 'Not enough price history to measure volatility yet.'))}</p>
        ${an ? `<small class="ap-meta">${an.ai ? 'Written with AI from the price data and the linked articles' : 'Generated from the price data and the linked articles'} · updated ${new Date(S.anAsof).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}</small>` : ''}
        <div class="ap-pro"><b>Live analysis is coming to Investedia Pro.</b> Real-time alerts the moment ${esc(a.n)} makes an unusual move, and deeper analysis of every catalyst. Free analysis refreshes about every 15 minutes.</div></section>
      <section class="ap-sec"><h2>Articles naming ${esc(a.n)}</h2>${rel.length ? `<ol class="ap-rail">${rel.slice(0, EMB ? 3 : 20).map(({ s, i }, n) => `<li id="ap-a${rel.length - n}" class="${cls(i.direction === 'up' ? 1 : i.direction === 'down' ? -1 : 0)}"><span class="ap-dot">${rel.length - n}</span><div><span class="nf-eb">${new Date(s.published_at).toLocaleString('en-GB', { weekday: 'short', hour: '2-digit', minute: '2-digit' })} · ${esc(s.source?.name || '')}</span><a href="story.html?id=${encodeURIComponent(s.id)}"><b>${esc(s.headline)}</b></a><p>${esc(i.why || s.why || '')}</p></div><span class="ap-ar ${cls(i.direction === 'up' ? 1 : i.direction === 'down' ? -1 : 0)}">${i.direction === 'up' ? '↑' : i.direction === 'down' ? '↓' : '↔'}</span></li>`).join('')}</ol><a class="ap-more" href="news.html?asset=${encodeURIComponent(a.s)}">See all articles on the News page →</a>` : '<p class="ap-none">No article in our feed names this asset right now. Coverage appears here as soon as it is published.</p>'}</section>
      <p class="mv-note">Prices are delayed by 15 to 30 minutes unless marked Live. Analysis describes the news around a move, not proof it caused it. Not investment advice.</p>`;
  }
  const paintWatch = () => { const b = document.getElementById('ap-watch'); if (!b || !window.INVWATCH) return; const on = INVWATCH.has({ kind: 'asset', src: 'site', s: S.a.s }); b.setAttribute('aria-pressed', on); b.textContent = on ? '★ Watching' : '☆ Watch'; };
  // TradingView symbol for the free chart widget; null = no valid mapping, the button is hidden
  const TV = { '^GSPC': 'FOREXCOM:SPXUSD', '^IXIC': 'NASDAQ:IXIC', '^NDX': 'NASDAQ:NDX', '^DJI': 'TVC:DJI', '^RUT': 'TVC:RUT', '^VIX': 'TVC:VIX', '^FTSE': 'TVC:UKX', '^GDAXI': 'XETR:DAX', '^FCHI': 'TVC:CAC40', '^STOXX50E': 'TVC:SX5E', '^N225': 'TVC:NI225', '^HSI': 'TVC:HSI', 'GC=F': 'OANDA:XAUUSD', 'SI=F': 'OANDA:XAGUSD', 'PL=F': 'OANDA:XPTUSD', 'HG=F': 'COMEX:HG1!', 'CL=F': 'TVC:USOIL', 'BZ=F': 'TVC:UKOIL', 'NG=F': 'NYMEX:NG1!', 'ZW=F': 'CBOT:ZW1!', 'ZC=F': 'CBOT:ZC1!', 'ZS=F': 'CBOT:ZS1!', 'KC=F': 'ICEUS:KC1!', 'SB=F': 'ICEUS:SB1!', 'CC=F': 'ICEUS:CC1!', 'CT=F': 'ICEUS:CT1!' };
  const tvSym = a => TV[a.s] || (a.t === 'crypto' ? 'COINBASE:' + a.s.replace('-USD', '') + 'USD' : a.t === 'fx' ? 'FX:' + a.s : a.t === 'stocks' && /^[A-Z]{1,5}(-[A-Z])?$/.test(a.s) && a.cc === 'us' ? a.s.replace('-', '.') : null);
  function fullChart() {
    const box = root.querySelector('.ap-ch'); if (!box || box.dataset.tv) return; box.dataset.tv = '1'; box.style.height = 'auto';
    box.innerHTML = '<p class="ap-tvn">The full chart is provided by TradingView. Loading it connects your browser to TradingView, which receives your IP address and may set its own cookies. Nothing loads until you press the button.</p><button type="button" class="ap-btn p" id="ap-tvgo">Load TradingView chart</button>';
    box.querySelector('#ap-tvgo').onclick = () => { box.style.height = '420px'; box.innerHTML = '<div class="tradingview-widget-container" style="height:100%"><div class="tradingview-widget-container__widget" style="height:calc(100% - 22px)"></div><div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/" target="_blank" rel="noopener">Chart by TradingView</a> · data may be delayed</div></div>'; const sc = document.createElement('script'); sc.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js'; sc.async = true; sc.text = JSON.stringify({ autosize: true, symbol: tvSym(S.a), interval: 'D', theme: 'dark', style: '1', locale: 'en', backgroundColor: '#0e0e10', hide_side_toolbar: true, allow_symbol_change: false, withdateranges: true, details: false, calendar: false }); box.querySelector('.tradingview-widget-container').append(sc); };
  }
  const poll = () => { if (!window.INV_LIVE_URL || S.a.t !== 'crypto') return; const t = async () => { try { const j = await (await fetch(INV_LIVE_URL, { cache: 'no-store' })).json(), v = j.p?.[S.a.s]; if (v) { const first = !S.live; S.live = { p: v.p, o: v.o || v.p / (1 + (v.pc || 0) / 100), h: v.h, l: v.l, v: v.v }; if (first) render(); else { const p = root.querySelector('[data-k=p]'), c = root.querySelector('[data-k=c]'); if (p) { p.textContent = money(v.p); p.classList.remove('flash'); void p.offsetWidth; p.classList.add('flash'); } const m = S.win === 'd' ? pc(S.live.p, S.live.o) : null; if (c && m != null) { c.className = 'ap-chip ' + cls(m); c.textContent = `${arrow(m)} ${fmt(m)}`; } } } } catch {} }; t(); setInterval(() => { if (!document.hidden) t(); }, 3000); };
  const s = qs.get('s') || qs.get('asset') || '';
  Promise.all([AssetIcons.ready, fetch('assets/globe/markets.json').then(r => r.json()), fetch('assets/globe/news-prices.json').then(r => r.json()).catch(() => ({ assets: {} })), fetch('assets/intraday.json').then(r => r.json()).catch(() => ({ s: {} })), fetch('assets/globe/news-archive.json').then(r => r.ok ? r.json() : null).catch(() => null), fetch('assets/globe/analysis.json', { cache: 'no-cache' }).then(r => r.ok ? r.json() : null).catch(() => null)])
    .then(async ([, m, np, i, arc, an]) => {
      const by = Object.fromEntries((m.assets || []).map(a => [a.s, a])); Object.assign(by, np.assets || {});
      const a = s && find(by, s); if (!a) { root.innerHTML = `<a class="ap-back" href="markets.html">← Markets</a><div class="nb-none">We couldn’t find “${esc(s)}”. Try the search in the News menu.</div>`; return; }
      try { S.hist = await (await fetch('assets/hist/' + encodeURIComponent(a.s.replace(/-USD$|=F$|^\^/g, '')) + '.json')).json(); } catch { S.hist = null; }
      S.a = a; S.intra = i.s || {}; S.an = an?.items || {}; S.anAsof = an?.asof; S.rel = related(a, (arc && arc.stories) || []); render(); poll();
      root.addEventListener('click', e => { const b = e.target.closest('.ap-seg button'); if (b) { S.win = b.dataset.k; render(); return; }
        if (e.target.closest('#ap-watch') && window.INVWATCH) { INVWATCH.toggle({ kind: 'asset', src: 'site', s: S.a.s }); paintWatch(); return; }
        if (e.target.closest('#ap-full')) { fullChart(); return; }
        const pin = e.target.closest('.ap-pin'); const tip = root.querySelector('.ap-tip');
        if (pin && tip) { const it = S.rel.find((x, n) => S.rel.length - n === +pin.dataset.n); if (!it) return; if (!tip.hidden && tip.dataset.n === pin.dataset.n) { const li = document.getElementById('ap-a' + pin.dataset.n); if (li) { li.scrollIntoView({ behavior: 'smooth', block: 'center' }); li.classList.add('hl'); setTimeout(() => li.classList.remove('hl'), 1600); } return; }
          tip.dataset.n = pin.dataset.n; const dir = it.i.direction === 'up' ? '↑' : it.i.direction === 'down' ? '↓' : '↔'; tip.innerHTML = `<span class="nf-eb">${pin.dataset.n} · ${new Date(it.s.published_at).toLocaleString('en-GB', { weekday: 'short', hour: '2-digit', minute: '2-digit' })} · ${esc(it.s.source?.name || '')}</span><b>${esc(it.s.headline)}</b><p>${dir} ${esc(it.i.why || it.s.why || '')}</p><small>Tap again to jump to the article</small>`; tip.hidden = false;
          const box = root.querySelector('.ap-cv').getBoundingClientRect(), pb = pin.getBoundingClientRect(); tip.style.left = Math.max(0, Math.min(box.width - 270, pb.left - box.left - 120)) + 'px'; tip.style.top = (pb.top - box.top > 90 ? pb.top - box.top - 118 : pb.top - box.top + 30) + 'px'; return; }
        if (tip && !e.target.closest('.ap-tip')) tip.hidden = true; });
      paintWatch();
    }).catch(e => { console.error('asset', e); root.innerHTML = '<div class="nb-none">Asset data could not load. Please refresh.</div>'; });
})();
