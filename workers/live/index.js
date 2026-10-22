// Investedia live crypto relay (Cloudflare Worker, free plan).
// Visitors call THIS worker (our own subdomain), not Coinbase, so no third party sees their IP.
// One edge-cached snapshot of Coinbase's public 24h stats is shared by everyone and refreshed at most every 3 seconds.
const PRODUCTS = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'XRP-USD', 'BNB-USD', 'DOGE-USD', 'ADA-USD', 'TRX-USD', 'AVAX-USD', 'LINK-USD', 'DOT-USD', 'LTC-USD'];
const ALLOWED = ['https://investedia.com', 'https://www.investedia.com'];
const TTL = 3;

const cors = (req) => {
  const o = req.headers.get('Origin') || '';
  const ok = ALLOWED.includes(o) || /^http:\/\/localhost(:\d+)?$/.test(o);
  return { 'Access-Control-Allow-Origin': ok ? o : ALLOWED[0], 'Vary': 'Origin', 'Access-Control-Allow-Methods': 'GET, OPTIONS', 'Access-Control-Max-Age': '86400' };
};

async function snapshot() {
  const out = {};
  await Promise.all(PRODUCTS.map(async (id) => {
    try {
      const r = await fetch(`https://api.exchange.coinbase.com/products/${id}/stats`, { headers: { 'User-Agent': 'Investedia live relay (info@investedia.com)' } });
      if (!r.ok) return;
      const s = await r.json(), p = +s.last, o = +s.open;
      if (p > 0 && o > 0) out[id] = { p, o, h: +s.high, l: +s.low };
    } catch { /* skip this product this round */ }
  }));
  return { t: Date.now(), source: 'Coinbase Exchange public data', ttl: TTL, p: out };
}

export default {
  async fetch(req, env, ctx) {
    const h = cors(req), url = new URL(req.url);
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: h });
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
