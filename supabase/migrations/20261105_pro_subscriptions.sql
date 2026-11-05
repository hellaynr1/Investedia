-- Investedia Pro: subscription state written only by the Cloudflare Worker (service role) from verified Stripe webhooks.
create table if not exists public.subscriptions (
  user_id              uuid primary key references auth.users(id) on delete cascade,
  stripe_customer      text unique,
  stripe_subscription  text,
  status               text not null default 'none',      -- trialing | active | past_due | canceled | incomplete | unpaid | none
  plan                 text,                              -- month | year
  price_id             text,
  trial_end            timestamptz,
  current_period_end   timestamptz,
  cancel_at_period_end boolean not null default false,
  past_due_since       timestamptz,
  last_event_created   bigint,                            -- Stripe event.created of the last applied event (ignores out-of-order delivery)
  updated_at           timestamptz not null default now()
);
create table if not exists public.stripe_events (        -- webhook idempotency
  id          text primary key,
  received_at timestamptz not null default now()
);
alter table public.subscriptions enable row level security;
alter table public.stripe_events enable row level security;
-- signed-in users may read only their own subscription; nobody but the service role can write
drop policy if exists "read own subscription" on public.subscriptions;
create policy "read own subscription" on public.subscriptions for select to authenticated using (auth.uid() = user_id);
-- stripe_events: no policies -> no access for anon/authenticated; service role bypasses RLS
