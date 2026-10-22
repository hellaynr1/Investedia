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
