create table if not exists public.bookings (
  id uuid primary key default gen_random_uuid(),
  customer_name text not null,
  phone_number text not null,
  service text not null,
  stylist text,
  booking_date text not null,
  booking_time text not null,
  status text not null default 'confirmed',
  created_at timestamptz not null default now()
);

alter table public.bookings enable row level security;

-- Service role can do everything (backend writes)
create policy "Service role full access" on public.bookings
  using (true)
  with check (true);
