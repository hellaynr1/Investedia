// Markets page: sector heatmap (tile size = articles in 7 days, colour = price move of the sector fund), plus indices, commodities, crypto.
(() => {
  const $ = id => document.getElementById(id);
  const WIN = [['d', 'Today'], ['w', 'Week'], ['m', 'Month']];
  const VIEW = [['sec', 'Sectors'], ['idx', 'Indices'], ['cmd', 'Commodities'], ['cry', 'Crypto & FX']];
  // Sector buckets: keyword rules over impact names, entity names and headline. Fund = the public sector ETF whose price colours the tile.
  const SECTORS = [
    ['Technology', 'XLK', /technolog|software|cloud|internet|cyber|saas|\bai\b|artificial intelligence|data cent/i],
    ['Semiconductors', 'SMH', /semiconductor|chip|nvidia|micron|\bamd\b|asml|tsmc|lam research|wafer/i],
    ['Energy', 'XLE', /\boil\b|\bgas\b|energy|opec|crude|petrol|lng|refin|pipeline/i],
    ['Banks & Finance', 'XLF', /\bbank|lender|financ|fed\b|central bank|interest rate|credit|loan|mortgage/i],
    ['Healthcare', 'XLV', /health|pharma|drug|biotech|medic|hospital|vaccine/i],
    ['Consumer & Retail', 'XLY', /retail|consumer|luxury|e-?commerce|restaurant|shopping|apparel/i],
    ['Autos', 'CARZ', /\bauto|\bcar\b|vehicle|\bev\b|tesla|ford\b|general motors|toyota|hyundai/i],
    ['Industrials', 'XLI', /industrial|manufactur|machinery|logistic|shipping|rail|freight/i],
    ['Aerospace & Defence', 'ITA', /aerospace|defen[cs]e|spacex|boeing|airbus|rheinmetall|missile|airline/i],
    ['Materials & Mining', 'XLB', /mining|miner|steel|copper|lithium|gold\b|silver|chemical|materials/i],
    ['Utilities', 'XLU', /utilit|electric|power|renewable|solar|wind/i],
    ['Real estate', 'XLRE', /real estate|housing|property|reit|home price|mortgage rate/i],
    ['Insurance', 'KIE', /insur/i],
    ['Communication', 'XLC', /media|stream|telecom|social network|netflix|meta platforms|advertis/i],
    ['Crypto', 'BTC-USD', /crypto|bitcoin|ethereum|stablecoin|blockchain/i]
  ];
  const IDX = [['^GSPC', 'S&P 500'], ['^IXIC', 'Nasdaq'], ['^DJI', 'Dow Jones'], ['^FTSE', 'FTSE 100'], ['^GDAXI', 'DAX'], ['^N225', 'Nikkei 225'], ['^HSI', 'Hang Seng'], ['^NSEI', 'Nifty 50']];
  const CMD = ['GC=F', 'SI=F', 'HG=F', 'BZ=F', 'CL=F', 'NG=F', 'ZW=F', 'KC=F'];
  const CRY = ['BTC', 'ETH', 'SOL', 'EURUSD', 'GBPUSD', 'USDJPY'];
  const S = { win: 'w', view: 'sec', sel: null, by: {}, stories: [], intra: {} };
  const fmt = v => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toFixed(Math.abs(v) >= 10 ? 1 : 2) + '%';
  const cls = v => v > 0.005 ? 'u' : v < -0.005 ? 'd' : '';
  const col = v => v > 0.005 ? '#34d399' : v < -0.005 ? '#f87171' : '#8b8b94';
  const move = (a, k) => k === 'd' ? a.d : k === 'w' ? a.w : (a.sp && a.sp.length > 1 ? (a.sp[a.sp.length - 1] / a.sp[0] - 1) * 100 : 0);
  const tint = v => v > 0.005 ? `rgba(52,211,153,${Math.min(.38, .13 + Math.abs(v) * .09).toFixed(2)})` : v < -0.005 ? `rgba(248,113,113,${Math.min(.38, .13 + Math.abs(v) * .09).toFixed(2)})` : 'rgba(255,255,255,.08)';
  const line = (v, c) => { if (!v || v.length < 2) return ''; const lo = Math.min(...v), hi = Math.max(...v), r = hi - lo || 1; return `<svg viewBox="0 0 100 30" preserveAspectRatio="none"><path d="${v.map((y, i) => (i ? 'L' : 'M') + (i / (v.length - 1) * 100).toFixed(1) + ' ' + (27 - (y - lo) / r * 24).toFixed(1)).join('')}" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke"/></svg>`; };
  const series = (a, k) => k === 'd' ? (S.intra[a.s]?.d1?.c || (a.sp || []).slice(-2)) : k === 'w' ? (a.sp || []).slice(-6) : (a.sp || []);
  const text = s => [s.headline, ...(s.impacts || []).map(i => i.name), ...(s.entities || []).map(e => e.name)].join(' ');
  const bucket = s => SECTORS.filter(([, , re]) => re.test(text(s))).map(x => x[0]);
  function sectors() {
    const cut = Date.now() - 7 * 864e5, recent = S.stories.filter(s => Date.parse(s.published_at) >= cut);
    const cnt = {}; for (const s of recent) for (const n of bucket(s)) cnt[n] = (cnt[n] || 0) + 1;
    const L = SECTORS.map(([n, f]) => ({ n, f, c: cnt[n] || 0, a: S.by[f] })).filter(x => x.a).sort((a, b) => b.c - a.c);
    const max = Math.max(1, ...L.map(x => x.c));
    $('mh-grid').innerHTML = L.map((x, i) => { const m = move(x.a, S.win), big = x.c >= max * .9 ? ' w2 r2' : x.c >= max * .45 ? ' w2' : ''; return `<button type="button" class="mh-t${big}" data-n="${x.n}" aria-pressed="${S.sel === x.n}" style="background:${tint(m)}"><span><b>${x.n}</b><small>${x.c} ${x.c === 1 ? 'article' : 'articles'}</small></span><span class="mono ${cls(m)}">${fmt(m)}</span></button>`; }).join('');
  }
  const cards = (list) => { $('mh-grid').className = 'mh-idx'; $('mh-grid').innerHTML = list.map(a => { const m = move(a, S.win); return `<div class="mh-c"><small>${AssetIcons.icon(a)}<span>${a.n}</span></small><span class="mono ${cls(m)}">${fmt(m)}</span>${line(series(a, S.win), col(m))}</div>`; }).join('') || '<div class="nb-none">No data yet.</div>'; };
  function draw() {
    document.querySelectorAll('#mh-win button').forEach(b => b.setAttribute('aria-pressed', b.dataset.k === S.win));
    document.querySelectorAll('#mh-view button').forEach(b => b.setAttribute('aria-pressed', b.dataset.k === S.view));
    $('mh-grid').className = 'mh-grid';
    if (S.view === 'sec') sectors();
    else if (S.view === 'idx') cards(IDX.map(([s]) => S.by[s]).filter(Boolean));
    else if (S.view === 'cmd') cards(CMD.map(s => S.by[s]).filter(Boolean));
    else cards(CRY.map(s => S.by[s]).filter(Boolean));
    list();
  }
  function list() {
    const sel = S.view === 'sec' && S.sel, el = $('mh-ls'); $('mh-sh').hidden = !sel; if (!sel) { el.innerHTML = ''; return; }
    $('mh-t').textContent = 'Articles in ' + sel;
    const cut = Date.now() - 7 * 864e5, L = S.stories.filter(s => Date.parse(s.published_at) >= cut && bucket(s).includes(sel)).sort((a, b) => Date.parse(b.published_at) - Date.parse(a.published_at)).slice(0, 10);
    el.innerHTML = L.map(s => `<a class="nb-li" href="story.html?id=${encodeURIComponent(s.id)}"><span class="th">${s.image ? `<img src="assets/globe/${esc(s.image.file)}" alt="" loading="lazy">` : ''}</span><span><span class="nb-eb">${esc(s.location?.place?.split(',')[0] || '')}</span><h3>${esc(s.headline)}</h3><span class="m">${ago(s.published_at)} · ${esc(s.source?.name || '')}</span></span></a>`).join('') || '<div class="nb-none">No articles for this sector this week.</div>';
  }
  $('mh-win').innerHTML = WIN.map(([k, l]) => `<button type="button" data-k="${k}" aria-pressed="false">${l}</button>`).join('');
  $('mh-view').innerHTML = VIEW.map(([k, l]) => `<button type="button" data-k="${k}" aria-pressed="false">${l}</button>`).join('');
  $('mh-win').onclick = e => { const b = e.target.closest('button'); if (b) { S.win = b.dataset.k; draw(); } };
  $('mh-view').onclick = e => { const b = e.target.closest('button'); if (b) { S.view = b.dataset.k; S.sel = null; draw(); } };
  $('mh-grid').onclick = e => { const t = e.target.closest('.mh-t'); if (t) { S.sel = S.sel === t.dataset.n ? null : t.dataset.n; draw(); if (S.sel) $('mh-sh').scrollIntoView({ behavior: 'smooth', block: 'start' }); } };
  $('mh-x').onclick = () => { S.sel = null; draw(); };
  Promise.all([AssetIcons.ready, fetch('assets/globe/markets.json', { cache: 'no-cache' }).then(r => r.json()), fetch('assets/globe/news-prices.json', { cache: 'no-cache' }).then(r => r.json()).catch(() => ({ assets: {} })), fetch('assets/intraday.json').then(r => r.json()).catch(() => ({ s: {} })), fetch('assets/globe/news-archive.json', { cache: 'no-cache' }).then(r => r.ok ? r.json() : Promise.reject()).catch(() => loadNews())])
    .then(([, m, np, i, n]) => { S.by = Object.fromEntries((m.assets || []).map(a => [a.s, a])); Object.assign(S.by, np.assets || {}); S.intra = i.s || {}; S.stories = n.stories || []; $('mh-up').textContent = 'Updated ' + new Date(m.asof).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }); draw(); })
    .catch(e => { console.error('markets', e); $('mh-grid').innerHTML = '<div class="nb-none">Market data could not load. Please refresh.</div>'; });
})();
