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

// ---- Non-crypto prices, news and globe: /v1 (see v1/). Provider adapters live in providers/. ----
import { refresh, handlePrices, handleStatus } from './v1/prices.js';
export { refresh };
const json = (h, status, body, cache = 'no-store') => new Response(JSON.stringify(body), { status, headers: { ...h, 'Content-Type': 'application/json', 'Cache-Control': cache } });

export default {
  async scheduled(event, env, ctx) { ctx.waitUntil(refresh(env).then(r => console.log(JSON.stringify({ cron: 'prices', ok: r.ok, sent: r.sent, wrote: r.wrote, changed: r.changed, reason: r.reason }))).catch(e => console.log(JSON.stringify({ cron: 'prices', error: String(e).slice(0, 200) })))); },
  async fetch(req, env, ctx) {
    const h = cors(req), url = new URL(req.url);
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: h });
    if (req.method === 'GET' && (url.pathname === '/v1/prices' || url.pathname === '/v1/status')) {
      // 15 s shared edge cache in front of KV: many visitors cost one KV read per location per 15 s
      const cache = caches.default, key = new Request(url.origin + url.pathname + url.search + '#v1', { method: 'GET' });
      const hit = await cache.match(key);
      if (hit) return new Response(await hit.text(), { headers: { ...h, 'Content-Type': 'application/json', 'Cache-Control': 'public, max-age=15', 'X-Inv-Cache': 'hit' } });
      let r;
      try { r = url.pathname === '/v1/prices' ? await handlePrices(url, env, ctx) : await handleStatus(env); }
      catch (e) { console.log(JSON.stringify({ route: url.pathname, error: String(e).slice(0, 200) })); r = { status: 500, body: { error: 'internal', meta: { state: 'unavailable', version: 1 } } }; }
      const res = json(h, r.status, r.body, r.status === 200 ? 'public, max-age=15' : 'no-store');
      if (r.status === 200) { res.headers.set('X-Inv-State', r.body.meta?.state || 'ok'); ctx.waitUntil(cache.put(key, new Response(JSON.stringify(r.body), { headers: { 'Content-Type': 'application/json', 'Cache-Control': 'public, max-age=15' } }))); }
      return res;
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
