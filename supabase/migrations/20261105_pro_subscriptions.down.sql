-- Rollback for 20261105_pro_subscriptions.sql. Deletes ALL Pro subscription state in Supabase (Stripe keeps its own records).
-- Only run after the sandbox is disabled and no live billing exists.
drop policy if exists "read own subscription" on public.subscriptions;
drop table if exists public.stripe_events;
drop table if exists public.subscriptions;
