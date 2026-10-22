// Pop-up layer: any asset opens in a blurred sheet over the current page, and the header search is a search overlay with real data.
(() => {
  const EMBED = /[?&]embed=1/.test(location.search);
  const css = document.createElement('style');
  css.textContent = `
  html.embed .hdr,html.embed footer,html.embed #inv-consent-panel,html.embed .palette,html.embed .ap-back,html.embed .ap-bk{display:none!important}html.embed body{padding-top:0!important}html.embed .ap-h{padding-right:210px}@media(max-width:800px){html.embed .ap-h{padding-right:0;padding-top:56px}}
  .pk{position:fixed;inset:0;z-index:200;display:grid;place-items:center;padding:20px;background:rgba(6,6,8,.55);-webkit-backdrop-filter:blur(22px) saturate(1.2);backdrop-filter:blur(22px) saturate(1.2);opacity:0;transition:opacity .22s ease}.pk.on{opacity:1}
  .pk-sheet{position:relative;width:min(1080px,100%);height:min(90vh,940px);border-radius:26px;overflow:hidden;background:#0b0b0d;border:1px solid rgba(255,255,255,.12);box-shadow:0 40px 120px rgba(0,0,0,.6);transform:translateY(14px) scale(.985);transition:transform .26s cubic-bezier(.2,.8,.2,1)}.pk.on .pk-sheet{transform:none}
  .pk-sheet iframe{width:100%;height:100%;border:0;display:block;background:#0b0b0d}
  .pk-x,.pop-x{display:grid;place-items:center;width:40px;height:40px;border-radius:50%;border:1px solid rgba(255,255,255,.14);background:rgba(30,30,34,.72);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);color:#fff;cursor:pointer;transition:background .15s,transform .15s}.pk-x:hover,.pop-x:hover{background:rgba(255,255,255,.16);transform:scale(1.06)}.pk-x:focus-visible,.pop-x:focus-visible{outline:2px solid #ff7a1a;outline-offset:2px}.pk-x svg,.pop-x svg{width:16px;height:16px}
  .pk-x{position:absolute;top:14px;right:14px;z-index:3}.pk-full{position:absolute;top:14px;right:64px;z-index:3;height:40px;display:inline-flex;align-items:center;padding:0 16px;border-radius:999px;border:1px solid rgba(255,255,255,.14);background:rgba(30,30,34,.72);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);color:#fff;font-size:13px;text-decoration:none}.pk-full:hover{background:rgba(255,255,255,.16)}
  .pk-s{align-content:start;padding-top:9vh}.pk-sb{width:min(720px,100%);border-radius:26px;background:#0e0e11;border:1px solid rgba(255,255,255,.12);box-shadow:0 40px 120px rgba(0,0,0,.6);overflow:hidden;transform:translateY(-8px);transition:transform .26s cubic-bezier(.2,.8,.2,1)}.pk.on .pk-sb{transform:none}
  .pk-in{display:flex;align-items:center;gap:12px;padding:0 20px;height:68px;border-bottom:1px solid rgba(255,255,255,.1)}.pk-in svg{width:20px;height:20px;opacity:.6;flex:none}.pk-in input{-webkit-appearance:none;appearance:none;outline:0!important;box-shadow:none!important;border-radius:0!important;padding:0!important;flex:1;min-width:0;background:none;border:0;outline:0;color:#fff;font:500 18px/1 inherit;font-family:inherit;height:100%}.pk-in input::-webkit-search-cancel-button{display:none}.pk-in input:focus,.pk-in input:focus-visible{outline:0!important;box-shadow:none!important}.pk-in kbd{font:500 11px ui-monospace,monospace;opacity:.55;border:1px solid rgba(255,255,255,.2);border-radius:6px;padding:3px 6px}
  .pk-r{max-height:min(60vh,520px);overflow:auto;padding:8px}.pk-r h6{margin:12px 12px 6px;font:600 11px ui-monospace,monospace;letter-spacing:.08em;text-transform:uppercase;color:rgba(255,255,255,.45)}
  .pk-i{display:grid;grid-template-columns:36px minmax(0,1fr) auto;gap:12px;align-items:center;width:100%;border:0;background:none;color:inherit;text-align:left;font:inherit;padding:10px 12px;border-radius:14px;cursor:pointer;min-height:56px;text-decoration:none}.pk-i:hover,.pk-i[aria-selected=true]{background:rgba(255,255,255,.08)}
  .pk-i .ic{width:36px;height:36px;border-radius:50%;display:grid;place-items:center;overflow:hidden;background:rgba(255,255,255,.08)}.pk-i .ic svg,.pk-i .ic img{width:100%;height:100%;object-fit:cover}.pk-i b{display:block;font-size:15px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.pk-i small{display:block;font-size:12px;opacity:.6;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.pk-i .pv{text-align:right;font:500 13px ui-monospace,monospace}.pk-i .pv i{display:block;font-style:normal;font-size:12px;margin-top:2px}
  .pk-i .u{color:#34d399}.pk-i .d{color:#f87171}.pk-i .o{color:#8b8b94}.pk-r h6 em{font-style:normal;margin-left:8px;opacity:.7}.pk-i .ic img{border-radius:50%}.pk-none{padding:28px 16px;text-align:center;opacity:.6;font-size:14px}
  @media(max-width:800px){.pk{padding:0;place-items:end center}.pk-sheet{width:100%;height:94vh;border-radius:26px 26px 0 0}.pk-s{place-items:start center;padding-top:0}.pk-sb{border-radius:0 0 26px 26px;width:100%}.pk-full{right:62px}}
  @media(prefers-reduced-motion:reduce){.pk,.pk-sheet,.pk-sb{transition:none}}`;
  document.head.appendChild(css);
  if (EMBED) { document.documentElement.classList.add('embed'); const b = document.createElement('base'); b.target = '_top'; document.head.prepend(b); return; }
  const X = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg>', SEARCH = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>';
  const esc = t => String(t ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  let layer, prevFocus, onKey;
  function mount(cls, html) {
    close(true); prevFocus = document.activeElement; layer = document.createElement('div'); layer.className = 'pk ' + cls; layer.innerHTML = html; document.body.appendChild(layer); document.documentElement.style.overflow = 'hidden';
    layer.addEventListener('mousedown', e => { if (e.target === layer) close(); });
    onKey = e => { if (e.key === 'Escape') { e.preventDefault(); close(); } }; document.addEventListener('keydown', onKey);
    requestAnimationFrame(() => layer.classList.add('on')); return layer;
  }
  function close(silent) { if (!layer) return; const l = layer; layer = null; document.removeEventListener('keydown', onKey); document.documentElement.style.overflow = ''; l.classList.remove('on'); setTimeout(() => l.remove(), 200); if (!silent && /^#a=/.test(location.hash)) history.back(); try { prevFocus?.focus?.(); } catch {} }
  function open(sym, push = true) {
    const url = 'asset.html?s=' + encodeURIComponent(sym);
    const l = mount('', `<div class="pk-sheet" role="dialog" aria-modal="true" aria-label="Asset details"><a class="pk-full" href="${url}">Open full page</a><button class="pk-x" type="button" aria-label="Close">${X}</button><iframe title="Asset details" src="${url}&embed=1"></iframe></div>`);
    l.querySelector('.pk-x').onclick = () => close(); l.querySelector('.pk-x').focus();
    if (push) { try { history.pushState({ pk: 1 }, '', '#a=' + encodeURIComponent(sym)); } catch {} }
  }
  window.addEventListener('popstate', () => { const m = /^#a=(.+)/.exec(location.hash); if (m) open(decodeURIComponent(m[1]), false); else close(true); });
  // ---- search ----
  let DATA = null, loading;
  const load = () => loading || (loading = Promise.all([
    fetch('assets/globe/markets.json').then(r => r.json()).catch(() => ({ assets: [] })),
    fetch('assets/globe/iso.json').then(r => r.json()).catch(() => ({})),
    fetch('assets/globe/news-live.json').then(r => r.json()).catch(() => ({ stories: [] })),
    fetch('assets/globe/news-archive.json').then(r => r.json()).catch(() => ({ stories: [] })),
    window.INV_LIVE_URL ? fetch(window.INV_LIVE_URL, { cache: 'no-store' }).then(r => r.json()).catch(() => null) : Promise.resolve(null)
  ]).then(([m, iso, n, arc, live]) => {
    const by = new Map((m.assets || []).map(a => [a.s, a]));
    if (live?.p) for (const [id, v] of Object.entries(live.p)) { const a = by.get(id); if (a) { a.p = v.p; a.d = v.pc; } else by.set(id, { s: id, n: v.n, t: 'crypto', p: v.p, d: v.pc }); }
    const seen = new Set(), stories = []; for (const x of [...(n.stories || []), ...(arc.stories || [])]) if (x.id && !seen.has(x.id)) { seen.add(x.id); stories.push(x); }
    DATA = { assets: [...by.values()], iso, countries: Object.keys(iso).filter(c => !/\bIs\.$/.test(c)), stories };
  }));
  const label = a => a.s.replace(/-USD$/, '').replace(/=F$/, '');
  const money = (v, a) => window.InvPrefs ? InvPrefs.fmt(v, a) : v?.toLocaleString('en-US', { maximumFractionDigits: 2 });
  const rank = (q, a) => { const s = label(a).toLowerCase(), n = (a.n || '').toLowerCase(); if (s === q) return 0; if (n === q) return 1; if (s.startsWith(q)) return 2; if (n.startsWith(q)) return 3; if (n.split(/[\s.-]+/).some(w => w.startsWith(q))) return 4; if (n.includes(q) || s.includes(q)) return 5; return 9; };
  const PAGES = [['Markets', 'markets.html', 'Prices, sectors, crypto, currencies'], ['Crypto', 'markets.html?view=cry', 'Top coins with live prices'], ['Indices', 'markets.html?view=idx', 'World stock indices'], ['Commodities', 'markets.html?view=cmd', 'Oil, gold, metals, agriculture'], ['Currencies', 'markets.html?view=fx', 'Major pairs and cross rates'], ['Live charts', 'markets.html?view=tv', 'TradingView charts'], ['News', 'assets/globe/news.html', 'All articles'], ['Globe', 'globe.html', 'News on the world map'], ['Economic calendar', 'calendar.html', 'Releases and earnings'], ['Stock screener', 'screener.html', 'Filter companies'], ['Compare', 'compare.html', 'Compare assets side by side'], ['Calculator', 'calculator.html', 'Investment calculators'], ['Currency converter', 'converter.html', 'Convert between currencies'], ['Watchlist', 'watchlist.html', 'Your saved assets'], ['Learn', 'education.html', 'Lessons and guides'], ['About', 'about.html', 'Who we are'], ['Contact', 'contact.html', 'Get in touch'], ['Sources and methodology', 'sources.html', 'Where our data comes from'], ['Editorial policy', 'editorial-policy.html', 'How we publish'], ['Corrections', 'corrections.html', 'Fixes and updates'], ['Privacy', 'privacy.html', 'Privacy policy'], ['Cookies', 'cookies.html', 'Cookie policy'], ['Terms', 'terms.html', 'Terms of use']];
  const GROUPS = [['Stocks', a => a.t === 'stocks' && a.g !== 'Index'], ['Indices', a => a.t === 'stocks' && a.g === 'Index'], ['Crypto', a => a.t === 'crypto'], ['Commodities', a => a.t === 'cmd'], ['Currencies', a => a.t === 'fx']];
  const POP = ['BTC-USD', 'ETH-USD', '^GSPC', 'NVDA', 'GC=F', 'EURUSD'];
  const row = a => { const d = a.d, c = d > 0.005 ? 'u' : d < -0.005 ? 'd' : 'o', ar = d > 0.005 ? '↑' : d < -0.005 ? '↓' : '↔'; return `<button class="pk-i" type="button" data-a="${esc(a.s)}"><span class="ic">${window.AssetIcons ? AssetIcons.icon(a) : ''}</span><span><b>${esc(a.n)}</b><small>${esc(label(a))} · ${({ stocks: a.g === 'Index' ? 'Index' : 'Stock', crypto: 'Crypto', cmd: 'Commodity', fx: 'Currency pair' })[a.t] || ''}</small></span><span class="pv">${money(a.p, a)}<i class="${c}">${isFinite(d) ? ar + ' ' + Math.abs(d).toFixed(2) + '%' : ''}</i></span></button>`; };
  function searchUI() {
    const l = mount('pk-s', `<div class="pk-sb" role="dialog" aria-modal="true" aria-label="Search"><div class="pk-in">${SEARCH}<input type="search" autocomplete="off" spellcheck="false" placeholder="Search assets, countries, articles and pages" aria-label="Search"><kbd>esc</kbd></div><div class="pk-r"><div class="pk-none">Loading…</div></div></div>`);
    const inp = l.querySelector('input'), res = l.querySelector('.pk-r'); inp.focus(); let sel = 0;
    const items = () => [...res.querySelectorAll('.pk-i')], mark = () => items().forEach((e, i) => e.setAttribute('aria-selected', i === sel ? 'true' : 'false'));
    const paint = () => {
      if (!DATA) return; const q = inp.value.trim().toLowerCase(); let h = '';
      const link = (href, ic, t, sub) => `<a class="pk-i" href="${esc(href)}"><span class="ic">${ic}</span><span><b>${esc(t)}</b><small>${esc(sub || '')}</small></span><span></span></a>`;
      if (!q) { const pop = POP.map(s => DATA.assets.find(a => a.s === s)).filter(Boolean); h = `<h6>Popular</h6>` + pop.map(row).join('') + '<h6>Go to</h6>' + PAGES.slice(0, 6).map(p => link(p[1], '↗', p[0], p[2])).join(''); }
      else {
        const ranked = DATA.assets.map(a => [rank(q, a), a]).filter(x => x[0] < 9).sort((a, b) => a[0] - b[0] || (b[1].m || 0) - (a[1].m || 0)).map(x => x[1]);
        for (const [name, fn] of GROUPS) { const g = ranked.filter(fn); if (g.length) h += `<h6>${name}<em>${g.length}</em></h6>` + g.slice(0, 4).map(row).join(''); }
        const sec = (window.InvSectors ? InvSectors.list : []).filter(x => x.name.toLowerCase().includes(q)).slice(0, 3);
        if (sec.length) h += '<h6>Sectors</h6>' + sec.map(x => link('assets/globe/news.html?sector=' + encodeURIComponent(x.slug), InvSectors.icon(x.name), x.name, 'Sector · articles and sector fund move')).join('');
        const cs = DATA.countries.filter(c => c.toLowerCase().includes(q)).sort((a, b) => (a.toLowerCase().startsWith(q) ? 0 : 1) - (b.toLowerCase().startsWith(q) ? 0 : 1)).slice(0, 4);
        if (cs.length) h += '<h6>Countries</h6>' + cs.map(c => link('assets/globe/news.html?country=' + encodeURIComponent(c), DATA.iso[c] ? `<img src="assets/globe/flags/${DATA.iso[c].toLowerCase()}.svg" alt="">` : '', c, 'Articles and markets')).join('');
        const ns = DATA.stories.filter(s => ((s.headline || '') + ' ' + (s.summary || '') + ' ' + (s.entities || []).map(e => e.name).join(' ')).toLowerCase().includes(q)).sort((a, b) => Date.parse(b.published_at) - Date.parse(a.published_at));
        if (ns.length) h += `<h6>Articles<em>${ns.length}</em></h6>` + ns.slice(0, 5).map(s => link('assets/globe/news.html?story=' + encodeURIComponent(s.id), '', s.headline, (s.source?.name || '') + ' · ' + new Date(s.published_at).toLocaleDateString(window.InvPrefs ? undefined : 'en-GB', { day: 'numeric', month: 'short' }))).join('');
        const ps = PAGES.filter(p => (p[0] + ' ' + p[2]).toLowerCase().includes(q)).slice(0, 4);
        if (ps.length) h += '<h6>Pages and tools</h6>' + ps.map(p => link(p[1], '↗', p[0], p[2])).join('');
        if (!h) h = `<div class="pk-none">No result for “${esc(inp.value)}”.</div>`;
      }
      res.innerHTML = h; sel = 0; mark();
    };
    load().then(paint); inp.addEventListener('input', paint);
    res.addEventListener('click', e => { const b = e.target.closest('[data-a]'); if (b) { const s = b.dataset.a; close(true); setTimeout(() => open(s), 30); } });
    inp.addEventListener('keydown', e => { const it = items(); if (e.key === 'ArrowDown') { e.preventDefault(); sel = Math.min(sel + 1, it.length - 1); mark(); it[sel]?.scrollIntoView({ block: 'nearest' }); } else if (e.key === 'ArrowUp') { e.preventDefault(); sel = Math.max(sel - 1, 0); mark(); it[sel]?.scrollIntoView({ block: 'nearest' }); } else if (e.key === 'Enter') { e.preventDefault(); it[sel]?.click(); } });
  }
  // ---- wiring ----
  document.addEventListener('click', e => {
    if (e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
    const s = e.target.closest('.search-btn, [data-search], .hn-search'); if (s) { e.preventDefault(); e.stopImmediatePropagation(); searchUI(); return; }
    const a = e.target.closest('a[href*="asset.html?s="]'); if (a && !a.closest('.pk')) { const m = /asset\.html\?s=([^&#]+)/.exec(a.getAttribute('href')); if (m) { e.preventDefault(); open(decodeURIComponent(m[1])); } }
  }, true);
  document.addEventListener('keydown', e => { if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); e.stopImmediatePropagation(); searchUI(); } }, true);
  window.InvPeek = { open, search: searchUI, close };
  const m0 = /^#a=(.+)/.exec(location.hash); if (m0) document.addEventListener('DOMContentLoaded', () => open(decodeURIComponent(m0[1]), false));
})();
