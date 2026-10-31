-- Run once in Supabase (SQL editor) so the Feedback page can save messages.
-- Anyone may INSERT (the form is public); only the owner accounts can READ, like the `events` table.
create table if not exists public.feedback (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  mood text check (mood in ('good','bad','idea')),
  category text check (category in ('Idea','Bug','Data issue','Other')),
  message text check (char_length(message) <= 2000),
  email text check (char_length(email) <= 200),
  page text check (char_length(page) <= 200),
  device text check (device in ('phone','desktop'))
);
alter table public.feedback enable row level security;
create policy "anyone can send feedback" on public.feedback for insert to anon, authenticated with check (true);
-- Reading: copy the same condition the `events` select policy uses for the owner emails, for example:
-- create policy "owners read feedback" on public.feedback for select to authenticated
--   using ((auth.jwt() ->> 'email') in ('adonaykabeya10@gmail.com','info@investedia.com'));
