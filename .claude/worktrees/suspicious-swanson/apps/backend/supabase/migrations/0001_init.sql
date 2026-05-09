create extension if not exists "pgcrypto";

create table if not exists profiles (
  id uuid primary key,
  email text not null unique,
  plan text not null default 'free' check (plan in ('free', 'premium')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references profiles(id) on delete cascade,
  provider text not null default 'revenuecat',
  provider_customer_id text,
  status text not null default 'active',
  current_period_end timestamptz,
  last_event_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists entitlement_events (
  id uuid primary key default gen_random_uuid(),
  provider text not null,
  provider_event_id text not null,
  user_id uuid references profiles(id) on delete set null,
  app_user_id text not null,
  event_type text not null,
  payload jsonb not null,
  processed boolean not null default false,
  processed_at timestamptz,
  created_at timestamptz not null default now(),
  unique(provider, provider_event_id)
);

create table if not exists analyses (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references profiles(id) on delete cascade,
  plan text not null check (plan in ('free', 'premium')),
  input_matches jsonb not null,
  result jsonb not null,
  created_at timestamptz not null default now()
);

create table if not exists api_audit_logs (
  id bigint generated always as identity primary key,
  user_id uuid references profiles(id) on delete set null,
  endpoint text not null,
  method text not null,
  status_code int not null,
  meta jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_profiles_email on profiles(email);
create index if not exists idx_subscriptions_user on subscriptions(user_id);
create index if not exists idx_entitlement_events_user on entitlement_events(user_id);
create index if not exists idx_entitlement_events_event on entitlement_events(provider_event_id);
create index if not exists idx_analyses_user on analyses(user_id);
create index if not exists idx_api_audit_logs_user on api_audit_logs(user_id);
