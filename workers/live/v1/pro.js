// Investedia Pro billing and entitlement (Stripe Billing + Supabase Auth). SANDBOX FIRST.
// Every /v1/pro/* route returns 404 unless env.PRO_ENABLED === 'true'. Live Stripe keys (sk_live_...) are refused unless
// env.PRO_LIVE === 'true' (owner approval). Secrets come only from Worker secrets: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET,
// SUPABASE_SERVICE_KEY. Plain vars: SUPABASE_URL, SUPABASE_ANON_KEY, STRIPE_PRICE_MONTHLY, STRIPE_PRICE_YEARLY, SITE_URL.
//   POST /v1/pro/checkout {plan:'monthly'|'yearly'}  (signed-in)  -> { url }  hosted Checkout, 7-day trial, Stripe Tax
//   POST /v1/pro/portal                             (signed-in)  -> { url }  Stripe customer portal
//   GET  /v1/pro/me                                 (signed-in)  -> { pro, status, plan, trial_end, current_period_end, cancel_at_period_end }
//   POST /v1/pro/webhook                            (Stripe)     -> 200 after signature check; idempotent; ignores out-of-order events
export const TRIAL_DAYS = 7, GRACE_DAYS = 3;
const enc = new TextEncoder();

// ---------- entitlement ----------
export function isPro(sub, now = Date.now()) {
  if (!sub) return false;
  if (sub.status === 'trialing' || sub.status === 'active') return true;
  if (sub.status === 'past_due' && sub.past_due_since) return now < Date.parse(sub.past_due_since) + GRACE_DAYS * 864e5;
  return false;
}

// ---------- Stripe webhook signature (t=..., v1=... ; HMAC-SHA256 over "t.payload") ----------
const hex = (buf) => [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('');
export async function verifyStripe(payload, header, secret, toleranceSec = 300, nowSec = Math.floor(Date.now() / 1000)) {
  if (!header || !secret) return false;
  const parts = Object.fromEntries(header.split(',').map(p => p.split('=')).filter(p => p.length === 2).map(([k, v]) => [k.trim(), v.trim()]));
  const sigs = header.split(',').filter(p => p.trim().startsWith('v1=')).map(p => p.trim().slice(3));
  const t = Number(parts.t);
  if (!t || !sigs.length || Math.abs(nowSec - t) > toleranceSec) return false;
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const expected = hex(await crypto.subtle.sign('HMAC', key, enc.encode(`${t}.${payload}`)));
  return sigs.some(s => s.length === expected.length && timingSafeEqual(s, expected));
}
function timingSafeEqual(a, b) { let d = 0; for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i); return d === 0; }

// ---------- Supabase: who is calling (token check) and the subscriptions store ----------
export async function userFromToken(req, env, fetchImpl = fetch) {
  const m = /^Bearer\s+(.+)$/.exec(req.headers.get('Authorization') || '');
  if (!m) return null;
  const r = await fetchImpl(`${env.SUPABASE_URL}/auth/v1/user`, { headers: { apikey: env.SUPABASE_ANON_KEY, Authorization: `Bearer ${m[1]}` } });
  if (!r.ok) return null;
  const u = await r.json();
  return u && u.id ? { id: u.id, email: u.email } : null;
}

export function supabaseStore(env, fetchImpl = fetch) {
  const base = `${env.SUPABASE_URL}/rest/v1`, h = { apikey: env.SUPABASE_SERVICE_KEY, Authorization: `Bearer ${env.SUPABASE_SERVICE_KEY}`, 'Content-Type': 'application/json' };
  const one = async (q) => { const r = await fetchImpl(`${base}/${q}`, { headers: h }); if (!r.ok) throw new Error('store ' + r.status); return (await r.json())[0] || null; };
  return {
    byUser: (id) => one(`subscriptions?user_id=eq.${encodeURIComponent(id)}&select=*`),
    byCustomer: (c) => one(`subscriptions?stripe_customer=eq.${encodeURIComponent(c)}&select=*`),
    upsert: async (row) => { const r = await fetchImpl(`${base}/subscriptions?on_conflict=user_id`, { method: 'POST', headers: { ...h, Prefer: 'resolution=merge-duplicates,return=minimal' }, body: JSON.stringify(row) }); if (!r.ok) throw new Error('upsert ' + r.status); },
    // returns true the first time an event id is recorded, false if it was already processed
    claimEvent: async (id) => { const r = await fetchImpl(`${base}/stripe_events`, { method: 'POST', headers: { ...h, Prefer: 'return=minimal' }, body: JSON.stringify({ id }) }); if (r.status === 409) return false; if (!r.ok) throw new Error('event ' + r.status); return true; },
  };
}

