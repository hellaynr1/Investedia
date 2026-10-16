// Investedia shared UI: icons, header + dropdowns, mobile drawer, search palette, ticker, footer, charts, tables.
(function () {
  const M = window.MOCK;
  const page = document.body.dataset.page || '';

  // ---------- icons (24px stroke set) ----------
  const P = {
    search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    chev: '<path d="m6 9 6 6 6-6"/>',
    star: '<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
    bell: '<path d="M6 8a6 6 0 1 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.9 1.9 0 0 0 3.4 0"/>',
    menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
    x: '<path d="M18 6 6 18M6 6l12 12"/>',
    arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
    stocks: '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 6-6"/>',
    indices: '<rect x="3" y="12" width="4" height="8" rx="1"/><rect x="10" y="7" width="4" height="13" rx="1"/><rect x="17" y="3" width="4" height="17" rx="1"/>',
    crypto: '<path d="M9 7h5a2.5 2.5 0 0 1 0 5H9zM9 12h6a2.5 2.5 0 0 1 0 5H9zM9 5v14M12 5v2M12 17v2"/>',
    currencies: '<circle cx="8" cy="8" r="5"/><circle cx="16" cy="16" r="5"/>',
    commodities: '<path d="M4 20h16M6 20l2-8h8l2 8M9 12l1.5-5h3L15 12"/>',
    bonds: '<path d="M4 4h12l4 4v12H4z"/><path d="M8 12h8M8 16h5M15 4v4h4"/>',
    funds: '<circle cx="12" cy="12" r="9"/><path d="M12 3v9l6.4 6.4"/>',
    screener: '<path d="M3 5h18M6 12h12M10 19h4"/>',
    calendar: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    calc: '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8M8 12h.01M12 12h.01M16 12h.01M8 16h.01M12 16h.01M16 16h.01"/>',
    heat: '<rect x="3" y="3" width="10" height="10" rx="1"/><rect x="15" y="3" width="6" height="6" rx="1"/><rect x="15" y="11" width="6" height="10" rx="1"/><rect x="3" y="15" width="10" height="6" rx="1"/>',
    compound: '<path d="M3 20c6 0 9-4 12-10 1.5-3 3-5 6-6"/><path d="M16 4h5v5"/>',
    earnings: '<path d="M4 4h16v16H4z"/><path d="M8 15v-3M12 15V9M16 15v-5"/>',
    sparkle: '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6"/>',
    home: '<path d="m3 11 9-7 9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>',
    building: '<path d="M4 21V5a1 1 0 0 1 1-1h9a1 1 0 0 1 1 1v16M15 9h4a1 1 0 0 1 1 1v11M3 21h18M8 8h3M8 12h3M8 16h3"/>',
    check: '<path d="m5 12 5 5L20 7"/>',
    up: '<path d="m6 15 6-6 6 6"/>', down: '<path d="m6 9 6 6 6-6"/>',
    globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    send: '<path d="M4 12 20 4l-6 16-3-7z"/>',
    shield: '<path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z"/>',
    news: '<path d="M4 5h13v14H6a2 2 0 0 1-2-2zM17 9h3v8a2 2 0 0 1-2 2"/><path d="M8 9h5M8 13h5M8 17h3"/>',
    book: '<path d="M4 4h6a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H4zM20 4h-6a3 3 0 0 0-3 3"/><path d="M20 4v14h-7"/>',
    filter: '<path d="M4 5h16l-6 7v6l-4 2v-8z"/>',
    pin: '<path d="M12 21s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/>',
    ig: '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".5"/>',
    yt: '<rect x="2" y="5" width="20" height="14" rx="4"/><path d="m10 9 5 3-5 3z"/>',
    xlogo: '<path d="M4 4l16 16M20 4 4 20"/>',
    in: '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 10v7M8 7v.01M12 17v-4a2 2 0 0 1 4 0v4M12 10v7"/>',
  };
  const icon = (n, cls = '') => `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${P[n] || ''}</svg>`;

  // ---------- formatters ----------
  const fmtP = (a, v = a.p) => {
    if (a.y) return v.toFixed(3) + '%';
    const d = v >= 1000 ? 2 : v >= 10 ? 2 : v >= 1 ? 4 : 4;
    return (a.c === 'currencies' || a.c === 'indices' || a.c === 'bonds' ? '' : (a.x === 'XETRA' ? '€' : '$')) + v.toLocaleString('en-US', { minimumFractionDigits: a.c === 'currencies' ? 4 : d, maximumFractionDigits: a.c === 'currencies' ? 4 : d });
  };
  const fmtC = (v, bps) => bps ? `${v > 0 ? '+' : ''}${(v * 1).toFixed(1)} bp` : `${v > 0 ? '+' : v < 0 ? '−' : ''}${Math.abs(v).toFixed(2)}%`;
  const cls = v => v > 0 ? 'up' : v < 0 ? 'down' : 'muted';
  const cap = b => b == null ? '—' : b >= 1000 ? `$${(b / 1000).toFixed(2)}T` : `$${b}B`;
  const logo = (a, size = '') => { const t = a.s.length > 4 ? a.s.slice(0, 3) : a.s; return `<span class="logo ${size} ${t.length === 4 && !size ? 'l4' : ''}" style="background:${a.logo}">${t}</span>`; };
  const href = a => `asset.html?s=${a.s}`;

  // ---------- brand ----------
  const mark = `<svg class="brand-mark" viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" fill="#000"/><path d="M0 31 11 24.5l7 4.5 10-10 12 6.5V40H0z" fill="#1e1e21"/><path d="M0 28 11 21.5l7 4.5 10-10 12 6.5" fill="none" stroke="#FF7A1A" stroke-width="4"/></svg>`;
  const brand = `<a class="brand" href="index.html" aria-label="Investedia home">${mark}<b>Invested<span class="i">i</span>a</b></a>`;

  // ---------- header ----------
  // Mega-menu content per market category: link columns + popular assets
  const MENU = {
    stocks: { cols: [
      ['Discover', [['Stock Screener', 'screener.html'], ['Trending Stocks', 'stocks.html#trending'], ['Stocks Picked by AI', 'ai-insights.html#picks'], ['Most Active', 'stocks.html#active'], ['Top Gainers', 'stocks.html#gainers'], ['Top Losers', 'stocks.html#losers']]],
      ['Opportunities', [['Undervalued Stocks', 'screener.html?preset=undervalued'], ['Overvalued Stocks', 'screener.html?preset=overvalued'], ['52-Week Highs', 'screener.html?preset=highs'], ['52-Week Lows', 'screener.html?preset=lows'], ['Top Bank Stocks', 'screener.html?preset=banks'], ['Renewable Energy Stocks', 'screener.html?preset=renewable']]],
      ['Markets and events', [['United States', 'stocks.html#region-us'], ['Americas', 'stocks.html#region-americas'], ['Europe', 'stocks.html#region-europe'], ['Pre-Market', 'stocks.html#premarket'], ['After Hours', 'stocks.html#afterhours'], ['Earnings Calendar', 'calendar.html#earnings'], ['World ADRs', 'stocks.html#adrs']]],
    ], pop: ['AAPL', 'TSLA', 'META', 'AMZN', 'MSFT', 'NVDA', 'NFLX', 'AMD', 'BA', 'GME'] },
    indices: { cols: [
      ['Indices', [['Major Indices', 'indices.html#major'], ['Real-Time Indices', 'indices.html#realtime'], ['World Indices', 'indices.html#world'], ['Global Indices', 'indices.html#global']]],
      ['Futures', [['Indices Futures', 'indices.html#futures'], ['Dow Jones Futures', 'asset.html?s=YM1'], ['S&P 500 Futures', 'asset.html?s=ES1'], ['Nasdaq Futures', 'asset.html?s=NQ1']]],
    ], pop: ['SPX', 'DJI', 'NDX', 'DAX', 'UKX', 'SX5E', 'NKY'] },
    crypto: { cols: [
      ['Explore', [['Crypto Overview', 'crypto.html'], ['Trending Crypto', 'crypto.html#trending'], ['Crypto Screener', 'crypto.html#all'], ['Top Gainers', 'crypto.html#gainers'], ['Top Losers', 'crypto.html#losers']]],
      ['Market data', [['Most Active', 'crypto.html#active'], ['Crypto Market Cap', 'crypto.html#marketcap'], ['Bitcoin Dominance', 'crypto.html#dominance'], ['DeFi', 'crypto.html#defi'], ['Stablecoins', 'crypto.html#stablecoins']]],
    ], pop: ['BTC', 'ETH', 'SOL', 'XRP', 'BNB', 'DOGE'] },
    currencies: { cols: [
      ['Pairs', [['Major Pairs', 'currencies.html#major'], ['Minor Pairs', 'currencies.html#minor'], ['Exotic Pairs', 'currencies.html#exotic'], ['Currency Converter', 'converter.html']]],
      ['Analytics', [['Currency Heatmap', 'currencies.html#heatmap'], ['Currency Strength', 'currencies.html#strength'], ['Forex Volatility', 'currencies.html#volatility'], ['Economic Events', 'calendar.html']]],
    ], pop: ['EURUSD', 'GBPUSD', 'USDJPY', 'EURGBP', 'AUDUSD'] },
    commodities: { cols: [
      ['Energy', [['Crude Oil', 'asset.html?s=WTI'], ['Brent Oil', 'asset.html?s=BRENT'], ['Natural Gas', 'asset.html?s=NG']]],
      ['Metals', [['Gold', 'asset.html?s=XAU'], ['Silver', 'asset.html?s=XAG'], ['Copper', 'asset.html?s=HG'], ['Platinum', 'asset.html?s=PL']]],
      ['Agriculture', [['Wheat', 'asset.html?s=ZW'], ['Corn', 'asset.html?s=ZC'], ['Coffee', 'asset.html?s=KC'], ['Soybeans', 'asset.html?s=ZS']]],
    ], pop: ['XAU', 'WTI', 'XAG', 'NG', 'HG'] },
    bonds: { cols: [
      ['Government', [['Government Bonds', 'bonds.html#government'], ['US Treasuries', 'bonds.html#treasuries'], ['European Bonds', 'bonds.html#europe'], ['UK Gilts', 'bonds.html#gilts']]],
      ['Corporate & yields', [['Corporate Bonds', 'bonds.html#corporate'], ['High-Yield Bonds', 'asset.html?s=USHY'], ['US 10-Year Yield', 'asset.html?s=US10Y'], ['US 2-Year Yield', 'asset.html?s=US02Y'], ['Yield Curve', 'bonds.html#curve']]],
    ], pop: ['US10Y', 'US02Y', 'US30Y', 'DE10Y', 'UK10Y'] },
    funds: { cols: [
      ['Fund types', [['ETFs', 'funds.html#etfs'], ['Mutual Funds', 'funds.html#mutual'], ['Index Funds', 'funds.html#index'], ['Dividend ETFs', 'funds.html#dividend']]],
      ['Discover', [['Top ETFs', 'funds.html#top'], ['Trending ETFs', 'funds.html#trending'], ['ETF Screener', 'funds.html#all'], ['Fund Comparison', 'compare.html?type=funds'], ['Fund Flows', 'funds.html#flows']]],
    ], pop: ['SPY', 'VOO', 'QQQ', 'VTI', 'SCHD', 'IBIT'] },
  };
  const megaPanel = k => {
    const m = MENU[k], c = M.categories.find(x => x.k === k);
    return `<div class="mega-panel" data-panel="${k}" ${k === 'stocks' ? '' : 'hidden'}>
      <div class="mega-cols" style="grid-template-columns:repeat(${m.cols.length},minmax(0,1fr))">${m.cols.map(([h, links]) => `<div><h6>${h}</h6>${links.map(([t, u]) => `<a class="mega-link" role="menuitem" href="${u}">${t}</a>`).join('')}</div>`).join('')}</div>
      <div class="mega-pop"><h6>Popular ${c.t.toLowerCase()}</h6>${m.pop.map(s => M.bySym[s]).map(a => `<a class="dd-row" href="${href(a)}"><span class="ident">${logo(a)}<span><b>${a.c === 'indices' ? a.n : a.s}</b><small>${a.c === 'indices' ? a.x : a.n}</small></span></span><span class="num">${fmtP(a)}</span><span class="num ${cls(a.d)}">${fmtC(a.d, a.y)}</span></a>`).join('')}</div>
      <div class="dd-foot"><span class="preview-flag"><i></i>Illustrative data</span><a href="${c.page}">Open ${c.t} overview →</a></div>
    </div>`;
  };
  const megaMarkets = `<div class="dd dd-mega" id="dd-markets" role="menu">
    <div class="mega-rail" role="tablist">${M.categories.map((c, i) => `<a class="mega-cat" href="${c.page}" data-cat="${c.k}" ${i === 0 ? 'aria-current="true"' : ''}><span class="dd-ic">${icon(c.k)}</span><span><b>${c.t}</b><small>${c.d}</small></span><svg class="mega-arr" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m9 6 6 6-6 6"/></svg></a>`).join('')}
      <a class="mega-all" href="markets.html">All markets overview →</a></div>
    <div class="mega-body">${M.categories.map(c => megaPanel(c.k)).join('')}</div>
  </div>`;
  const tools = [
    ['screener', 'Stock Screener', 'Filter thousands of stocks by any metric', 'screener.html'],
    ['calendar', 'Economic Calendar', 'Rate decisions, jobs, inflation', 'calendar.html'],
    ['earnings', 'Earnings Calendar', 'Who reports this week', 'calendar.html#earnings'],
    ['indices', 'Stock Comparison', 'Compare up to four stocks side by side', 'compare.html'],
    ['compound', 'Compound Interest', 'Project long-term growth', 'calculator.html#compound'],
    ['calc', 'Investment Returns', 'Annualised return on any investment', 'calculator.html#returns'],
    ['funds', 'Dividend Calculator', 'Income from dividends and reinvesting', 'calculator.html#dividend'],
    ['currencies', 'Currency Converter', '160+ currencies at sample rates', 'converter.html'],
    ['stocks', 'POV Calculator', '“What if I had invested…”', 'calculator.html#pov'],
    ['heat', 'Market Heatmaps', 'Every sector at a glance', 'stocks.html#heatmap'],
  ];
  const ddTools = `<div class="dd dd-tools" id="dd-tools" role="menu">${tools.map(([i, t, d, h]) => `<a class="dd-item" role="menuitem" href="${h}"><span class="dd-ic">${icon(i)}</span><span><b>${t}</b><small>${d}</small></span></a>`).join('')}</div>`;
  const nav = [
    ['home', 'Home', 'index.html'],
    ['dashboard', 'Dashboard', 'dashboard.html'],
    ['markets', 'Markets', null, megaMarkets],
    ['news', 'News', 'news.html'],
    ['analysis', 'Analysis', 'analysis.html'],
    ['ai', 'AI Insights', 'ai-insights.html', null, true],
    ['tools', 'Tools', null, ddTools],
    ['realestate', 'Real Estate', 'real-estate.html'],
  ];
  const hdr = document.createElement('header');
  hdr.className = 'hdr';
  hdr.innerHTML = `<div class="wrap">${brand}
    <ul class="nav">${nav.map(([k, t, h, dd, isNew]) => dd
      ? `<li><button class="nav-link" type="button" aria-expanded="false" aria-haspopup="true" data-dd="dd-${k}" ${page === k || (k === 'tools' && ['screener', 'calendar', 'calc', 'compare', 'converter'].includes(page)) ? 'aria-current="page"' : ''}>${t}${icon('chev', 'chev')}</button>${dd}</li>`
      : `<li><a class="nav-link" href="${h}" ${page === k ? 'aria-current="page"' : ''}>${t}${isNew ? '<span class="badge-new">NEW</span>' : ''}</a></li>`).join('')}</ul>
    <div class="hdr-tools">
      <button class="search-btn" type="button" data-search aria-label="Search markets">${icon('search')}<span>Search markets, news…</span><kbd>⌘K</kbd></button>
      <a class="icon-btn hide-sm" href="watchlist.html" aria-label="Watchlist" title="Watchlist">${icon('star')}</a>
      <div class="notif-wrap hide-sm"><button class="icon-btn" type="button" id="notif-btn" aria-label="Notifications" aria-expanded="false" aria-haspopup="true" title="Notifications">${icon('bell')}<span class="dot" id="notif-dot"></span></button>
        <div class="dd notif-dd" id="notif-dd" role="dialog" aria-label="Notifications"></div></div>
      <a class="avatar hide-sm" id="hdr-avatar" href="profile.html" aria-label="Your profile" title="Your profile">AK</a>
      <button class="icon-btn" type="button" id="theme-btn" aria-label="Switch light or dark mode" title="Light / dark mode"></button>
      <button class="icon-btn menu-toggle" type="button" aria-label="Open menu" aria-expanded="false">${icon('menu')}</button>
    </div></div>`;
  document.body.prepend(hdr);
  // profile (stored on this device until accounts exist)
  const getProfile = () => { try { return JSON.parse(localStorage.getItem('inv-profile') || '{}'); } catch { return {}; } };
  const paintAvatar = () => { const pr = getProfile(), av = hdr.querySelector('#hdr-avatar'), ini = (pr.name || 'AK').split(/\s+/).map(w => w[0]).join('').slice(0, 2).toUpperCase(); av.innerHTML = pr.photo ? `<img src="${pr.photo}" alt="">` : ini; };
  paintAvatar(); window.addEventListener('profile-change', paintAvatar);
  // notifications panel (sample items; settings live on the profile page)
  const NOTIFS = [['news', 'Breaking', 'Fed officials signal no rush to cut rates after hot inflation data', '4 min ago', 'article.html'], ['watch', 'Watchlist', 'NVDA fell 1.84% today. Profit-taking after a 9% two-week run', '1 h ago', 'asset.html?s=NVDA'], ['earn', 'Earnings', 'Tesla reports on Wed 22 Oct after the close', '3 h ago', 'calendar.html#earnings'], ['event', 'Economic event', 'US Retail Sales at 08:30 ET tomorrow. Forecast 0.4%', '5 h ago', 'calendar.html'], ['price', 'Price alert', 'Gold moved more than 2% in a day', 'Yesterday', 'asset.html?s=XAU']];
  const nIcon = { news: 'news', watch: 'star', earn: 'earnings', event: 'calendar', price: 'bell' };
  let readN = 0; try { readN = +localStorage.getItem('inv-notif-read') || 0; } catch {}
  const nb = hdr.querySelector('#notif-btn'), nd = hdr.querySelector('#notif-dd');
  const paintNotif = () => {
    const unread = Math.max(0, NOTIFS.length - readN);
    hdr.querySelector('#notif-dot').hidden = !unread;
    nd.innerHTML = `<div class="notif-head"><b>Notifications</b>${unread ? `<span class="tag acc">${unread} new</span>` : ''}<button type="button" class="link" id="notif-read" style="background:none;border:0;margin-left:auto">Mark all read</button></div>
      <div class="notif-list">${NOTIFS.map(([k, t, m, time, h], i) => `<a class="notif-item ${i < unread ? 'unread' : ''}" href="${h}"><span class="dd-ic">${icon(nIcon[k])}</span><span><small class="accent">${t}</small><span class="notif-msg">${m}</span><small class="dim">${time}</small></span></a>`).join('')}</div>
      <a class="notif-foot" href="profile.html#notifications">${icon('heat')}Notification settings</a>`;
    nd.querySelector('#notif-read').onclick = e => { e.stopPropagation(); readN = NOTIFS.length; try { localStorage.setItem('inv-notif-read', readN); } catch {} paintNotif(); };
  };
  paintNotif();
  nb.onclick = e => { e.stopPropagation(); const o = !nd.classList.contains('open'); closeAll(); nd.classList.toggle('open', o); nb.setAttribute('aria-expanded', o); };
  document.addEventListener('click', e => { if (!e.target.closest('.notif-wrap')) { nd.classList.remove('open'); nb.setAttribute('aria-expanded', 'false'); } });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') nd.classList.remove('open'); });
  const tb = hdr.querySelector('#theme-btn');
  const sun = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>', moon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>';
  const setTheme = t => { document.documentElement.dataset.theme = t; tb.innerHTML = t === 'light' ? moon : sun; try { localStorage.setItem('inv-theme', t); } catch {} };
  let th = 'dark'; try { th = localStorage.getItem('inv-theme') || 'dark'; } catch {}
  setTheme(th); window.setInvTheme = setTheme; tb.onclick = () => setTheme(document.documentElement.dataset.theme === 'light' ? 'dark' : 'light');
  const skip = document.createElement('a'); skip.className = 'skip'; skip.href = '#main'; skip.textContent = 'Skip to content'; document.body.prepend(skip);
  const onScrollHdr = () => hdr.classList.toggle('scrolled', scrollY > 8); addEventListener('scroll', onScrollHdr, { passive: true }); onScrollHdr();
  document.addEventListener('DOMContentLoaded', () => { const m = document.querySelector('main'); if (m) { m.id = m.id || 'main'; m.classList.add('enter'); } });

  // dropdown behaviour: hover on desktop, click anywhere, Escape closes
  const closeAll = except => hdr.querySelectorAll('[data-dd]').forEach(b => { if (b === except) return; b.setAttribute('aria-expanded', 'false'); document.getElementById(b.dataset.dd).classList.remove('open'); });
  hdr.querySelectorAll('[data-dd]').forEach(btn => {
    const dd = document.getElementById(btn.dataset.dd), li = btn.parentElement;
    const open = v => { closeAll(btn); btn.setAttribute('aria-expanded', v); dd.classList.toggle('open', v); };
    btn.addEventListener('click', () => open(btn.getAttribute('aria-expanded') !== 'true'));
    let t;
    li.addEventListener('mouseenter', () => { if (matchMedia('(hover:hover)').matches) { clearTimeout(t); open(true); } });
    li.addEventListener('mouseleave', () => { if (matchMedia('(hover:hover)').matches) t = setTimeout(() => open(false), 120); });
  });
  const rail = hdr.querySelectorAll('.mega-cat');
  const pick = k => { rail.forEach(r => r.toggleAttribute('aria-current', r.dataset.cat === k)); hdr.querySelectorAll('.mega-panel').forEach(p => p.hidden = p.dataset.panel !== k); };
  rail.forEach(r => { r.addEventListener('mouseenter', () => pick(r.dataset.cat)); r.addEventListener('focus', () => pick(r.dataset.cat)); });
  document.addEventListener('click', e => { if (!e.target.closest('.nav>li')) closeAll(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') { closeAll(); closePalette(); closeDrawer(); } });

  // mobile drawer
  const drawer = document.createElement('div');
  drawer.className = 'drawer';
  drawer.innerHTML = `<button class="search-btn" type="button" data-search>${icon('search')}<span>Search markets, news…</span></button>
    <a href="index.html">Home</a><a href="dashboard.html">Dashboard</a>
    <details><summary>Markets ${icon('chev')}</summary><a href="markets.html">All markets</a>${M.categories.map(c => `<a href="${c.page}">${c.t}</a>`).join('')}</details>
    <a href="news.html">News</a><a href="analysis.html">Analysis</a><a href="ai-insights.html">AI Insights <span class="badge-new">NEW</span></a>
    <details><summary>Tools ${icon('chev')}</summary>${tools.map(([, t, , h]) => `<a href="${h}">${t}</a>`).join('')}</details>
    <a href="real-estate.html">Real Estate <span class="tag">Soon</span></a><a href="watchlist.html">Watchlist</a><a href="profile.html">Profile &amp; notifications</a>`;
  hdr.after(drawer);
  const mt = hdr.querySelector('.menu-toggle');
  function closeDrawer() { drawer.classList.remove('open'); mt.setAttribute('aria-expanded', 'false'); mt.innerHTML = icon('menu'); document.body.style.overflow = ''; }
  mt.onclick = () => { const o = !drawer.classList.contains('open'); drawer.classList.toggle('open', o); mt.setAttribute('aria-expanded', o); mt.innerHTML = icon(o ? 'x' : 'menu'); document.body.style.overflow = o ? 'hidden' : ''; };

  // ---------- search palette (UI only, searches sample data) ----------
  const pal = document.createElement('div');
  pal.className = 'palette'; pal.hidden = true;
  pal.innerHTML = `<div class="palette-box" role="dialog" aria-label="Search"><div class="palette-in">${icon('search')}<input id="pal-q" placeholder="Search stocks, crypto, indices, news…" autocomplete="off"><kbd>Esc</kbd></div><div class="palette-list" id="pal-list"></div></div>`;
  document.body.append(pal);
  const q = pal.querySelector('#pal-q'), list = pal.querySelector('#pal-list');
  function renderPal() {
    const s = q.value.trim().toLowerCase();
    const hits = M.assets.filter(a => !s || a.s.toLowerCase().includes(s) || a.n.toLowerCase().includes(s)).slice(0, s ? 8 : 6);
    const nh = M.news.filter(n => s && n.t.toLowerCase().includes(s)).slice(0, 3);
    list.innerHTML = `<h6>${s ? 'Markets' : 'Trending'}</h6>` + (hits.length ? hits.map((a, i) => `<a class="pal-item" href="${href(a)}" ${i === 0 ? 'aria-selected="true"' : ''}><span>${logo(a)}</span><span class="ident"><span><b>${a.s}</b><small>${a.n} · ${a.x}</small></span></span><span class="num">${fmtP(a)}</span><span class="num ${cls(a.d)}">${fmtC(a.d, a.y)}</span></a>`).join('') : `<div class="pal-item muted">No markets match “${q.value}”.</div>`)
      + (nh.length ? `<h6>News</h6>` + nh.map(n => `<a class="pal-item" href="article.html" style="grid-template-columns:auto 1fr"><span class="dd-ic" style="width:28px;height:28px">${icon('news')}</span><span>${n.t}</span></a>`).join('') : '');
  }
  function openPalette() { closeDrawer(); pal.hidden = false; q.value = ''; renderPal(); setTimeout(() => q.focus(), 10); }
  function closePalette() { pal.hidden = true; }
  q.oninput = renderPal;
  q.onkeydown = e => { if (e.key === 'Enter') { const a = list.querySelector('a'); if (a) location.href = a.href; } };
  pal.onclick = e => { if (e.target === pal) closePalette(); };
  document.querySelectorAll('[data-search]').forEach(b => b.onclick = openPalette);
  document.addEventListener('keydown', e => { if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); openPalette(); } });

  // ---------- ticker ----------
  const tickSyms = ['SPX', 'NDX', 'DJI', 'BTC', 'ETH', 'NVDA', 'AAPL', 'MSFT', 'AMZN', 'TSLA', 'XAU', 'WTI', 'EURUSD', 'US10Y', 'DAX', 'NKY'];
  const tk = document.createElement('div');
  tk.className = 'ticker'; tk.setAttribute('aria-label', 'Market ticker');
  const items = tickSyms.map(s => M.bySym[s]).map(a => `<a class="tk" href="${href(a)}"><b>${a.c === 'indices' ? a.n : a.s}</b><span class="num">${fmtP(a)}</span><span class="num ${cls(a.d)}">${fmtC(a.d, a.y)}</span></a>`).join('');
  tk.innerHTML = `<div class="ticker-track">${items}${items}</div>`;
  drawer.after(tk);

  // ---------- footer ----------
  const ftr = document.createElement('footer');
  ftr.className = 'ftr';
  ftr.innerHTML = `<div class="wrap"><div class="ftr-top">
    <div>${brand}<p class="muted" style="margin:14px 0 0;max-width:34ch">Markets, news and tools for people who want to understand their money.</p>
      <div class="socials"><a class="icon-btn" href="https://www.instagram.com/investedia/" aria-label="Instagram">${icon('ig')}</a></div></div>
    <div><h6>Markets</h6><ul>${M.categories.map(c => `<li><a href="${c.page}">${c.t}</a></li>`).join('')}</ul></div>
    <div><h6>Content</h6><ul><li><a href="news.html">News</a></li><li><a href="analysis.html">Analysis</a></li><li><a href="ai-insights.html">AI Insights</a></li><li><a href="real-estate.html">Real Estate</a></li></ul></div>
    <div><h6>Tools</h6><ul>${tools.map(([, t, , h]) => `<li><a href="${h}">${t}</a></li>`).join('')}</ul></div>
    <div><h6>Company</h6><ul><li><a href="about.html">About</a></li><li><a href="about.html#careers">Careers</a></li><li><a href="about.html#advertise">Advertise</a></li><li><a href="about.html#contact">Contact</a></li><li><a href="about.html#terms">Terms & privacy</a></li></ul></div>
  </div>
  <div class="partner"><span class="dim">In partnership with</span><a href="about.html#partners"><b>Guidify</b></a><span class="dim">· growth partner for Shopify brands</span></div>
  <div class="ftr-bottom"><span>© 2026 Investedia. For information and education only, not investment advice.</span><span class="preview-flag"><i></i>Design preview · all market figures are illustrative demo data</span></div></div>`;
  document.addEventListener('DOMContentLoaded', () => document.body.append(ftr));

  // ---------- charts ----------
  // Sparkline as an inline SVG string
  function spark(vals, color, w = 96, h = 28, fill = true) {
    const mn = Math.min(...vals), mx = Math.max(...vals), r = mx - mn || 1;
    const pts = vals.map((v, i) => [i / (vals.length - 1) * w, h - 2 - (v - mn) / r * (h - 4)]);
    const d = pts.map((p, i) => (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join('');
    const id = 'g' + Math.random().toString(36).slice(2, 8);
    return `<svg class="spark" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" aria-hidden="true">${fill ? `<defs><linearGradient id="${id}" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="${color}" stop-opacity=".22"/><stop offset="1" stop-color="${color}" stop-opacity="0"/></linearGradient></defs><path d="${d}L${w} ${h}L0 ${h}Z" fill="url(#${id})"/>` : ''}<path d="${d}" fill="none" stroke="${color}" stroke-width="1.5" vector-effect="non-scaling-stroke" stroke-linejoin="round"/></svg>`;
  }
  const colorFor = v => v >= 0 ? '#22C55E' : '#F04444';

  // Full area chart with axes, crosshair and tooltip
  function areaChart(el, vals, opts = {}) {
    const { color = '#FF7A1A', labels, fmt = v => v.toFixed(2), height = 320, compare } = opts;
    el.classList.add('chart'); el.style.height = height + 'px';
    const draw = () => {
      const W = el.clientWidth, H = height, padL = 8, padR = 64, padT = 12, padB = 28;
      const all = compare ? vals.concat(compare) : vals;
      let mn = Math.min(...all), mx = Math.max(...all); const pad = (mx - mn) * .08 || 1; mn -= pad; mx += pad;
      const sx = i => padL + i / (vals.length - 1) * (W - padL - padR), sy = v => padT + (1 - (v - mn) / (mx - mn)) * (H - padT - padB);
      const ticks = 5, grid = [];
      for (let k = 0; k <= ticks; k++) { const v = mn + (mx - mn) * k / ticks; grid.push(`<line class="grid-l" x1="${padL}" x2="${W - padR}" y1="${sy(v)}" y2="${sy(v)}"/><text class="ax" x="${W - padR + 10}" y="${sy(v) + 4}">${fmt(v)}</text>`); }
      const xl = labels ? labels.map((l, k) => { const i = Math.round(k / (labels.length - 1) * (vals.length - 1)); return `<text class="ax" x="${sx(i)}" y="${H - 8}" text-anchor="${k === 0 ? 'start' : k === labels.length - 1 ? 'end' : 'middle'}">${l}</text>`; }).join('') : '';
      const path = vals.map((v, i) => (i ? 'L' : 'M') + sx(i).toFixed(1) + ' ' + sy(v).toFixed(1)).join('');
      const cpath = compare ? compare.map((v, i) => (i ? 'L' : 'M') + sx(i).toFixed(1) + ' ' + sy(v).toFixed(1)).join('') : '';
      const id = 'a' + Math.random().toString(36).slice(2, 8), last = vals[vals.length - 1];
      el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Price chart"><defs><linearGradient id="${id}" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="${color}" stop-opacity=".22"/><stop offset="1" stop-color="${color}" stop-opacity="0"/></linearGradient></defs>
        ${grid.join('')}${xl}
        <path d="${path}L${sx(vals.length - 1)} ${H - padB}L${padL} ${H - padB}Z" fill="url(#${id})"/>
        ${compare ? `<path d="${cpath}" fill="none" stroke="#A1A1AA" stroke-width="1.5" stroke-dasharray="4 4"/>` : ''}
        <path d="${path}" fill="none" stroke="${color}" stroke-width="2" stroke-linejoin="round"/>
        <line class="grid-l" x1="${padL}" x2="${W - padR}" y1="${sy(last)}" y2="${sy(last)}" stroke-dasharray="2 4" style="stroke:${color};opacity:.5"/>
        <rect x="${W - padR + 4}" y="${sy(last) - 10}" width="${padR - 6}" height="20" rx="4" fill="${color}"/><text x="${W - padR + 10}" y="${sy(last) + 4}" font-family="Geist Mono, monospace" font-size="11" font-weight="600" fill="#0A0A0B">${fmt(last)}</text>
        <g class="hover" style="display:none"><line class="xh" y1="${padT}" y2="${H - padB}"/><circle r="4.5" fill="${color}" stroke="#0A0A0B" stroke-width="2"/></g></svg><div class="tip" style="display:none"></div>`;
      const svg = el.querySelector('svg'), g = el.querySelector('.hover'), tip = el.querySelector('.tip');
      svg.addEventListener('pointermove', e => {
        const r = svg.getBoundingClientRect(), x = (e.clientX - r.left) * W / r.width;
        const i = Math.max(0, Math.min(vals.length - 1, Math.round((x - padL) / (W - padL - padR) * (vals.length - 1))));
        g.style.display = ''; g.querySelector('line').setAttribute('x1', sx(i)); g.querySelector('line').setAttribute('x2', sx(i));
        g.querySelector('circle').setAttribute('cx', sx(i)); g.querySelector('circle').setAttribute('cy', sy(vals[i]));
        tip.style.display = ''; tip.style.left = sx(i) / W * 100 + '%'; tip.style.top = sy(vals[i]) + 'px';
        tip.innerHTML = `<b>${fmt(vals[i])}</b>${opts.tipLabel ? `<div class="dim">${opts.tipLabel(i)}</div>` : ''}`;
      });
      svg.addEventListener('pointerleave', () => { g.style.display = 'none'; tip.style.display = 'none'; });
    };
    draw();
    let rt; new ResizeObserver(() => { clearTimeout(rt); rt = setTimeout(draw, 60); }).observe(el);
  }

  // Abstract cover art for news cards (no stock photos): a chart-like composition
  function cover(key, accent = '#FF7A1A') {
    const r = M.seeded(String(key)), vals = M.series(String(key), 40, 100, (r() - .4) * 40, .04);
    const mn = Math.min(...vals), mx = Math.max(...vals);
    const d = vals.map((v, i) => `${i ? 'L' : 'M'}${(i / 39 * 400).toFixed(1)} ${(170 - (v - mn) / (mx - mn) * 120).toFixed(1)}`).join('');
    const bars = Array.from({ length: 40 }, (_, i) => `<rect x="${i * 10 + 2}" y="${200 - r() * 26}" width="6" height="30" fill="#ffffff" opacity=".05"/>`).join('');
    const id = 'c' + Math.random().toString(36).slice(2, 8);
    return `<svg viewBox="0 0 400 200" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><defs><linearGradient id="${id}" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="${accent}" stop-opacity=".28"/><stop offset="1" stop-color="${accent}" stop-opacity="0"/></linearGradient></defs><rect width="400" height="200" fill="#121214"/>${[40, 80, 120, 160].map(y => `<line x1="0" x2="400" y1="${y}" y2="${y}" stroke="#ffffff" stroke-opacity=".04"/>`).join('')}${bars}<path d="${d}L400 200L0 200Z" fill="url(#${id})"/><path d="${d}" fill="none" stroke="${accent}" stroke-width="2.5"/></svg>`;
  }

  // Asset table
  function assetTable(rows, cols = ['price', 'chg', 'week', 'spark']) {
    const H = { price: 'Price', chg: '24h / 1D', week: '1W', cap: 'Market cap', vol: 'Volume', pe: 'P/E', spark: '7 days', aum: 'Assets', fee: 'Fee', sector: 'Sector' };
    return `<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Name</th>${cols.map(c => `<th>${H[c]}</th>`).join('')}<th style="width:40px"></th></tr></thead><tbody>${rows.map(a => `<tr data-href="${href(a)}"><td><a class="ident" href="${href(a)}">${logo(a)}<span><b>${a.s}</b><small>${a.n}</small></span></a></td>${cols.map(c => {
      if (c === 'price') return `<td class="num">${fmtP(a)}${a.unit ? `<span class="dim">${a.unit}</span>` : ''}</td>`;
      if (c === 'chg') return `<td><span class="pill ${cls(a.d)}">${fmtC(a.d, a.y)}</span></td>`;
      if (c === 'week') return `<td class="num ${cls(a.w)}">${fmtC(a.w, a.y)}</td>`;
      if (c === 'cap') return `<td class="num">${cap(a.m)}</td>`;
      if (c === 'vol') return `<td class="num muted">${a.vol || '—'}</td>`;
      if (c === 'pe') return `<td class="num muted">${a.pe ? a.pe.toFixed(1) : '—'}</td>`;
      if (c === 'aum') return `<td class="num muted">${a.aum || '—'}</td>`;
      if (c === 'fee') return `<td class="num muted">${a.fee || '—'}</td>`;
      if (c === 'sector') return `<td class="muted">${a.sector || '—'}</td>`;
      if (c === 'spark') return `<td>${spark(a.spark.slice(-28), colorFor(a.w))}</td>`;
      return '<td></td>';
    }).join('')}<td><button class="star" type="button" aria-label="Add ${a.s} to watchlist">${icon('star')}</button></td></tr>`).join('')}</tbody></table></div>`;
  }
  document.addEventListener('click', e => {
    const st = e.target.closest('.star');
    if (st) { e.stopPropagation(); e.preventDefault(); st.classList.toggle('on'); st.querySelector('svg').setAttribute('fill', st.classList.contains('on') ? 'currentColor' : 'none'); return; }
    const tr = e.target.closest('tr[data-href]');
    if (tr && !e.target.closest('a,button')) location.href = tr.dataset.href;
  });

  // Tabs helper: buttons with data-tab inside a .tabs; calls fn(key)
  function tabs(el, fn) {
    el.setAttribute('role', 'tablist');
    el.querySelectorAll('.tab').forEach(b => { b.setAttribute('role', 'tab'); b.onclick = () => { el.querySelectorAll('.tab').forEach(x => x.setAttribute('aria-selected', x === b)); fn(b.dataset.tab); }; });
  }

  // Compact asset row used in lists (movers, related, mentioned)
  const row = a => `<a class="arow" href="${href(a)}"><span class="ident">${logo(a)}<span><b>${a.c === 'indices' ? a.n : a.s}</b><small>${a.c === 'indices' ? a.x : a.n}</small></span></span><span class="num">${fmtP(a)}</span><span class="pill ${cls(a.d)}">${fmtC(a.d, a.y)}</span></a>`;
  // Impact bars for calendar events
  const impact = n => `<span class="impact" title="${['', 'Low', 'Medium', 'High'][n]} impact">${[1, 2, 3].map(k => `<i style="height:${6 + k * 3}px;background:${k <= n ? (n === 3 ? 'var(--accent)' : 'var(--fg-2)') : 'var(--line)'}"></i>`).join('')}</span>`;
  const sTag = s => `<span class="tag ${s === 'Bullish' ? 'bull' : s === 'Bearish' ? 'bear' : ''}">${s}</span>`;
  const analysisCard = (x, i = 0) => `<a class="card n-card" href="analysis-article.html"><div class="cover">${cover('an' + x.t.length + i, i % 3 === 1 ? '#A1A1AA' : '#FF7A1A')}</div><div class="body"><div class="news-meta"><span class="tag">${x.kind}</span>${sTag(x.sentiment)}${x.tag ? `<span class="mono">${x.tag}</span>` : ''}</div><h3>${x.t}</h3><p>${x.d}</p><div class="news-meta"><span>${x.a}</span><i></i><span>${x.read} min read</span></div></div></a>`;
  // Newsletter band (UI only)
  const late = () => document.querySelectorAll('[data-newsletter]').forEach(el => {
    el.innerHTML = `<div class="panel cta-band ai-glow"><div><span class="eyebrow">The Investedia Brief</span><h2 style="margin-top:10px;font-size:26px">Markets in five minutes, every morning.</h2><p class="lede" style="font-size:15px">The moves that matter, the news behind them and one chart worth your time. Free.</p></div>
      <form class="subscribe" onsubmit="event.preventDefault();this.querySelector('button').textContent='Subscribed ✓'"><input class="input" type="email" placeholder="you@email.com" aria-label="Email address" required><button class="btn btn-primary" type="submit">Subscribe</button>
      <div class="chips" style="display:flex;gap:6px;flex-wrap:wrap;width:100%;margin-top:6px">${['Daily brief', 'Crypto weekly', 'Earnings alerts', 'Real estate monthly'].map((t, i) => `<button type="button" class="chip ${i === 0 ? 'on' : ''}" onclick="this.classList.toggle('on')">${t}</button>`).join('')}</div></form></div>`;
  });
  document.addEventListener('DOMContentLoaded', () => { late(); document.querySelectorAll('[data-icon]').forEach(e => { e.innerHTML = icon(e.dataset.icon); e.style.display = 'inline-flex'; const v = e.querySelector('svg'); v.style.width = v.style.height = '16px'; }); document.querySelectorAll('[data-search]').forEach(b => b.onclick = openPalette); });

  // Category navigation strip shown on every market page
  function subnav(k) {
    const el = document.getElementById('subnav'); if (!el) return;
    el.innerHTML = `<a href="markets.html" ${!k ? 'aria-current="page"' : ''}>Overview</a>` + M.categories.map(c => `<a href="${c.page}" ${c.k === k ? 'aria-current="page"' : ''}>${icon(c.k)}${c.t}</a>`).join('');
  }
  // Treemap-style heatmap from [asset, colSpan, rowSpan]
  const heatColor = d => { const t = Math.min(1, Math.abs(d) / 4); return d >= 0 ? `rgba(34,197,94,${.16 + t * .64})` : `rgba(240,68,68,${.16 + t * .64})`; };
  function heatmap(el, items) { el.innerHTML = items.map(([a, w, h]) => `<a href="${a.n && M.bySym[a.s] ? href(a) : 'screener.html'}" style="grid-column:span ${w};grid-row:span ${h};background:${heatColor(a.d)}" title="${a.n || a.s}: ${fmtC(a.d)}"><b style="font-size:${Math.min(22, 10 + w * 2)}px">${a.label || a.s}</b><span>${fmtC(a.d)}</span></a>`).join(''); }
  function heatLegend(el) { el.className = 'heat-legend'; el.innerHTML = [-4, -3, -2, -1, 0, 1, 2, 3, 4].map(v => `<span style="background:${v === 0 ? '#29292D' : heatColor(v)}">${v > 0 ? '+' : ''}${v}%</span>`).join(''); }
  // Diverging bar row (sectors, strength)
  const divBar = (n, v, mx = 2, suffix) => `<div class="divbar"><span class="muted">${n}</span><div class="divbar-track"><i class="mid"></i><i class="bar" style="${v >= 0 ? `left:50%;width:${v / mx * 50}%;background:var(--up)` : `right:50%;width:${-v / mx * 50}%;background:var(--down)`}"></i></div><span class="num ${cls(v)}">${suffix ? (v > 0 ? '+' : '') + v.toFixed(1) + suffix : fmtC(v)}</span></div>`;
  // Email sign-up pop-up
  const pop = document.createElement('div');
  pop.className = 'palette'; pop.hidden = true;
  pop.innerHTML = `<div class="palette-box pop" role="dialog" aria-modal="true" aria-labelledby="pop-t">
    <button class="icon-btn pop-x" type="button" aria-label="Close">${icon('x')}</button>
    <div class="pop-art">${mark}</div>
    <span class="eyebrow">The Investedia Brief</span>
    <h2 id="pop-t" style="margin:10px 0 6px;font-size:24px">Markets in five minutes, every morning.</h2>
    <p class="muted" style="margin:0 0 18px">Join the list for the daily brief, weekly charts and early access to new dashboard features. Free, unsubscribe anytime.</p>
    <form class="subscribe" id="pop-f"><input class="input" type="email" id="pop-email" placeholder="you@email.com" aria-label="Email address" required><button class="btn btn-primary" type="submit">Join free</button></form>
    <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:12px">${['Daily brief', 'Weekly charts', 'Crypto', 'Product updates'].map((t, i) => `<button type="button" class="chip ${i < 2 ? 'on' : ''}" onclick="this.classList.toggle('on')">${t}</button>`).join('')}</div>
    <p class="pop-ok up" hidden style="margin:14px 0 0;font-weight:550">You’re on the list. Check your inbox to confirm.</p>
  </div>`;
  const store = (k, v) => { try { return v === undefined ? localStorage.getItem(k) : localStorage.setItem(k, v); } catch { return null; } };
  const openPop = () => { pop.hidden = false; store('inv-pop', '1'); setTimeout(() => pop.querySelector('input').focus(), 30); };
  const closePop = () => { pop.hidden = true; };
  pop.querySelector('.pop-x').onclick = closePop;
  pop.onclick = e => { if (e.target === pop) closePop(); };
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closePop(); });
  pop.querySelector('#pop-f').onsubmit = e => { e.preventDefault(); store('inv-sub', '1'); pop.querySelector('#pop-f').hidden = true; pop.querySelector('.pop-ok').hidden = false; setTimeout(closePop, 2200); };
  document.addEventListener('DOMContentLoaded', () => {
    document.body.append(pop);
    document.querySelectorAll('[data-subscribe]').forEach(b => b.onclick = openPop);
    if (!store('inv-pop') && !store('inv-sub')) {
      const t = setTimeout(openPop, 12000);
      const onScroll = () => { if (scrollY > (document.body.scrollHeight - innerHeight) * .6) { clearTimeout(t); removeEventListener('scroll', onScroll); if (!store('inv-pop')) openPop(); } };
      addEventListener('scroll', onScroll, { passive: true });
    }
  });
  // Deep links: #hash selects a tab (routes = { hash: [tabsId, tabKey] }) or scrolls to an element id
  function routeHash(routes = {}) {
    const go = () => {
      const h = decodeURIComponent(location.hash.slice(1)); if (!h) return;
      const r = routes[h];
      if (r) { const t = document.getElementById(r[0]); const b = t && t.querySelector(`[data-tab="${r[1]}"]`); if (b) { b.click(); (t.closest('section') || t).scrollIntoView({ block: 'start' }); } }
      else { const el = document.getElementById(h); if (el) el.scrollIntoView({ block: 'start' }); }
    };
    addEventListener('hashchange', go); setTimeout(go, 60);
  }
  // Pro chart: candles / line / area with volume pane, moving averages and crosshair readout
  function proChart(el, bars, opts = {}) {
    const { type = 'candles', height = 460, labels = [], sma = [], volume = true, fmt = v => v.toFixed(2), onHover, upCol = upCol, downCol = downCol, lineCol = '#FF7A1A' } = opts;
    el.classList.add('chart'); el.style.height = height + 'px';
    const avg = (k) => bars.map((_, i) => i < k - 1 ? null : bars.slice(i - k + 1, i + 1).reduce((s, b) => s + b.c, 0) / k);
    const draw = () => {
      const W = el.clientWidth, H = height, padL = 4, padR = 68, padT = 10, volH = volume ? H * .18 : 0, padB = 26;
      const pH = H - padT - padB - volH - (volume ? 8 : 0);
      let mn = Math.min(...bars.map(b => b.l)), mx = Math.max(...bars.map(b => b.h)); const pd = (mx - mn) * .06; mn -= pd; mx += pd;
      const n = bars.length, step = (W - padL - padR) / n, bw = Math.max(1, step * .64);
      const sx = i => padL + step * i + step / 2, sy = v => padT + (1 - (v - mn) / (mx - mn)) * pH;
      const vmax = Math.max(...bars.map(b => b.v)), vy0 = padT + pH + 8 + volH;
      let g = '';
      for (let k = 0; k <= 5; k++) { const v = mn + (mx - mn) * k / 5; g += `<line class="grid-l" x1="${padL}" x2="${W - padR}" y1="${sy(v)}" y2="${sy(v)}"/><text class="ax" x="${W - padR + 8}" y="${sy(v) + 4}">${fmt(v)}</text>`; }
      g += labels.map((l, k) => { const i = Math.round(k / Math.max(1, labels.length - 1) * (n - 1)); return `<text class="ax" x="${sx(i)}" y="${H - 8}" text-anchor="${k === 0 ? 'start' : k === labels.length - 1 ? 'end' : 'middle'}">${l}</text>`; }).join('');
      let body = '';
      if (volume) body += bars.map((b, i) => `<rect x="${sx(i) - bw / 2}" y="${vy0 - b.v / vmax * volH}" width="${bw}" height="${b.v / vmax * volH}" fill="${b.c >= b.o ? upCol : downCol}" opacity=".28"/>`).join('');
      if (type === 'candles') body += bars.map((b, i) => { const up = b.c >= b.o, col = up ? upCol : downCol, y1 = sy(Math.max(b.o, b.c)), y2 = sy(Math.min(b.o, b.c)); return `<line x1="${sx(i)}" x2="${sx(i)}" y1="${sy(b.h)}" y2="${sy(b.l)}" stroke="${col}" stroke-width="1"/><rect x="${sx(i) - bw / 2}" y="${y1}" width="${bw}" height="${Math.max(1, y2 - y1)}" fill="${up ? col : col}" ${up ? 'fill-opacity=".9"' : ''} rx="${bw > 4 ? 1 : 0}"/>`; }).join('');
      else { const d = bars.map((b, i) => (i ? 'L' : 'M') + sx(i).toFixed(1) + ' ' + sy(b.c).toFixed(1)).join(''); const id = 'p' + Math.random().toString(36).slice(2, 7);
        body += (type === 'area' ? `<defs><linearGradient id="${id}" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="${lineCol}" stop-opacity=".25"/><stop offset="1" stop-color="${lineCol}" stop-opacity="0"/></linearGradient></defs><path d="${d}L${sx(n - 1)} ${padT + pH}L${sx(0)} ${padT + pH}Z" fill="url(#${id})"/>` : '') + `<path d="${d}" fill="none" stroke="${lineCol}" stroke-width="2" stroke-linejoin="round"/>`; }
      const maCol = { 20: '#38BDF8', 50: '#A78BFA', 200: '#F472B6' };
      sma.forEach(k => { const a = avg(k); body += `<path d="${a.map((v, i) => v == null ? '' : (a[i - 1] == null ? 'M' : 'L') + sx(i).toFixed(1) + ' ' + sy(v).toFixed(1)).join('')}" fill="none" stroke="${maCol[k] || '#fff'}" stroke-width="1.4" opacity=".9"/>`; });
      const last = bars[n - 1], lc = last.c >= last.o ? upCol : downCol;
      body += `<line x1="${padL}" x2="${W - padR}" y1="${sy(last.c)}" y2="${sy(last.c)}" stroke="${lc}" stroke-dasharray="2 3" opacity=".7"/><rect x="${W - padR + 3}" y="${sy(last.c) - 10}" width="${padR - 5}" height="20" rx="4" fill="${lc}"/><text x="${W - padR + 8}" y="${sy(last.c) + 4}" font-family="Geist Mono,monospace" font-size="11" font-weight="600" fill="#0A0A0B">${fmt(last.c)}</text>`;
      el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Price chart">${g}${body}<g class="hover" style="display:none"><line class="xh" y1="${padT}" y2="${H - padB}"/><line class="xh yh" x1="${padL}" x2="${W - padR}"/><rect class="ytag" x="${W - padR + 3}" width="${padR - 5}" height="20" rx="4" fill="#3f3f46"/><text class="ytxt" x="${W - padR + 8}" font-family="Geist Mono,monospace" font-size="11" fill="#fff"></text></g></svg>`;
      const svg = el.querySelector('svg'), hv = el.querySelector('.hover');
      svg.addEventListener('pointermove', e => {
        const r = svg.getBoundingClientRect(), x = (e.clientX - r.left) * W / r.width, y = (e.clientY - r.top) * H / r.height;
        const i = Math.max(0, Math.min(n - 1, Math.floor((x - padL) / step)));
        hv.style.display = ''; const [vx, hy] = hv.querySelectorAll('line');
        vx.setAttribute('x1', sx(i)); vx.setAttribute('x2', sx(i)); const yy = Math.max(padT, Math.min(padT + pH, y)); hy.setAttribute('y1', yy); hy.setAttribute('y2', yy);
        hv.querySelector('.ytag').setAttribute('y', yy - 10); const t = hv.querySelector('.ytxt'); t.setAttribute('y', yy + 4); t.textContent = fmt(mn + (1 - (yy - padT) / pH) * (mx - mn));
        onHover && onHover(bars[i], i);
      });
      svg.addEventListener('pointerleave', () => { hv.style.display = 'none'; onHover && onHover(null); });
    };
    draw();
    let rt; new ResizeObserver(() => { clearTimeout(rt); rt = setTimeout(draw, 60); }).observe(el);
  }
  window.UI = { icon, fmtP, fmtC, cls, cap, logo, href, spark, colorFor, areaChart, cover, assetTable, tabs, row, impact, sTag, analysisCard, routeHash, subnav, heatmap, heatLegend, heatColor, divBar, proChart };
})();
