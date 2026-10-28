# Investedia live relay (Cloudflare Worker)

Streams near-real-time crypto prices (refreshed every ~3 s) through our own subdomain so visitors never connect to a third party.

## Deploy (about 15 minutes, free plan)
1. Create a free Cloudflare account and add the domain `investedia.com` (or use the free `*.workers.dev` address first and skip the domain steps).
2. Install the tool: `npm install -g wrangler`, then `wrangler login`.
3. In this folder run `wrangler deploy`. It prints a URL like `https://investedia-live.<you>.workers.dev`.
4. Optional custom domain: Cloudflare dashboard > Workers & Pages > investedia-live > Settings > Domains & Routes > Add > Custom domain > `live.investedia.com`.
5. Put the final URL in `assets/live-config.js` (`window.INV_LIVE_URL = 'https://live.investedia.com/ticker'`), rebuild and publish.
6. Test: open the URL in a browser; you should see JSON with BTC-USD and others. The Markets > Crypto page shows **Live** when it works.

## Limits and safety
- Free plan: 100,000 requests a day. One shared edge cache means Coinbase is called at most about every 3 seconds per Cloudflare location.
- Only `investedia.com` and `localhost` may call it from a browser (CORS). It stores nothing and logs nothing.
- Data comes from Coinbase Exchange public market data. Keep the attribution line on the Markets page.

## Data API v1 (prices, status; news and globe come next)
- `GET /v1/prices[?group=indices|stocks|currencies|commodities]` -> `{ data: { SYMBOL: [price, change_pct, provider_time_ms, fetched_at_ms] }, meta: { state, fetched_at, age_s, provider, licensed, ttl_s, upstream_ok, version } }`
  `state` is `delayed` (fresh, the provider is 15 minutes delayed), `stale` (snapshot older than 6 minutes: the last good data is still served) or `unavailable` (HTTP 503, the page falls back to its static file).
- `GET /v1/status` -> KV writes today (exact), cron runs/failures, upstream failures, free-plan limits.
- `/ticker` (crypto relay) is unchanged.
- Cron every 2 minutes: all of tier A (133 symbols, 7 Yahoo "spark" calls) plus a rotating slice of tier B (160 of 778 symbols, 8 calls) = about 15 subrequests of the 50 allowed. One combined KV key `px`; a snapshot whose prices did not change is not written (except a heartbeat every 10 minutes); past 900 writes a day it slows to one write per 15 minutes. A failed or empty upstream never overwrites the last good snapshot; symbols are kept up to 7 days.
- Provider code is isolated in `providers/yahoo.js` (not licensed for commercial use, see ../../DATA-LICENSING.md).
- Tests: `cd workers/live && npm test`. CPU benchmark: `npm run bench` (estimate; the real CPU time is in the Cloudflare dashboard after deploy).
- Deploy: `cd ~/Investedia && git pull origin main && cd workers/live && npx wrangler deploy` (free plan; creates the KV namespace on first deploy).