// ---------- Stripe REST (form-encoded) ----------
function form(obj, prefix = '', out = []) {
  for (const [k, v] of Object.entries(obj)) {
    const key = prefix ? `${prefix}[${k}]` : k;
    if (v === undefined || v === null) continue;
    if (typeof v === 'object') form(v, key, out); else out.push(`${encodeURIComponent(key)}=${encodeURIComponent(String(v))}`);
  }
  return out.join('&');
}
async function stripe(env, path, body, fetchImpl = fetch) {
  const r = await fetchImpl(`https://api.stripe.com/v1/${path}`, { method: 'POST', headers: { Authorization: `Bearer ${env.STRIPE_SECRET_KEY}`, 'Content-Type': 'application/x-www-form-urlencoded', 'Stripe-Version': '2024-06-20' }, body: form(body) });
  const j = await r.json();
  if (!r.ok) throw new Error(`stripe ${r.status}: ${(j.error && j.error.message) || ''}`.slice(0, 200));
  return j;
}

// ---------- webhook event -> subscription row ----------
const ts = (s) => (s ? new Date(s * 1000).toISOString() : null);
export async function applyEvent(ev, store, now = Date.now()) {
  const o = ev.data && ev.data.object;
  if (!o) return 'ignored';
  if (ev.type === 'checkout.session.completed') {
    if (!o.client_reference_id || !o.customer) return 'ignored';
    const prev = await store.byUser(o.client_reference_id);
    await store.upsert({ ...(prev || {}), user_id: o.client_reference_id, stripe_customer: o.customer, stripe_subscription: o.subscription || (prev && prev.stripe_subscription) || null,
                         status: (prev && prev.status) || 'incomplete', updated_at: new Date(now).toISOString() });
    return 'linked';
  }
  if (ev.type.startsWith('customer.subscription.')) {
    const prev = await store.byCustomer(o.customer);
    if (!prev) return 'unknown-customer';           // checkout link not seen yet: Stripe retries the event later
    if (prev.last_event_created && ev.created < prev.last_event_created) return 'stale';   // out-of-order delivery
    const item = (o.items && o.items.data && o.items.data[0]) || {};
    const status = ev.type === 'customer.subscription.deleted' ? 'canceled' : o.status;
    await store.upsert({ ...prev, stripe_subscription: o.id, status, price_id: item.price && item.price.id,
                         plan: item.price && item.price.recurring ? item.price.recurring.interval : prev.plan,
                         trial_end: ts(o.trial_end), current_period_end: ts(o.current_period_end || item.current_period_end), cancel_at_period_end: !!o.cancel_at_period_end,
                         past_due_since: status === 'past_due' ? (prev.past_due_since || new Date(now).toISOString()) : null,
                         last_event_created: ev.created, updated_at: new Date(now).toISOString() });
    return status;
  }
  if (ev.type === 'invoice.payment_failed' || ev.type === 'invoice.paid' || ev.type === 'customer.subscription.trial_will_end') return 'noted';  // status changes arrive as subscription events
  return 'ignored';
}

// ---------- routes ----------
const json = (h, status, body) => new Response(JSON.stringify(body), { status, headers: { ...h, 'Content-Type': 'application/json', 'Cache-Control': 'private, no-store' } });
export function proCors(h) { return { ...h, 'Access-Control-Allow-Methods': 'GET, POST, OPTIONS', 'Access-Control-Allow-Headers': 'Authorization, Content-Type' }; }

