// Pop-up layer: any asset opens in a blurred sheet over the current page, and the header search is a search overlay with real data.
(() => {
  const EMBED = /[?&]embed=1/.test(location.search);
  const ROOT = (() => { try { return new URL('../', document.currentScript.src).href; } catch { return ''; } })();
  const css = document.createElement('style');
  css.textContent = `
  html.embed .hdr,html.embed footer,html.embed #inv-consent-panel,html.embed .palette,html.embed .ap-back,html.embed .ap-bk{display:none!important}html.embed body{padding-top:0!important}html.embed .ap-h{padding-right:210px}@media(max-width:800px){html.embed .ap-h{padding-right:0;padding-top:56px}}
  .pk{position:fixed;inset:0;z-index:200;display:grid;place-items:center;padding:20px;background:rgba(6,6,8,.55);-webkit-backdrop-filter:blur(22px) saturate(1.2);backdrop-filter:blur(22px) saturate(1.2);opacity:0;transition:opacity .22s ease}.pk.on{opacity:1}
  .pk-sheet{position:relative;width:min(600px,100%);height:min(88vh,860px);border-radius:26px;overflow:hidden;background:#0b0b0d;border:1px solid rgba(255,255,255,.12);box-shadow:0 40px 120px rgba(0,0,0,.6);transform:translateY(14px) scale(.985);transition:transform .26s cubic-bezier(.2,.8,.2,1)}.pk.on .pk-sheet{transform:none}
  .pk-sheet iframe{width:100%;height:100%;border:0;display:block;background:#0b0b0d}
  .pk-x,.pop-x{display:grid;place-items:center;width:40px;height:40px;border-radius:50%;border:1px solid rgba(255,255,255,.14);background:rgba(30,30,34,.72);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);color:#fff;cursor:pointer;transition:background .15s,transform .15s}.pk-x:hover,.pop-x:hover{background:rgba(255,255,255,.16);transform:scale(1.06)}.pk-x:focus-visible,.pop-x:focus-visible{outline:2px solid #ff7a1a;outline-offset:2px}.pk-x svg,.pop-x svg{width:16px;height:16px}
  .pk-x{position:absolute;top:14px;right:14px;z-index:3}.pk-full{position:absolute;top:14px;right:64px;z-index:3;height:40px;display:inline-flex;align-items:center;padding:0 16px;border-radius:999px;border:1px solid rgba(255,255,255,.14);background:rgba(30,30,34,.72);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);color:#fff;font-size:13px;text-decoration:none}.pk-full:hover{background:rgba(255,255,255,.16)}
  .pk-s{align-content:start;padding-top:9vh}.pk-sb{width:min(720px,100%);border-radius:26px;background:#0e0e11;border:1px solid rgba(255,255,255,.12);box-shadow:0 40px 120px rgba(0,0,0,.6);overflow:hidden;transform:translateY(-8px);transition:transform .26s cubic-bezier(.2,.8,.2,1)}.pk.on .pk-sb{transform:none}
  .pk-in{display:flex;align-items:center;gap:12px;padding:0 20px;height:68px;border-bottom:1px solid rgba(255,255,255,.1)}.pk-in svg{width:20px;height:20px;opacity:.6;flex:none}.pk-in input{-webkit-appearance:none;appearance:none;outline:0!important;box-shadow:none!important;border-radius:0!important;padding:0!important;flex:1;min-width:0;background:none;border:0;outline:0;color:#fff;font:500 18px/1 inherit;font-family:inherit;height:100%}.pk-in input::-webkit-search-cancel-button{display:none}.pk-in input:focus,.pk-in input:focus-visible{outline:0!important;box-shadow:none!important}.pk-in kbd{font:500 11px ui-monospace,monospace;opacity:.55;border:1px solid rgba(255,255,255,.2);border-radius:6px;padding:3px 6px}
  .pk-r{max-height:min(60vh,520px);overflow:auto;padding:8px}.pk-r h6{margin:12px 12px 6px;font:600 11px ui-monospace,monospace;letter-spacing:.08em;text-transform:uppercase;color:rgba(255,255,255,.45)}
  .pk-i{display:grid;grid-template-columns:36px minmax(0,1fr) auto;gap:12px;align-items:center;width:100%;border:0;background:none;color:inherit;text-align:left;font:inherit;padding:10px 12px;border-radius:14px;cursor:pointer;min-height:56px;text-decoration:none}.pk-i:hover,.pk-i[aria-selected=true]{background:rgba(255,255,255,.08)}
  .pk-i .ic{width:36px;height:36px;border-radius:50%;display:grid;place-items:center;overflow:hidden;background:rgba(255,255,255,.08);color:#c9c9d1}.pk-i .ic svg,.pk-i .ic img{width:100%;height:100%;object-fit:cover}.pk-i b{display:block;font-size:15px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.pk-i small{display:block;font-size:12px;opacity:.6;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.pk-i .pv{text-align:right;font:500 13px ui-monospace,monospace}.pk-i .pv i{display:block;font-style:normal;font-size:12px;margin-top:2px}
  .pk-i .u{color:#34d399}.pk-i .d{color:#f87171}.pk-i .o{color:#8b8b94}.pk-r h6 em{font-style:normal;margin-left:8px;opacity:.7}.pk-i .ic img{border-radius:50%}.pk-none{padding:28px 16px;text-align:center;opacity:.6;font-size:14px}
  @media(max-width:800px){.pk{padding:0;place-items:end center}.pk-sheet{width:100%;height:94vh;border-radius:26px 26px 0 0}.pk-s{place-items:start center;padding-top:0}.pk-sb{border-radius:0 0 26px 26px;width:100%}.pk-full{right:62px}}

  .pk-sb{width:min(780px,100%)}.pk-in{height:76px;padding:0 24px}.pk-in input{font-size:22px!important;font-weight:500;letter-spacing:-.02em}.pk-in svg{width:22px;height:22px}
  .pk-fl{display:flex;gap:8px;overflow-x:auto;padding:12px 16px 4px;scrollbar-width:none}.pk-fl::-webkit-scrollbar{display:none}
  .pk-f{flex:none;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.05);color:inherit;font:600 13px -apple-system,"SF Pro Text",Inter,sans-serif;border-radius:999px;height:36px;padding:0 14px;cursor:pointer;display:inline-flex;align-items:center;gap:7px;transition:background .15s}.pk-f:hover{background:rgba(255,255,255,.1)}.pk-f.on{background:#fff;color:#000;border-color:#fff}.pk-f em{font-style:normal;font-weight:500;opacity:.55;font-size:12px}
  .pk-body{display:block}.pk-pv{display:none}
  .pk-i{grid-template-columns:44px minmax(0,1fr) auto;min-height:64px;border-radius:18px}.pk-i .ic{width:44px;height:44px}.pk-i b{font-size:16px;letter-spacing:-.01em}.pk-i .sp{display:none}
  .pk-i .pv{text-align:right;font-family:-apple-system,"SF Pro Display",Inter,sans-serif;display:grid;justify-items:end;gap:4px}.pk-i .px{font-size:17px;font-weight:650;letter-spacing:-.025em;font-variant-numeric:tabular-nums}.pk-i .pc{font-style:normal;font-size:12px;font-weight:700;padding:2px 8px;border-radius:999px;font-variant-numeric:tabular-nums}.pk-i .pc.u{background:rgba(48,209,88,.16);color:#5df08a}.pk-i .pc.d{background:rgba(255,69,58,.16);color:#ff7b72}.pk-i .pc.o{background:rgba(255,255,255,.08);color:#a1a1aa}
  .pk-r h6{display:flex;align-items:center}.pk-r h6 em{font-style:normal;margin-left:8px;opacity:.7}
  .pk-i.top{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.1)}
  .pk-s.v2 .pk-sb{width:min(860px,100%)}.pk-s.v2.v3 .pk-sb{width:min(1120px,100%)}.pk-s.v2.v3 .pk-i.top{grid-template-columns:56px minmax(0,1fr) 110px auto}.pk-s.v2 .pk-i.top{grid-template-columns:56px minmax(0,1fr) 120px auto;min-height:92px;padding:14px 16px;background:linear-gradient(135deg,rgba(255,122,26,.16),rgba(255,255,255,.05))}.pk-s.v2 .pk-i.top .ic{width:56px;height:56px}.pk-s.v2 .pk-i.top b{font-size:20px}.pk-s.v2 .pk-i.top .sp{display:block}.pk-s.v2 .pk-i.top .sp svg{width:120px;height:40px}.pk-s.v2 .pk-i.top .px{font-size:22px}
  .pk-s.v3 .pk-sb{width:min(1120px,100%)}.pk-s.v3 .pk-body{display:grid;grid-template-columns:200px minmax(0,1fr) 320px;min-height:420px}.pk-s.v3 .pk-fl{flex-direction:column;overflow:visible;padding:16px 12px;border-right:1px solid rgba(255,255,255,.08);gap:4px}.pk-s.v3 .pk-f{border:0;background:none;border-radius:12px;height:42px;justify-content:space-between;width:100%}.pk-s.v3 .pk-f.on{background:rgba(255,255,255,.12);color:#fff}.pk-s.v3 .pk-r{max-height:min(62vh,560px)}.pk-s.v3 .pk-pv{display:block;border-left:1px solid rgba(255,255,255,.08);padding:20px;background:rgba(255,255,255,.03)}
  .pv-h{display:flex;gap:12px;align-items:center}.pv-h .ic{width:48px;height:48px;border-radius:50%;overflow:hidden;display:grid;place-items:center;flex:none}.pv-h .ic svg,.pv-h .ic img{width:100%;height:100%;object-fit:cover}.pv-h b{display:block;font-size:18px;letter-spacing:-.02em}.pv-h small{opacity:.6;font-size:12px}.pv-p{font:700 38px/1.1 -apple-system,"SF Pro Display",Inter,sans-serif;letter-spacing:-.04em;margin:18px 0 8px}.pk-pv .pc{font-style:normal;font-size:13px;font-weight:700;padding:3px 10px;border-radius:999px}.pk-pv .pc.u{background:rgba(48,209,88,.16);color:#5df08a}.pk-pv .pc.d{background:rgba(255,69,58,.16);color:#ff7b72}.pk-pv .pc.o{background:rgba(255,255,255,.08)}.pv-c svg{width:100%;height:80px;margin:16px 0}.pv-r{display:grid;grid-template-columns:1fr auto;gap:8px 12px;font-size:13px}.pv-r span{opacity:.6}.pv-r b{font-variant-numeric:tabular-nums}.pv-go{margin-top:18px;width:100%;height:46px;border-radius:14px;border:0;background:#fff;color:#000;font:600 14px Inter,sans-serif;cursor:pointer}
  @media(max-width:800px){.pk-i{grid-template-columns:32px minmax(0,1fr) auto!important;gap:10px;min-height:54px;padding:8px 10px;border-radius:14px}.pk-i .ic{width:32px!important;height:32px!important}.pk-i .ic svg{width:66%;height:66%}.pk-i b{font-size:14.5px}.pk-i small{font-size:11.5px}.pk-i .px{font-size:15px}.pk-i .pc{font-size:11px;padding:1px 7px}.pk-s .pk-i.top{grid-template-columns:40px minmax(0,1fr) auto!important;min-height:68px!important;padding:10px 12px!important}.pk-s .pk-i.top .ic{width:40px!important;height:40px!important}.pk-s .pk-i.top b{font-size:16px!important}.pk-s .pk-i.top .px{font-size:17px!important}.pk-f{height:32px;font-size:12.5px;padding:0 12px}.pk-s .pk-sb{width:100%}.pk-in{height:64px;padding:0 18px}.pk-in input{font-size:18px!important}.pk-s.v3 .pk-body{display:block}.pk-s.v3 .pk-fl{flex-direction:row;overflow-x:auto;border:0;padding:12px 16px 4px}.pk-s.v3 .pk-f{width:auto;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.05)}.pk-s.v3 .pk-pv{display:none}.pk-s.v2 .pk-i.top{grid-template-columns:48px minmax(0,1fr) auto}.pk-s.v2 .pk-i.top .sp{display:none}}
  .ai-c{border-radius:28%!important}.ai-c svg{width:100%!important;height:100%!important;display:block}.pk-i .ic:has(.ai-c),.pv-h .ic:has(.ai-c){border-radius:28%!important;background:none!important}
  .ai-c{width:100%!important;height:100%!important}
  .pk-sector{width:min(780px,100%)!important;height:auto!important;max-height:88vh}.pk-pbody{max-height:88vh;overflow:auto;padding:26px 26px 22px}.pk-sector .mh-p{background:none!important;border:0!important;-webkit-backdrop-filter:none!important;backdrop-filter:none!important;padding:0!important;border-radius:0!important}.pk-sector .mh-ph{padding-right:52px}
  /* glass: the page (globe, map, lists) stays visible, blurred, behind the panels */
  .pk{background:rgba(6,6,8,.28)!important;-webkit-backdrop-filter:blur(14px) saturate(1.2)!important;backdrop-filter:blur(14px) saturate(1.2)!important}
  .pk-sb,.pk-sheet{background:rgba(12,12,15,.46)!important;-webkit-backdrop-filter:blur(24px) saturate(1.5)!important;backdrop-filter:blur(24px) saturate(1.5)!important;border-color:rgba(255,255,255,.14)!important}
  .pk-in{border-bottom-color:rgba(255,255,255,.08)!important}.pk-s.v3 .pk-pv{background:rgba(255,255,255,.04)!important}
  @media(max-width:800px){.pk-s{padding:0}.pk-s .pk-sb{border-radius:0 0 26px 26px;border-top:0;height:auto}.pk-sheet{background:rgba(12,12,15,.62)!important}}
  .pk-s .pk-r.popular,.pk-s.v3 .pk-r.popular{max-height:min(38vh,292px);overflow-y:auto;-webkit-mask-image:linear-gradient(#000 calc(100% - 28px),transparent);mask-image:linear-gradient(#000 calc(100% - 28px),transparent);padding-bottom:22px}
  @media(min-width:801px){.pk-s .pk-r.popular,.pk-s.v3 .pk-r.popular{max-height:min(62vh,560px);-webkit-mask-image:none;mask-image:none;padding-bottom:8px}}
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
    const url = ROOT + 'asset.html?s=' + encodeURIComponent(sym);
    const l = mount('', `<div class="pk-sheet" role="dialog" aria-modal="true" aria-label="Asset details"><a class="pk-full" href="${url}">Open full page</a><button class="pk-x" type="button" aria-label="Close">${X}</button><iframe title="Asset details" src="${url}&embed=1"></iframe></div>`);
    l.querySelector('.pk-x').onclick = () => close(); l.querySelector('.pk-x').focus();
    if (push) { try { history.pushState({ pk: 1 }, '', '#a=' + encodeURIComponent(sym)); } catch {} }
  }
  window.addEventListener('popstate', () => { const m = /^#a=(.+)/.exec(location.hash), n = /^#s=(.+)/.exec(location.hash); if (m) open(decodeURIComponent(m[1]), false); else if (n && window.InvPeek?.onSector) InvPeek.onSector(decodeURIComponent(n[1]), false); else close(true); });
  function panel(html, hash) {
    const l = mount('', `<div class="pk-sheet pk-sector" role="dialog" aria-modal="true" aria-label="Details"><button class="pk-x" type="button" aria-label="Close">${X}</button><div class="pk-pbody">${html}</div></div>`);
    l.querySelector('.pk-x').onclick = () => close(); l.querySelector('.pk-x').focus();
    l.querySelector('.pk-pbody').addEventListener('click', e => { const r = e.target.closest('[data-s]'); if (r) { close(true); setTimeout(() => open(r.dataset.s), 30); } });
    if (hash) { try { history.pushState({ pk: 1 }, '', hash); } catch {} }
    return l;
  }
  // ---- search ----
  if (!window.AssetIcons) { const sc = document.createElement('script'); sc.src = ROOT + 'assets/asset-icons.js'; document.head.appendChild(sc); }
  let DATA = null, loading;
  const jf = u => fetch(ROOT + u).then(r => r.json());
  const load = () => loading || (loading = Promise.all([
    jf('assets/globe/markets.json').catch(() => ({ assets: [] })),
    jf('assets/globe/iso.json').catch(() => ({})),
    jf('assets/globe/news-live.json').catch(() => ({ stories: [] })),
    jf('assets/globe/news-archive.json').catch(() => ({ stories: [] })),
    window.INV_LIVE_URL ? fetch(window.INV_LIVE_URL, { cache: 'no-store' }).then(r => r.json()).catch(() => null) : Promise.resolve(null)
  ]).then(([m, iso, n, arc, live]) => {
    const by = new Map((m.assets || []).map(a => [a.s, a]));
    if (live?.p) for (const [id, v] of Object.entries(live.p)) { const a = by.get(id); if (a) { a.p = v.p; a.d = v.pc; } else by.set(id, { s: id, n: v.n, t: 'crypto', p: v.p, d: v.pc }); }
    const seen = new Set(), stories = []; for (const x of [...(n.stories || []), ...(arc.stories || [])]) if (x.id && !seen.has(x.id)) { seen.add(x.id); stories.push(x); }
    DATA = { assets: [...by.values()], iso, countries: Object.keys(iso).filter(c => !/\bIs\.$/.test(c)), stories };
  }));
  const label = a => a.s.replace(/-USD$/, '').replace(/=F$/, '').replace(/^\^/, '');
  const money = (v, a) => window.InvPrefs ? InvPrefs.fmt(v, a) : v?.toLocaleString('en-US', { maximumFractionDigits: 2 });
  const rank = (q, a) => { const s = label(a).toLowerCase(), n = (a.n || '').toLowerCase(); if (s === q) return 0; if (n === q) return 1; if (s.startsWith(q)) return 2; if (n.startsWith(q)) return 3; if (n.split(/[\s.-]+/).some(w => w.startsWith(q))) return 4; if (n.includes(q) || s.includes(q)) return 5; return 9; };
  const PAGES = [['Markets', 'markets.html', 'Prices, sectors, crypto, currencies'], ['Crypto', 'markets.html?view=cry', 'Top coins with live prices'], ['Indices', 'markets.html?view=idx', 'World stock indices'], ['Commodities', 'markets.html?view=cmd', 'Oil, gold, metals, agriculture'], ['Currencies', 'markets.html?view=fx', 'Major pairs and cross rates'], ['Live charts', 'markets.html?view=tv', 'TradingView charts'], ['News', 'assets/globe/news.html', 'All articles'], ['Globe', 'globe.html', 'News on the world map'], ['Economic calendar', 'calendar.html', 'Releases and earnings'], ['Stock screener', 'screener.html', 'Filter companies'], ['Compare', 'compare.html', 'Compare assets side by side'], ['Calculator', 'calculator.html', 'Investment calculators'], ['Currency converter', 'converter.html', 'Convert between currencies'], ['Watchlist', 'watchlist.html', 'Your saved assets'], ['Learn', 'education.html', 'Lessons and guides'], ['About', 'about.html', 'Who we are'], ['Contact', 'contact.html', 'Get in touch'], ['Sources and methodology', 'sources.html', 'Where our data comes from'], ['Editorial policy', 'editorial-policy.html', 'How we publish'], ['Corrections', 'corrections.html', 'Fixes and updates'], ['Privacy', 'privacy.html', 'Privacy policy'], ['Cookies', 'cookies.html', 'Cookie policy'], ['Terms', 'terms.html', 'Terms of use']];
  const FILTERS = [['all', 'All'], ['stocks', 'Companies'], ['crypto', 'Crypto'], ['idx', 'Indices'], ['cmd', 'Commodities'], ['fx', 'Currencies'], ['countries', 'Countries'], ['articles', 'Articles']];
  const GROUPS = { stocks: ['Companies', a => a.t === 'stocks' && a.g !== 'Index'], idx: ['Indices', a => a.t === 'stocks' && a.g === 'Index'], crypto: ['Crypto', a => a.t === 'crypto'], cmd: ['Commodities', a => a.t === 'cmd'], fx: ['Currencies', a => a.t === 'fx'] };
  const POP = ['BTC-USD', 'ETH-USD', '^GSPC', 'NVDA', 'TSLA', 'AAPL', 'META', 'MSFT', '^IXIC', 'GC=F', 'CL=F', 'SOL-USD', 'EURUSD'];
  const fmtP = d => isFinite(d) ? `<i class="pc ${d > 0.005 ? 'u' : d < -0.005 ? 'd' : 'o'}">${d > 0.005 ? '↑' : d < -0.005 ? '↓' : '↔'} ${Math.abs(d).toFixed(2)}%</i>` : '';
  const kind = a => ({ stocks: a.g === 'Index' ? 'Index' : a.g === 'Country ETF' ? 'ETF' : 'Company', crypto: 'Crypto', cmd: 'Commodity', fx: 'Currency pair' })[a.t] || '';
  const spark = (v, w = 260, h = 70) => { v = (v || []).filter(isFinite); if (v.length < 2) return ''; const lo = Math.min(...v), hi = Math.max(...v), r = hi - lo || 1, up = v[v.length - 1] >= v[0], c = up ? '#34d399' : '#f87171', pts = v.map((y, i) => `${(i / (v.length - 1) * w).toFixed(1)},${(h - 4 - (y - lo) / r * (h - 8)).toFixed(1)}`).join(' L'); return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none"><path d="M${pts}" fill="none" stroke="${c}" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/></svg>`; };
  const row = (a, cls = '') => `<button class="pk-i ${cls}" type="button" data-a="${esc(a.s)}"><span class="ic">${window.AssetIcons ? AssetIcons.icon(a) : ''}</span><span><b>${esc(a.n)}</b><small>${esc(label(a))} · ${kind(a)}</small></span>${cls ? `<span class="sp">${spark(a.sp, 120, 40)}</span>` : ''}<span class="pv"><span class="px">${money(a.p, a)}</span>${fmtP(a.d)}</span></button>`;
  const lnk = (href, ic, t, sub, nav = '') => `<a class="pk-i" href="${esc(href)}" ${nav ? `data-nav="${esc(nav)}"` : ''}><span class="ic">${ic}</span><span><b>${esc(t)}</b><small>${esc(sub || '')}</small></span><span></span></a>`;
  function search(q) {
    const out = []; if (!DATA) return out;
    const ranked = q ? DATA.assets.map(a => [rank(q, a), a]).filter(x => x[0] < 9).sort((a, b) => a[0] - b[0] || (b[1].m || 0) - (a[1].m || 0)).map(x => x[1]) : [];
    for (const k of ['stocks', 'crypto', 'idx', 'cmd', 'fx']) { const items = ranked.filter(GROUPS[k][1]); if (items.length) out.push({ key: k, title: GROUPS[k][0], items, html: (i, c) => row(i, c), type: 'asset' }); }
    const sec = q ? (window.InvSectors ? InvSectors.list : []).filter(x => x.name.toLowerCase().includes(q)) : [];
    if (sec.length) out.push({ key: 'sectors', fk: 'stocks', title: 'Sectors', items: sec, html: x => lnk(ROOT + 'assets/globe/news.html?sector=' + encodeURIComponent(x.slug), InvSectors.icon(x.name), x.name, 'Sector · articles and sector fund move') });
    const cs = q ? DATA.countries.filter(c => c.toLowerCase().includes(q)).sort((a, b) => (a.toLowerCase().startsWith(q) ? 0 : 1) - (b.toLowerCase().startsWith(q) ? 0 : 1)) : [];
    if (cs.length) out.push({ key: 'countries', title: 'Countries', items: cs, html: c => lnk(ROOT + 'assets/globe/news.html?country=' + encodeURIComponent(c), DATA.iso[c] ? `<img src="${ROOT}assets/globe/flags/${DATA.iso[c].toLowerCase()}.svg" alt="">` : '', c, 'Articles and markets', 'country:' + c) });
    const ns = q ? DATA.stories.filter(s => ((s.headline || '') + ' ' + (s.summary || '') + ' ' + (s.entities || []).map(e => e.name).join(' ')).toLowerCase().includes(q)).sort((a, b) => Date.parse(b.published_at) - Date.parse(a.published_at)) : [];
    if (ns.length) out.push({ key: 'articles', title: 'Articles', items: ns, html: s => lnk(ROOT + 'assets/globe/news.html?story=' + encodeURIComponent(s.id), '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M5 4h11a2 2 0 0 1 2 2v13a1 1 0 0 0 1 1H6a2 2 0 0 1-2-2V5a1 1 0 0 1 1-1z"/><path d="M18 8h2v11a1 1 0 0 1-1 1M8 8h6M8 12h6M8 16h4"/></svg>', s.headline, (s.source?.name || '') + ' · ' + new Date(s.published_at).toLocaleDateString(undefined, { day: 'numeric', month: 'short' }), 'story:' + s.id), more: 'articles' });
    return out;
  }
  function searchUI() {
    const V = (new URLSearchParams(location.search).get('sv') || (() => { try { return localStorage.getItem('inv-sv'); } catch { return null; } })() || '23');
    const l = mount('pk-s ' + [...V].map(c => 'v' + c).join(' '), `<div class="pk-sb" role="dialog" aria-modal="true" aria-label="Search"><div class="pk-in">${SEARCH}<input type="search" autocomplete="off" spellcheck="false" placeholder="Search assets, countries &amp; articles" aria-label="Search"><kbd>esc</kbd></div><div class="pk-body"><nav class="pk-fl" aria-label="Filters"></nav><div class="pk-r"><div class="pk-none">Loading…</div></div><aside class="pk-pv" aria-live="polite"></aside></div></div>`);
    const inp = l.querySelector('input'), res = l.querySelector('.pk-r'), fl = l.querySelector('.pk-fl'), pv = l.querySelector('.pk-pv'); inp.focus(); let sel = 0, F = 'all', SEC = [];
    const items = () => [...res.querySelectorAll('.pk-i')], mark = () => { items().forEach((e, i) => e.setAttribute('aria-selected', i === sel ? 'true' : 'false')); preview(); };
    const count = k => k === 'all' ? SEC.reduce((n, s) => n + s.items.length, 0) : SEC.filter(s => s.key === k || s.fk === k).reduce((n, s) => n + s.items.length, 0);
    const preview = () => {
      const e = items()[sel], a = e && DATA?.assets.find(x => x.s === e.dataset.a);
      pv.innerHTML = a ? `<div class="pv-h"><span class="ic">${window.AssetIcons ? AssetIcons.icon(a) : ''}</span><div><b>${esc(a.n)}</b><small>${esc(label(a))} · ${kind(a)}</small></div></div><div class="pv-p">${money(a.p, a)}</div>${fmtP(a.d)}<div class="pv-c">${spark(a.sp)}</div>${(a.sp || []).length > 1 ? `<div class="pv-r"><span>1-month low</span><b>${money(Math.min(...a.sp), a)}</b><span>1-month high</span><b>${money(Math.max(...a.sp), a)}</b></div>` : ''}<button type="button" class="pv-go" data-a="${esc(a.s)}">Open ${esc(label(a))}</button>` : '<div class="pk-none">Select a result to preview it.</div>';
    };
    const paint = () => {
      if (!DATA) return; const q = inp.value.trim().toLowerCase(); let h = '';
      SEC = q ? search(q) : [{ key: 'popular', title: 'Popular', items: POP.map(s => DATA.assets.find(a => a.s === s)).filter(Boolean), html: (a, c) => row(a, c), type: 'asset' }];
      fl.innerHTML = FILTERS.filter(([k]) => !q || k === 'all' || count(k)).map(([k, t]) => `<button type="button" class="pk-f${k === F ? ' on' : ''}" data-f="${k}">${t}${q ? `<em>${count(k)}</em>` : ''}</button>`).join('');
      const shown = SEC.filter(s => F === 'all' || s.key === F || s.fk === F || (F === 'stocks' && s.key === 'sectors'));
      for (const s of shown) { const lim = s.key === 'popular' ? 20 : F === 'all' ? (s.key === 'articles' ? 5 : 4) : 40; h += `<h6>${s.title}${q ? `<em>${s.items.length}</em>` : ''}</h6>` + s.items.slice(0, lim).map((x, i) => s.html(x, i === 0 && s.type === 'asset' && F === 'all' && q ? 'top' : '')).join(''); }
      res.classList.toggle('popular', !q); res.scrollTop = 0;
      res.innerHTML = h || `<div class="pk-none">No result for “${esc(inp.value)}”.</div>`; sel = 0; mark();
    };
    load().then(paint); inp.addEventListener('input', () => { F = 'all'; paint(); });
    fl.addEventListener('click', e => { const b = e.target.closest('[data-f]'); if (b) { F = b.dataset.f; paint(); inp.focus(); } });
    const go = s => { close(true); setTimeout(() => open(s), 30); };
    res.addEventListener('click', e => { const b = e.target.closest('[data-a]'); if (b) { go(b.dataset.a); return; } const a = e.target.closest('[data-nav]'); if (a && window.InvGlobeNav) { const [k, v] = [a.dataset.nav.split(':')[0], a.dataset.nav.slice(a.dataset.nav.indexOf(':') + 1)]; e.preventDefault(); if (InvGlobeNav[k] && InvGlobeNav[k](v)) close(true); else location.href = a.href; } });
    res.addEventListener('mousemove', e => { const b = e.target.closest('.pk-i'); if (b) { const i = items().indexOf(b); if (i >= 0 && i !== sel) { sel = i; mark(); } } });
    pv.addEventListener('click', e => { const b = e.target.closest('[data-a]'); if (b) go(b.dataset.a); });
    inp.addEventListener('keydown', e => { const it = items(); if (e.key === 'ArrowDown') { e.preventDefault(); sel = Math.min(sel + 1, it.length - 1); mark(); it[sel]?.scrollIntoView({ block: 'nearest' }); } else if (e.key === 'ArrowUp') { e.preventDefault(); sel = Math.max(sel - 1, 0); mark(); it[sel]?.scrollIntoView({ block: 'nearest' }); } else if (e.key === 'Enter') { e.preventDefault(); it[sel]?.click(); } });
  }
  // ---- wiring ----
  document.addEventListener('click', e => {
    if (e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
    const s = e.target.closest('.search-btn, [data-search], .hn-search, .gsearch, #sbox'); if (s) { e.preventDefault(); e.stopImmediatePropagation(); searchUI(); return; }
    const a = e.target.closest('a[href*="asset.html?s="]'); if (a && !a.closest('.pk')) { const m = /asset\.html\?s=([^&#]+)/.exec(a.getAttribute('href')); if (m) { e.preventDefault(); open(decodeURIComponent(m[1])); } }
  }, true);
  document.addEventListener('keydown', e => { if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); e.stopImmediatePropagation(); searchUI(); } }, true);
  window.InvPeek = { open, search: searchUI, close, panel };
  const m0 = /^#a=(.+)/.exec(location.hash); if (m0) document.addEventListener('DOMContentLoaded', () => open(decodeURIComponent(m0[1]), false));
  const n0 = /^#s=(.+)/.exec(location.hash); if (n0) window.addEventListener('load', () => setTimeout(() => window.InvPeek?.onSector?.(decodeURIComponent(n0[1]), false), 600));
})();
