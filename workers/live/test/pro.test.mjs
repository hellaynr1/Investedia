// Investedia Pro billing: signature checks, flags, entitlement, webhook idempotency and ordering, checkout parameters.
import test from 'node:test';
import assert from 'node:assert/strict';
import { handlePro, verifyStripe, isPro, applyEvent, TRIAL_DAYS, WITHDRAWAL_TEXT } from '../v1/pro.js';

const SECRET = 'whsec_test', ENV = { PRO_ENABLED: 'true', STRIPE_SECRET_KEY: 'sk_test_x', STRIPE_WEBHOOK_SECRET: SECRET, SUPABASE_URL: 'https://sb.test', SUPABASE_ANON_KEY: 'anon',
  SUPABASE_SERVICE_KEY: 'svc', STRIPE_PRICE_MONTHLY: 'price_m', STRIPE_PRICE_YEARLY: 'price_y', SITE_URL: 'https://investedia.com', VAT_MODE: 'registered' };
const hex = (b) => [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, '0')).join('');
async function sign(payload, t) { const k = await crypto.subtle.importKey('raw', new TextEncoder().encode(SECRET), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']); return `t=${t},v1=${hex(await crypto.subtle.sign('HMAC', k, new TextEncoder().encode(`${t}.${payload}`)))}`; }
function memStore() { const rows = new Map(), ev = new Set();
  return { rows, byUser: async (id) => rows.get(id) || null, byCustomer: async (c) => [...rows.values()].find(r => r.stripe_customer === c) || null,
           upsert: async (r) => { rows.set(r.user_id, { ...r }); }, claimEvent: async (id) => (ev.has(id) ? false : (ev.add(id), true)) }; }
const authFetch = (calls) => async (url, init = {}) => {
  calls.push({ url, init });
  if (url.endsWith('/auth/v1/user')) return new Response(JSON.stringify(init.headers.Authorization === 'Bearer good' ? { id: 'u1', email: 'a@b.c' } : {}), { status: init.headers.Authorization === 'Bearer good' ? 200 : 401 });
  if (url.includes('api.stripe.com/v1/checkout/sessions')) return new Response(JSON.stringify({ url: 'https://checkout.stripe.test/s' }), { status: 200 });
  if (url.includes('api.stripe.com/v1/billing_portal/sessions')) return new Response(JSON.stringify({ url: 'https://billing.stripe.test/p' }), { status: 200 });
  return new Response('{}', { status: 404 }); };
const req = (path, { method = 'GET', token, body, headers = {} } = {}) => new Request('https://w.test' + path, { method, body, headers: { ...(token ? { Authorization: 'Bearer ' + token } : {}), ...headers } });
const run = (r, env = ENV, deps = {}) => handlePro(r, env, new URL(r.url), {}, deps);

test('feature flag off hides every route', async () => { assert.equal((await run(req('/v1/pro/me'), { ...ENV, PRO_ENABLED: 'false' })).status, 404); });
test('live Stripe key refused without approval', async () => { assert.equal((await run(req('/v1/pro/me'), { ...ENV, STRIPE_SECRET_KEY: 'sk_live_x' })).status, 503); });
test('signed-in required', async () => { assert.equal((await run(req('/v1/pro/me', { token: 'bad' }), ENV, { fetch: authFetch([]), store: memStore() })).status, 401); });

test('signature: valid, tampered, stale', async () => {
  const p = '{"id":"evt_1"}', t = 1_800_000_000;
  assert.equal(await verifyStripe(p, await sign(p, t), SECRET, 300, t + 10), true);
  assert.equal(await verifyStripe(p + ' ', await sign(p, t), SECRET, 300, t + 10), false);
  assert.equal(await verifyStripe(p, await sign(p, t), SECRET, 300, t + 1000), false);
  assert.equal(await verifyStripe(p, 't=1', SECRET), false);
});

test('entitlement states incl. 3-day grace', () => {
  const now = Date.parse('2026-11-10T00:00:00Z');
  assert.equal(isPro({ status: 'trialing' }, now), true); assert.equal(isPro({ status: 'active' }, now), true);
  assert.equal(isPro({ status: 'past_due', past_due_since: '2026-11-08T00:00:00Z' }, now), true);
  assert.equal(isPro({ status: 'past_due', past_due_since: '2026-11-06T00:00:00Z' }, now), false);
  assert.equal(isPro({ status: 'canceled' }, now), false); assert.equal(isPro(null, now), false);
});

test('webhook: link, trial, duplicate, out-of-order, cancel', async () => {
  const store = memStore(), t = 1_800_000_000, post = async (ev) => { const p = JSON.stringify(ev); return run(req('/v1/pro/webhook', { method: 'POST', body: p, headers: { 'Stripe-Signature': await sign(p, t) } }), ENV, { store, nowSec: t }); };
  const sub = (status, created, extra = {}) => ({ id: 'evt_' + created, type: 'customer.subscription.updated', created, data: { object: { id: 'sub_1', customer: 'cus_1', status, trial_end: t + 7 * 86400, current_period_end: t + 7 * 86400, items: { data: [{ price: { id: 'price_m', recurring: { interval: 'month' } } }] }, ...extra } } });
  assert.equal((await post({ id: 'evt_0', type: 'customer.subscription.created', created: 5, data: { object: { customer: 'cus_1', status: 'trialing' } } })).status, 409);  // not linked yet -> retry
  assert.equal((await post({ id: 'evt_a', type: 'checkout.session.completed', created: 9, data: { object: { client_reference_id: 'u1', customer: 'cus_1', subscription: 'sub_1' } } })).status, 200);
  assert.equal((await post(sub('trialing', 10))).status, 200); assert.equal(store.rows.get('u1').status, 'trialing');
  const dup = await post(sub('trialing', 10)); assert.equal((await dup.json()).duplicate, true);
  await post(sub('active', 20)); await post(sub('past_due', 15));           // older event arrives late: ignored
  assert.equal(store.rows.get('u1').status, 'active');
  await post({ ...sub('canceled', 30), type: 'customer.subscription.deleted' }); assert.equal(store.rows.get('u1').status, 'canceled');
  assert.equal((await run(req('/v1/pro/webhook', { method: 'POST', body: '{}', headers: { 'Stripe-Signature': 't=1,v1=00' } }), ENV, { store })).status, 400);
});

test('checkout: 7-day trial, tax, consent text, user link; no second trial; portal', async () => {
  const calls = [], store = memStore();
  const r = await run(req('/v1/pro/checkout', { method: 'POST', token: 'good', body: '{"plan":"yearly"}' }), ENV, { fetch: authFetch(calls), store });
  assert.equal(r.status, 200); assert.equal((await r.json()).url, 'https://checkout.stripe.test/s');
  const body = decodeURIComponent(calls.find(c => c.url.includes('checkout/sessions')).init.body);
  for (const s of ['mode=subscription', 'client_reference_id=u1', 'line_items[0][price]=price_y', `subscription_data[trial_period_days]=${TRIAL_DAYS}`, 'automatic_tax[enabled]=true', 'tax_id_collection[enabled]=true', 'consent_collection[terms_of_service]=required', 'withdraw within 14 days', 'full refund']) assert.ok(body.includes(s), s);
  store.rows.set('u1', { user_id: 'u1', stripe_customer: 'cus_1', status: 'canceled', trial_end: '2026-01-01T00:00:00Z' });
  const c2 = []; await run(req('/v1/pro/checkout', { method: 'POST', token: 'good', body: '{}' }), ENV, { fetch: authFetch(c2), store });
  const b2 = decodeURIComponent(c2.find(c => c.url.includes('checkout/sessions')).init.body);
  assert.ok(!b2.includes('trial_period_days') && b2.includes('customer=cus_1'));
  const p = await run(req('/v1/pro/portal', { method: 'POST', token: 'good' }), ENV, { fetch: authFetch([]), store }); assert.equal((await p.json()).url, 'https://billing.stripe.test/p');
  store.rows.set('u1', { user_id: 'u1', status: 'active' });
  assert.equal((await run(req('/v1/pro/checkout', { method: 'POST', token: 'good', body: '{}' }), ENV, { fetch: authFetch([]), store })).status, 409);
});

test('VAT mode must be explicit; exempt mode charges no VAT', async () => {
  const st = memStore();
  assert.equal((await run(req('/v1/pro/checkout', { method: 'POST', token: 'good', body: '{}' }), { ...ENV, VAT_MODE: undefined }, { fetch: authFetch([]), store: st })).status, 500);
  const c = []; await run(req('/v1/pro/checkout', { method: 'POST', token: 'good', body: '{}' }), { ...ENV, VAT_MODE: 'exempt' }, { fetch: authFetch(c), store: memStore() });
  const b = decodeURIComponent(c.find(x => x.url.includes('checkout/sessions')).init.body);
  assert.ok(b.includes('automatic_tax[enabled]=false') && b.includes('tax_id_collection[enabled]=false'));
});

test('withdrawal wording never claims the right is lost', () => { assert.ok(!/lose|waive|forfeit/i.test(WITHDRAWAL_TEXT)); assert.ok(/14 days/.test(WITHDRAWAL_TEXT)); });

test('failed payment: grace starts at first past_due, recovery clears it, unpaid/canceled end access', async () => {
  const store = memStore(), base = Date.parse('2026-11-20T00:00:00Z');
  await applyEvent({ type: 'checkout.session.completed', created: 1, data: { object: { client_reference_id: 'u1', customer: 'cus_1', subscription: 'sub_1' } } }, store, base);
  const ev = (status, created) => ({ type: 'customer.subscription.updated', created, data: { object: { id: 'sub_1', customer: 'cus_1', status, items: { data: [] } } } });
  await applyEvent(ev('past_due', 10), store, base);
  const since = store.rows.get('u1').past_due_since;
  await applyEvent(ev('past_due', 11), store, base + 864e5);               // retry also failed: grace clock does NOT restart
  assert.equal(store.rows.get('u1').past_due_since, since);
  assert.equal(isPro(store.rows.get('u1'), base + 2 * 864e5), true);
  assert.equal(isPro(store.rows.get('u1'), base + 4 * 864e5), false);       // grace over while Stripe may still retry
  await applyEvent(ev('active', 12), store, base + 5 * 864e5);              // card updated, invoice paid
  assert.equal(store.rows.get('u1').past_due_since, null); assert.equal(isPro(store.rows.get('u1'), base + 5 * 864e5), true);
  await applyEvent(ev('unpaid', 13), store, base + 40 * 864e5); assert.equal(isPro(store.rows.get('u1')), false);
});

test('trial reuse: a returning customer with a past trial gets no second trial, an active one cannot double-subscribe', async () => {
  const store = memStore(); store.rows.set('u1', { user_id: 'u1', stripe_customer: 'cus_1', status: 'canceled', trial_end: '2026-11-12T00:00:00Z' });
  const c = []; await run(req('/v1/pro/checkout', { method: 'POST', token: 'good', body: '{}' }), ENV, { fetch: authFetch(c), store });
  assert.ok(!decodeURIComponent(c.find(x => x.url.includes('checkout/sessions')).init.body).includes('trial_period_days'));
  store.rows.set('u1', { user_id: 'u1', stripe_customer: 'cus_1', status: 'trialing' });
  assert.equal((await run(req('/v1/pro/checkout', { method: 'POST', token: 'good', body: '{}' }), ENV, { fetch: authFetch([]), store })).status, 409);
});
