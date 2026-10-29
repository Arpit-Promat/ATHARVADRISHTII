-- ATHARVADRISHTI Supabase scan-history schema
-- Run this in Supabase SQL Editor after configuring Supabase Auth.
-- Safe to re-run. This extends the initial scan_history table created earlier.

create table if not exists public.scan_history (
    id bigint generated always as identity primary key,
    user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
    image_name text,
    predicted_disease text,
    confidence double precision,
    created_at timestamptz not null default now()
);

alter table public.scan_history
    add column if not exists session_key text,
    add column if not exists status text not null default 'completed',
    add column if not exists top_predictions jsonb not null default '[]'::jsonb;

alter table public.scan_history enable row level security;

create unique index if not exists scan_history_user_session_key_uidx
    on public.scan_history (user_id, session_key)
    where session_key is not null;

drop policy if exists "Users can read their own scans" on public.scan_history;
create policy "Users can read their own scans"
on public.scan_history for select to authenticated
using (auth.uid() = user_id);

drop policy if exists "Users can add their own scans" on public.scan_history;
create policy "Users can add their own scans"
on public.scan_history for insert to authenticated
with check (auth.uid() = user_id);

drop policy if exists "Users can delete their own scans" on public.scan_history;
create policy "Users can delete their own scans"
on public.scan_history for delete to authenticated
using (auth.uid() = user_id);