export async function handlePro(req, env, url, baseHeaders, deps = {}) {
  const h = proCors(baseHeaders), f = deps.fetch || fetch, store = deps.store || supabaseStore(env, f), now = deps.now || Date.now();
  if (env.PRO_ENABLED !== 'true') return new Response('Not found', { status: 404, headers: h });
  if (String(env.STRIPE_SECRET_KEY || '').startsWith('sk_live') && env.PRO_LIVE !== 'true') return json(h, 503, { error: 'live payments are not approved' });
  if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: h });

  if (url.pathname === '/v1/pro/webhook' && req.method === 'POST') {
    const raw = await req.text();
    if (!(await verifyStripe(raw, req.headers.get('Stripe-Signature'), env.STRIPE_WEBHOOK_SECRET, 300, deps.nowSec))) return json({}, 400, { error: 'bad signature' });
    const ev = JSON.parse(raw);
    if (!(await store.claimEvent(ev.id))) return json({}, 200, { ok: true, duplicate: true });
    const result = await applyEvent(ev, store, now);
    if (result === 'unknown-customer') return json({}, 409, { error: 'customer not linked yet' });  // non-2xx -> Stripe retries
    return json({}, 200, { ok: true, result });
  }

  const user = await userFromToken(req, env, f);
  if (!user) return json(h, 401, { error: 'sign in required' });

  if (url.pathname === '/v1/pro/me' && req.method === 'GET') {
    const s = await store.byUser(user.id);
    return json(h, 200, { pro: isPro(s, now), status: s ? s.status : 'none', plan: s ? s.plan : null, trial_end: s ? s.trial_end : null,
                          current_period_end: s ? s.current_period_end : null, cancel_at_period_end: s ? !!s.cancel_at_period_end : false });
  }
  if (url.pathname === '/v1/pro/checkout' && req.method === 'POST') {
    const body = await req.json().catch(() => ({}));
    const price = body.plan === 'yearly' ? env.STRIPE_PRICE_YEARLY : env.STRIPE_PRICE_MONTHLY;
    if (!price) return json(h, 500, { error: 'price not configured' });
    const existing = await store.byUser(user.id);
    if (isPro(existing, now)) return json(h, 409, { error: 'already subscribed' });
    const site = env.SITE_URL || 'https://investedia.com';
    const s = await stripe(env, 'checkout/sessions', {
      mode: 'subscription', client_reference_id: user.id,
      ...(existing && existing.stripe_customer ? { customer: existing.stripe_customer } : { customer_email: user.email }),
      line_items: { 0: { price, quantity: 1 } },
      subscription_data: { trial_period_days: existing && existing.trial_end ? undefined : TRIAL_DAYS, trial_settings: { end_behavior: { missing_payment_method: 'cancel' } }, metadata: { user_id: user.id } },
      payment_method_collection: 'always', automatic_tax: { enabled: 'true' }, tax_id_collection: { enabled: 'true' }, billing_address_collection: 'required',
      allow_promotion_codes: 'false', locale: 'auto',
      custom_text: { submit: { message: 'I ask Investedia to start Pro immediately and understand that I lose my 14-day withdrawal right once the service has started. I can cancel anytime.' } },
      success_url: `${site}/pro.html?checkout=success`, cancel_url: `${site}/pro.html?checkout=cancelled`,
    }, f);
    return json(h, 200, { url: s.url });
  }
  if (url.pathname === '/v1/pro/portal' && req.method === 'POST') {
    const s = await store.byUser(user.id);
    if (!s || !s.stripe_customer) return json(h, 404, { error: 'no subscription' });
    const p = await stripe(env, 'billing_portal/sessions', { customer: s.stripe_customer, return_url: `${env.SITE_URL || 'https://investedia.com'}/profile.html` }, f);
    return json(h, 200, { url: p.url });
  }
  return json(h, 404, { error: 'not found' });
}
