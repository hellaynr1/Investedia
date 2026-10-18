// Display sourced snapshots in the existing page components, without changing layout.
(() => {
  const H = window.HOME_DATA || {}, M = window.MOCK, U = window.UI;
  const $ = id => document.getElementById(id);
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  const safeURL = u => { try { const x = new URL(u); return x.protocol === 'https:' ? x.href : '#'; } catch { return '#'; } };
  const date = d => d ? new Date(d).toLocaleString('en-GB', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' }) : 'Unavailable';
  const money = v => Number.isFinite(v) ? '$' + (v >= 1e12 ? (v / 1e12).toFixed(2) + 'T' : v >= 1e9 ? (v / 1e9).toFixed(2) + 'B' : v.toLocaleString()) : '—';
  const pct = v => Number.isFinite(v) ? v.toFixed(1) + '%' : '—';
  const empty = text => `<p class="card-pad muted" style="margin:0">${esc(text || 'Verified data unavailable')}</p>`;
  const source = d => d ? `<a class="dim" href="${safeURL(d.url)}" target="_blank" rel="noopener" style="font-size:11px">${esc(d.source)} · ${esc(date(d.asof))}</a>` : '';
  const stats = (rows, d) => rows.map(([k, v]) => `<div class="stat"><span>${esc(k)}</span><b>${esc(v)}</b></div>`).join('') + `<div class="stat">${source(d)}</div>`;
  const upcoming = () => M.calendar.filter(e => Date.parse(e.date) >= Date.now());
  const g = H.crypto, f = H.fear;
  const cryptoRows = [['Total market cap', money(g?.cap)], ['24h volume', money(g?.volume)], ['Bitcoin dominance', pct(g?.btc)], ['Ethereum dominance', pct(g?.eth)], ['Fear & Greed', f ? `${f.value} · ${f.label}` : '—']];
  if ($('crypto-stats')) $('crypto-stats').innerHTML = stats(cryptoRows, g) + `<div class="stat">${source(f)}</div>`;
  if (location.pathname.endsWith('crypto.html')) {
    $('stats').innerHTML = stats(cryptoRows, g) + `<div class="stat">${source(f)}</div>`;
    if (g) {
      const dom = [['Bitcoin', g.btc, '#f7931a'], ['Ethereum', g.eth, '#627eea'], ['Others', 100 - g.btc - g.eth, '#52525b']];
      let acc = 0; const C = 2 * Math.PI * 70;
      $('donut').innerHTML = `<svg viewBox="0 0 200 200" style="width:190px;height:190px"><g transform="rotate(-90 100 100)">${dom.map(([n, v, c]) => { const d = acc; acc += v; return `<circle cx="100" cy="100" r="70" fill="none" stroke="${c}" stroke-width="26" stroke-dasharray="${v / 100 * C} ${C}" stroke-dashoffset="${-d / 100 * C}"/>`; }).join('')}</g><text x="100" y="96" text-anchor="middle" font-size="24" fill="#fff">${pct(g.btc)}</text></svg>`;
      $('dom-legend').innerHTML = dom.map(([n, v]) => `<div style="display:flex;justify-content:space-between"><span>${n}</span><span class="num">${pct(v)}</span></div>`).join('');
    }
    $('defi-t').innerHTML = '<tr><td colspan="4">Verified protocol data unavailable</td></tr>';
    document.querySelector('#defi .meta').textContent = 'Source not connected';
    document.querySelector('#stablecoins .meta').textContent = 'Supply data unavailable';
    const pad = document.querySelector('#stablecoins > .card-pad');
    if (pad) pad.innerHTML = empty('Verified supply breakdown unavailable');
  }
  if ($('sectors')) {
    const rows = H.sectors?.items || [], max = Math.max(1, ...rows.map(r => Math.abs(r.change)));
    $('sectors').innerHTML = rows.map(r => `<div style="display:grid;grid-template-columns:110px 1fr 64px;gap:10px;align-items:center;font-size:13px"><span class="muted">${esc(r.name)}</span><div style="position:relative;height:16px"><div style="position:absolute;left:50%;top:0;bottom:0;width:1px;background:var(--line)"></div><div style="position:absolute;top:2px;bottom:2px;border-radius:2px;${r.change >= 0 ? 'left' : 'right'}:50%;width:${Math.abs(r.change) / max * 50}%;background:var(--${r.change >= 0 ? 'up' : 'down'})"></div></div><span class="num ${U.cls(r.change)}" style="text-align:right">${U.fmtC(r.change)}</span></div>`).join('') + source(H.sectors);
    if ($('sector-asof')) $('sector-asof').textContent = 'ETF proxies · latest session';
  }
  if ($('tm-sub')) $('tm-sub').textContent = 'Delayed quotes · feed fetched ' + date(window.QUOTES?.updated);
  if ($('next-real-event')) { const e = upcoming()[0]; $('next-real-event').textContent = e ? `${e.e} · ${date(e.date)}` : 'No verified upcoming event'; }
  if ($('events')) $('events').innerHTML = upcoming().slice(0, 6).map(e => `<a class="news-item" href="${safeURL(e.url || H.calendar?.url)}" target="_blank" rel="noopener" style="grid-template-columns:86px 1fr auto;gap:12px"><span><b class="num">${esc(e.time)}</b><small class="dim" style="display:block">${esc(e.day)}</small></span><span><b>${esc(e.e)}</b><small class="dim" style="display:block">${esc(e.c)} · Forecast ${esc(e.fc)} · Prev. ${esc(e.prev)}</small></span>${U.impact(e.imp)}</a>`).join('') + source(H.calendar);
  if ($('earn')) $('earn').innerHTML = M.earnings.filter(e => e.iso >= new Date().toISOString().slice(0, 10)).slice(0, 6).map(e => `<a class="news-item" href="${safeURL(H.earnings?.url)}" target="_blank" rel="noopener"><span><b>${esc(e.n)}</b><small class="dim" style="display:block">${esc(e.date)} · ${esc(e.when)}</small></span><span class="num muted">EPS est. ${esc(e.eps)}</span></a>`).join('') + source(H.earnings);
  if ($('an-cards')) $('an-cards').innerHTML = M.news.slice(7, 10).map((n, i) => `<a class="card n-card" href="${safeURL(n.url)}" target="_blank" rel="noopener"><div class="cover">${U.cover('report' + i)}</div><div class="body"><div class="news-meta"><span class="tag">${esc(n.cat)}</span></div><h3>${esc(n.t)}</h3><p>${esc(n.d)}</p><div class="news-meta">${esc(n.a)} · ${esc(n.time)}</div></div></a>`).join('') || empty('No sourced reports available');
  if ($('quotes')) $('quotes').innerHTML = empty('Have feedback? Share your experience with Investedia.');
  // Per-instrument provenance is available wherever a price appears.
  document.querySelectorAll('[data-lp]').forEach(el => {
    const a = M.bySym[el.dataset.lp]; if (!a) return;
    const q = window.QUOTES?.q[a.s];
    el.title = `${a.source} · ${q?.symbol || a.s} · ${a.cur || 'currency unconfirmed'} · ${date(q?.asof || (q?.t ? new Date(q.t * 1000).toISOString() : null))}${a.fetchFailed ? ' · refresh failed; last known quote' : ''}`;
  });
  const status = () => {
    if (!$('a-time')) return;
    const a = M.bySym[new URLSearchParams(location.search).get('s') || 'NVDA']; if (!a) return;
    const q = window.QUOTES?.q[a.s];
    $('a-time').textContent = a.live && Date.now() - (a.liveAt || 0) < 60000 ? 'Live · Coinbase · ' + date(new Date(a.liveAt).toISOString()) : a.real ? `${a.freq === 'monthly' ? 'Monthly average' : 'Delayed snapshot'} · ${date(q?.asof || (q?.t ? new Date(q.t * 1000).toISOString() : null))}` : 'Verified price unavailable';
  };
  status(); document.addEventListener('inv:tick', status);
})();
