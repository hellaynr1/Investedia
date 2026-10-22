// Investedia live crypto relay (Cloudflare Worker, free plan).
// Visitors call THIS worker (our own subdomain), not Coinbase, so no third party sees their IP.
// One edge-cached snapshot of Coinbase's public market data (top 100 coins) is shared by everyone and refreshed at most every 3 seconds.
const ALLOWED = ['https://investedia.com', 'https://www.investedia.com'];
const TTL = 3, TOP = 100;

const cors = (req) => {
  const o = req.headers.get('Origin') || '';
  const ok = ALLOWED.includes(o) || /^http:\/\/localhost(:\d+)?$/.test(o);
  return { 'Access-Control-Allow-Origin': ok ? o : ALLOWED[0], 'Vary': 'Origin', 'Access-Control-Allow-Methods': 'GET, OPTIONS', 'Access-Control-Max-Age': '86400' };
};

// One call returns every Coinbase spot product with price, 24h change, 24h range, volume and market cap.
async function snapshot() {
  const out = {};
  try {
    const r = await fetch('https://api.coinbase.com/api/v3/brokerage/market/products?product_type=SPOT&limit=1000', { headers: { 'User-Agent': 'Investedia live relay (info@investedia.com)' } });
    if (!r.ok) throw new Error(String(r.status));
    const rows = ((await r.json()).products || []).filter(x => x.quote_currency_id === 'USD' && !x.is_disabled && !x.trading_disabled && +x.price > 0 && +x.approximate_quote_24h_volume > 0 && !/^(USDT|USDC|DAI|PYUSD|EURC|GUSD|PAX|TUSD)$/.test(x.base_currency_id));
    rows.sort((x, y) => (+y.market_cap || 0) - (+x.market_cap || 0) || (+y.approximate_quote_24h_volume) - (+x.approximate_quote_24h_volume));
    for (const x of rows.slice(0, TOP)) out[x.product_id] = { p: +x.price, pc: +x.price_percentage_change_24h || 0, h: +x.high_24h || null, l: +x.low_24h || null, v: Math.round(+x.approximate_quote_24h_volume || 0), mc: Math.round(+x.market_cap || 0), n: (x.base_name || x.base_currency_id).replace(/\s+/g, ' ').trim() };
  } catch { /* upstream error: return what we have (nothing) so the caller serves 503 and the page falls back */ }
  return { t: Date.now(), source: 'Coinbase public market data', ttl: TTL, p: out };
}

// ---- Non-crypto prices: a cron job refreshes a rotating batch from Yahoo's free chart feed and saves one snapshot in KV. ----
import { TIER_A, TIER_B } from './symbols.js';
const UA_Y = 'Mozilla/5.0 (compatible; Investedia/1.0; +https://investedia.com)';
async function quote(entry) {
  const [site, y, inv] = entry.split('|');
  try {
    const r = await fetch(`https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(y)}?range=1d&interval=1d`, { headers: { 'User-Agent': UA_Y } });
    if (!r.ok) return null;
    const m = (await r.json())?.chart?.result?.[0]?.meta, p = m?.regularMarketPrice, prev = m?.chartPreviousClose ?? m?.previousClose;
    if (!(p > 0) || !(prev > 0)) return null;
    const d = (p / prev - 1) * 100 * (inv === '1' ? -1 : 1);
    return [site, [+p.toFixed(6), +d.toFixed(2), m.regularMarketDayHigh ?? null, m.regularMarketDayLow ?? null, m.regularMarketVolume ?? null, (m.regularMarketTime || 0) * 1000]];
  } catch { return null; }
}
const pick = (list, from, n) => { const out = []; for (let i = 0; i < Math.min(n, list.length); i++) out.push(list[(from + i) % list.length]); return out; };
export async function refresh(env, now = Date.now()) {
  const a = +env.BATCH_A || 30, b = +env.BATCH_B || 15;
  let snap = {}; try { snap = JSON.parse(await env.PRICES.get('px')) || {}; } catch {}
  const cur = snap.cur || { a: 0, b: 0 }, p = snap.p || {};
  const batch = [...pick(TIER_A, cur.a, a), ...pick(TIER_B, cur.b, b)];
  const got = (await Promise.all(batch.map(quote))).filter(Boolean);
  for (const [site, v] of got) p[site] = [...v, now];
  const next = { t: now, cur: { a: (cur.a + a) % TIER_A.length, b: (cur.b + b) % TIER_B.length }, p };
  if (got.length) await env.PRICES.put('px', JSON.stringify(next));
  return { fetched: batch.length, ok: got.length };
}

export default {
  async scheduled(event, env, ctx) { ctx.waitUntil(refresh(env)); },
  async fetch(req, env, ctx) {
    const h = cors(req), url = new URL(req.url);
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: h });
    if (req.method === 'GET' && url.pathname === '/prices') {
      let body = await env.PRICES?.get('px');
      if (!body) return new Response(JSON.stringify({ error: 'no data yet' }), { status: 503, headers: { ...h, 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } });
      const snap = JSON.parse(body); delete snap.cur;
      return new Response(JSON.stringify(snap), { headers: { ...h, 'Content-Type': 'application/json', 'Cache-Control': 'public, max-age=30' } });
    }
    if (req.method === 'GET' && url.pathname === '/probe') { // temporary check: can this Worker read Yahoo's free chart feed? Fixed symbols only.
      const out = {};
      for (const sym of ['^GSPC', 'AAPL', 'EURUSD=X']) {
        try { const r = await fetch(`https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(sym)}?range=1d&interval=5m`, { headers: { 'User-Agent': 'Mozilla/5.0 (compatible; Investedia/1.0; +https://investedia.com)' } }); const j = r.ok ? await r.json() : null; out[sym] = { status: r.status, price: j?.chart?.result?.[0]?.meta?.regularMarketPrice ?? null }; } catch (e) { out[sym] = { error: String(e) }; }
      }
      return new Response(JSON.stringify(out), { headers: { ...h, 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } });
    }
    if (req.method !== 'GET' || url.pathname !== '/ticker') return new Response('Not found', { status: 404, headers: h });
    const cache = caches.default, key = new Request(url.origin + '/__ticker', { method: 'GET' });
    let res = await cache.match(key);
    if (!res) {
      const snap = await snapshot();
      if (!Object.keys(snap.p).length) return new Response(JSON.stringify({ error: 'upstream unavailable' }), { status: 503, headers: { ...h, 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } });
      res = new Response(JSON.stringify(snap), { headers: { 'Content-Type': 'application/json', 'Cache-Control': `public, max-age=${TTL}` } });
      ctx.waitUntil(cache.put(key, res.clone()));
    }
    const body = await res.text();
    return new Response(body, { headers: { ...h, 'Content-Type': 'application/json', 'Cache-Control': `public, max-age=${TTL}` } });
  }
};
