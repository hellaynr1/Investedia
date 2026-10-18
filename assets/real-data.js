// Normalize sourced data before any page renders. Unknown fields stay unavailable.
(() => {
  const M = window.MOCK, Q = window.QUOTES?.q || {}, H = window.HOME_DATA || {};
  const number = v => typeof v === 'number' && Number.isFinite(v);
  const stamp = x => x?.asof || x?.fetched;
  M.assets.forEach(a => {
    const q = Q[a.s], f = H.active?.items?.[a.s];
    a.m = number(f?.cap) ? f.cap / 1e9 : number(H.coins?.items?.[a.s]?.cap) ? H.coins.items[a.s].cap / 1e9 : null;
    a.pe = number(f?.pe) ? f.pe : null;
    a.g = null; a.div = null; a.aum = '—'; a.fee = '—';
    a.vol = q?.v ? (q.v >= 1e9 ? (q.v / 1e9).toFixed(1) + 'B' : q.v >= 1e6 ? (q.v / 1e6).toFixed(1) + 'M' : q.v.toLocaleString()) : '—';
    a.real = !!q && number(q.p) && q.p > 0;
    if (!a.real) { a.p = NaN; a.d = NaN; a.w = NaN; a.m1 = NaN; }
    a.spark = q?.sp?.length > 2 ? q.sp : [];
    a.source = q?.source || (q?.freq ? 'FRED' : 'Yahoo Finance');
    a.fetchFailed = !!q?.fetch_failed;
    a.open = q?.open; a.prev = q?.prev;
    if (q?.exchange) a.x = q.exchange;
    if (q?.freq === 'monthly') { a.d = NaN; a.w = NaN; }
  });
  // Preserve the public helpers, but never synthesize financial history.
  M.decorativeSeries = M.series;
  M.series = () => [];
  M.ohlc = () => [];
  M.news = window.NEWS?.items?.length ? M.news.filter(n => n.url) : [];
  
  M.calendar = (H.calendar?.items || []).map(e => ({
    date: e.date, day: new Date(e.date).toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short' }),
    time: new Date(e.date).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: 'UTC' }) + ' UTC',
    c: e.country, e: e.title, imp: Math.max(1, Math.min(3, (e.importance ?? 0) + 1)),
    act: e.actual ?? '—', fc: e.forecast ?? '—', prev: e.previous ?? '—', source: e.source, url: e.source_url
  })).filter(e => Number.isFinite(Date.parse(e.date))).sort((a, b) => Date.parse(a.date) - Date.parse(b.date));
  M.earnings = (H.earnings?.items || []).map(e => ({ s: e.symbol, n: e.name, iso: e.date,
    date: new Date(e.date + 'T12:00:00Z').toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short' }),
    when: ({ 'time-pre-market': 'Before open', 'time-after-hours': 'After close' })[e.time] || 'Time unconfirmed',
    eps: e.epsForecast || '—', rev: '—' }));
  M.feedStamp = stamp;
})();
