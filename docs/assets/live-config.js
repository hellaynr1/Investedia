// URL of the live relay worker (see workers/live/README.md). Empty = the relay is not deployed yet.
window.INV_LIVE_URL = window.INV_LIVE_URL || 'https://investedia-live.adonaykabeya10.workers.dev/ticker';

// Where frequently changing prices come from: 'worker' = the Cloudflare Worker /v1 API with the static GitHub files as fallback (visitor consent for live data required), 'shadow' = compare only, 'static' = GitHub files only.
window.INV_DATA_MODE = window.INV_DATA_MODE || 'worker';
