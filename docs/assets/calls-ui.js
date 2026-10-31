/* Calls UI: shared renderers for Recent market implications, the Track Record and the call page.
   A call = one frozen live prediction from assets/globe/news-ledger.json (outcome-v2: id, sym, name, dir, conf, created, public, start,
   res, move, base, end, ver, recovered...). Article time and event family are joined from the news archive and the event archive.
   Price paths: judged calls use call-paths.json (exchange bars kept permanently by the price robot); pending calls use the live price
   recorder (news-track.json), labelled "recorded so far". Nothing is interpolated: missing data renders as missing. */
(function () {
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const MIN = 60000, HR = 3600000, DAY = 864e5, NEED = 50, SUB = 30;
  const ENGINE = v => ({ 'impact-gemini-v1': 'Prediction Engine v1', 'impact-gemini-v2': 'Prediction Engine v2', 'impact-gemini-v3': 'Prediction Engine v3' })[v] || 'Prediction Engine v1';
  const RES = { hit: ['ok', '✓', 'Hit'], miss: ['no', '✕', 'Miss'], flat: ['na', '–', 'No clear move'], pending: ['wait', '◷', 'Waiting for price'], unresolved: ['na', '?', 'Unresolved'], void: ['na', '!', 'Excluded'] };
  const FAM = { earnings: 'Earnings', guidance: 'Guidance', 'm&a': 'M&A', regulation: 'Regulation', rates: 'Rates', 'macro-data': 'Macro data', 'commodity-prices': 'Commodities', 'energy-supply': 'Energy supply', geopolitics: 'Geopolitics', crypto: 'Crypto', capital: 'Capital markets', trade: 'Trade', labor: 'Labour', other: 'Other' };
  const ago = t => { const m = Math.round((Date.now() - t) / MIN); return m < 60 ? `${m} min ago` : m < 1440 ? `${Math.round(m / 60)} h ago` : `${Math.round(m / 1440)} d ago`; };
  const when = t => new Date(t).toLocaleString('en-GB', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZone: 'UTC' }) + ' UTC';
  const pct = v => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toFixed(2) + '%';
  const tk = c => (c.sym || '').replace(/-USD$/, '').replace(/=X$/, '');
  const badge = c => { const [k, i, l] = RES[c.res] || RES.pending; return `<span class="cx-badge ${k}">${i} ${l}</span>`; };
  const said = c => `<span class="cx-said ${c.dir}">${c.dir === 'up' ? 'Long' : 'Short'}</span>`;
  const conf = c => c.conf ? `<span class="cx-conf">${esc(c.conf)} confidence</span>` : '';
  const start = c => Date.parse(c.start || c.created);
  // result of the call, not the asset's move: "down" is read as sold, so a fall is a gain and a rise is a loss
  const gain = c => Number.isFinite(c.move) ? (c.dir === 'down' ? -c.move : c.move) : null;
  const moved = c => `${esc(c.name)} ${c.move > 0 ? 'rose' : c.move < 0 ? 'fell' : 'was unchanged'}${c.move ? ' ' + Math.abs(c.move).toFixed(2) + '%' : ''}`;
  const resBox = (c, big) => { const g = gain(c); if (g === null) return `<span class="cx-rb na${big ? ' big' : ''}"><b>—</b><small>${c.res === 'pending' ? 'waiting' : 'no result'}</small></span>`;
    return `<span class="cx-rb ${c.res === 'flat' ? 'na' : g > 0 ? 'up' : 'dn'}${big ? ' big' : ''}" title="${moved(c)}"><b>${pct(g)}</b></span>`; };

  // load the ledger and its joins; returns live calls (legacy calls never count as live)
  async function load(root = 'assets/globe/') {
    const get = u => fetch(root + u, { cache: 'no-cache' }).then(r => r.ok ? r.json() : {}).catch(() => ({}));
    const [L, P, T, A] = await Promise.all([get('news-ledger.json'), get('call-paths.json'), get('news-track.json'), get('news-archive.json')]);
    const calls = (L.calls || []).filter(c => c && !c.legacy && c.sym && (c.dir === 'up' || c.dir === 'down'));
    const days = [...new Set(calls.map(c => (c.start || c.created || '').slice(0, 10)).filter(Boolean))];
    const ev = await Promise.all(days.map(d => get(`events/${d}.json`)));
    const fam = {}; ev.forEach(e => (e.events || []).forEach(x => { fam[x.id] = x.fam; }));
    const art = {}; (A.stories || []).forEach(s => { art[s.id] = s; });
    for (const c of calls) {
      const s = art[c.id]; c.art = (c.art ? Date.parse(c.art) : null) || (s && Date.parse(s.published_at)) || null;  // first-seen article time (git) beats the archive, whose time moves when sources merge c.src = s && s.source && (s.source.name || s.source) || null;
      c.url = s && (s.url || (s.source && s.source.url)) || null; c.fam = fam[c.id] || null; c.t = start(c);
      const p = P[c.id + '|' + c.sym];
      c.path = p ? { pts: p.pts, src: 'exchange bars' } : (T.s && T.s[c.sym] ? { pts: T.s[c.sym], src: 'recorded so far' } : null);
    }
    return { calls: calls.sort((a, b) => b.t - a.t), rule: L.outcome_rule, live_since: L.live_since };
  }
  const inWin = (c, days) => !days || c.t >= Date.now() - days * DAY;
  const counts = cs => { const n = { hit: 0, miss: 0, flat: 0, pending: 0, unresolved: 0, void: 0 }; cs.forEach(c => { n[c.res] = (n[c.res] || 0) + 1; }); n.judged = n.hit + n.miss + n.flat; n.clear = n.hit + n.miss; return n; };
  // accuracy only above the sample threshold, always with its sample size
  const acc = (n, need) => n.judged >= need && n.clear ? { pct: Math.round(100 * n.hit / n.clear), text: `${n.hit} of ${n.clear} directional calls correct${n.flat ? ` · ${n.flat} no clear move` : ''}` } : null;

  // chart: verified price path; markers for the article, the proven call time, baseline and outcome. Trading-time axis (no flat weekends).
  function chart(c, o = {}) {
    const W = o.w || 300, H = o.h || 70, big = !!o.big, pad = big ? [16, 16, 26, 56] : [6, 4, 6, 4];
    const t0 = Math.min(c.t, c.art || c.t), raw = (c.path && c.path.pts || []).map(([m, p]) => [m * MIN, p]).sort((a, b) => a[0] - b[0]);
    const tEnd = c.end ? c.end[0] * MIN : Infinity, pts = raw.filter(([t]) => t >= t0 - (big ? 12 : 6) * HR && t <= tEnd + (big ? 2 * HR : 0));
    if (pts.length < 3) return `<div class="cx-chart empty" style="height:${H}px"><span>${c.res === 'pending' ? 'Waiting for prices after the call' : 'No verified price path stored for this call'}</span></div>`;
    const ps = pts.map(p => p[1]).concat(c.base ? [c.base[1]] : [], c.end ? [c.end[1]] : []), lo = Math.min(...ps), hi = Math.max(...ps), span = (hi - lo) || hi * .01;
    const idx = t => { let k = pts.findIndex(p => p[0] >= t); if (k < 0) return pts.length - 1; if (k === 0) return 0; const a = pts[k - 1][0], b = pts[k][0]; return k - 1 + (t - a) / ((b - a) || 1); };
    const X = t => pad[3] + idx(t) / (pts.length - 1) * (W - pad[1] - pad[3]), Y = p => pad[0] + (1 - (p - lo) / span) * (H - pad[0] - pad[2]);
    const before = pts.filter(p => p[0] <= c.t), after = pts.filter(p => p[0] >= c.t);
    const line = arr => arr.map((p, i) => `${i ? 'L' : 'M'}${X(p[0]).toFixed(1)},${Y(p[1]).toFixed(1)}`).join('');
    const col = { hit: 'var(--up)', miss: 'var(--down)', pending: '#F5A524' }[c.res] || '#a1a1aa', xs = X(c.t);
    let s = `<svg class="cx-chart" viewBox="0 0 ${W} ${H}" width="100%" height="${H}" role="img" aria-label="Price of ${esc(c.name)} around the call">`;
    if (big) for (let k = 0; k <= 3; k++) { const p = lo + span * k / 3, y = Y(p); s += `<line x1="${pad[3]}" x2="${W - pad[1]}" y1="${y}" y2="${y}" class="cx-grid"/><text x="${pad[3] - 8}" y="${y + 4}" class="cx-ax" text-anchor="end">${p.toFixed(p < 10 ? 4 : 2)}</text>`; }
    if (after.length > 1) s += `<path d="${line(after)} L${X(after.at(-1)[0]).toFixed(1)},${H - pad[2]} L${X(after[0][0]).toFixed(1)},${H - pad[2]}Z" fill="${col}" opacity="${c.res === 'pending' ? .04 : .08}"/>`;
    s += `<path d="${line(before.length ? [...before, after[0] || before.at(-1)] : [])}" class="cx-pre"/><path d="${line(after)}" fill="none" stroke="${col}" stroke-width="${big ? 2 : 1.6}" stroke-linejoin="round"/>`;
    if (c.art && Math.abs(c.art - c.t) > 5 * MIN && c.art >= pts[0][0]) { const xa = X(c.art); s += `<line x1="${xa}" x2="${xa}" y1="${pad[0] - 2}" y2="${H - pad[2]}" class="cx-mark"/>`; if (big) s += `<text x="${xa - 6}" y="${pad[0] + 8}" class="cx-lbl" text-anchor="end">Article posted</text>`; }
    s += `<line x1="${xs}" x2="${xs}" y1="${pad[0] - 2}" y2="${H - pad[2]}" class="cx-mark call"/>`;
    if (big) s += `<text x="${xs + 6}" y="${pad[0] + 8}" class="cx-lbl">${c.art && Math.abs(c.art - c.t) > 5 * MIN ? 'Investedia call (proven)' : 'Article posted · Investedia call'}</text>`;
    if (c.base) s += `<circle cx="${X(c.base[0] * MIN)}" cy="${Y(c.base[1])}" r="${big ? 4 : 2.6}" fill="#e4e4e7" stroke="#0A0A0B" stroke-width="2"/>`;
    if (c.end) { const ex = X(c.end[0] * MIN), ey = Y(c.end[1]); s += `<circle cx="${ex}" cy="${ey}" r="${big ? 5 : 3.2}" fill="${col}" stroke="#0A0A0B" stroke-width="2"/>`; if (big) s += `<text x="${ex - 8}" y="${ey - 10}" class="cx-lbl" text-anchor="end">Call result ${pct(gain(c) || 0)}</text>`; }
    if (big) s += `<text x="${pad[3]}" y="${H - 6}" class="cx-ax">${esc(when(pts[0][0]))}</text><text x="${W - pad[1]}" y="${H - 6}" class="cx-ax" text-anchor="end">${esc(when(pts.at(-1)[0]))}</text>`;
    return s + '</svg>';
  }
  const href = c => `call.html?id=${encodeURIComponent(c.id)}&sym=${encodeURIComponent(c.sym)}`;
  function card(c) {
    return `<a class="cx-card" href="${href(c)}">
      <div class="cx-top"><span class="cx-tk">${esc(tk(c))}</span><span class="cx-name">${esc(c.name)}</span>${badge(c)}</div>
      <h3 class="cx-h">${esc(c.h)}</h3>
      <div class="cx-meta">${said(c)}${conf(c)}<span class="cx-t" title="${esc(when(c.t))}">${c.art ? 'article ' + esc(when(c.art)) : esc(when(c.t))}</span>${resBox(c)}</div>
      ${chart(c)}</a>`;
  }
  const due = c => { const d = c.t + 24 * HR; return d > Date.now() ? `checked in ~${Math.max(1, Math.round((d - Date.now()) / HR))} h` : 'waiting for its market to reopen'; };
  const row = c => `<a class="tr2-row" href="${href(c)}"><small class="tr2-when">${esc(when(c.t))}</small><span><h4>${esc(c.h)}</h4><small><span class="cx-tk">${esc(tk(c))}</span> ${esc(c.name)} · ${said(c)}${c.conf ? ' · ' + esc(c.conf) : ''}${c.res === 'pending' ? ' · ' + due(c) : ''}</small></span>${Number.isFinite(c.move) ? resBox(c) : '<span></span>'}${badge(c)}</a>`;
  function detail(c) {
    const rows = [['Asset', `${esc(c.name)} · <b>${esc(tk(c))}</b>`], ['Article posted', c.art ? esc(when(c.art)) : '<span class="muted">not in the news archive</span>'],
      ['Investedia call (proven start)', esc(when(c.t))], ['Prediction', said(c)], ['Confidence', c.conf ? esc(c.conf) : '<span class="muted">not recorded</span>'],
      ['Baseline', c.base ? `${c.base[1]} · ${esc(when(c.base[0] * MIN))}` : '<span class="muted">—</span>'],
      ['Call result', c.end ? `${resBox(c, true)} <span class="muted">measured ${esc(when(c.end[0] * MIN))}</span>` : c.res === 'pending' ? esc(due(c)) : esc(c.why || '—')], ['Result', badge(c)],
      ['Model', `Investedia Prediction Model · <span class="muted">${esc(ENGINE(c.ver))}</span>`], c.fam ? ['Event type', esc(FAM[c.fam] || c.fam)] : null];
    return `<div class="cx-detail"><div class="cx-dh"><span class="cx-tk">${esc(tk(c))}</span>${badge(c)}</div>
      <h2>${c.url ? `<a href="${esc(c.url)}" rel="noopener" target="_blank">${esc(c.h)} ↗</a>` : `<a href="story.html?id=${encodeURIComponent(c.id)}">${esc(c.h)}</a>`}</h2>
      ${c.src ? `<p class="cx-fine" style="margin:-8px 0 12px">${esc(c.src)}</p>` : ''}
      <div class="cx-bigchart">${chart(c, { w: 720, h: 280, big: true })}${c.path ? `<p class="cx-fine">Price path: ${esc(c.path.src === 'exchange bars' ? 'traded prices from the asset’s own exchange session (5-minute bars, thinned to 30 minutes), stored when the call was judged' : 'prices recorded by Investedia’s price robot so far; the full path is stored when the call is judged')}. Nothing is interpolated.</p>` : ''}</div>
      <dl class="cx-dl">${rows.filter(Boolean).map(([k, v]) => `<div><dt>${k}</dt><dd>${v}</dd></div>`).join('')}</dl>
      <p class="cx-fine">Call result reads the call as a position: a long gains when the price rises, a short gains when it falls. The call was frozen before its outcome and is scored from the earliest time it can be proven public. No exit or target signal was recorded for this call, so none is shown.</p></div>`;
  }
  window.CallsUI = { gain, resBox, esc, load, inWin, counts, acc, chart, card, row, detail, badge, said, conf, ago, when, pct, ENGINE, FAM, MIN, DAY, NEED, SUB };
})();
