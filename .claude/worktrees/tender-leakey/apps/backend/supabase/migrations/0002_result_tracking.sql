-- match_results tablosu
create table if not exists match_results (
  id uuid primary key default gen_random_uuid(),
  bulletin_id text not null,
  game_round_id int not null,
  match_id smallint not null,
  home_team text not null,
  away_team text not null,
  home_score int,
  away_score int,
  home_ht_score int,
  away_ht_score int,
  full_time_result text,              -- '1' ev, '0' beraberlik, '2' deplasman
  our_prediction text,
  is_correct boolean,
  processed_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  unique(bulletin_id, match_id)
);

-- weekly_accuracy tablosu
create table if not exists weekly_accuracy (
  id uuid primary key default gen_random_uuid(),
  bulletin_id text not null unique,
  game_round_id int not null,
  total_matches int not null default 0,
  correct_predictions int not null default 0,
  accuracy_pct numeric(5,2) default 0,
  processed_at timestamptz not null default now(),
  created_at timestamptz not null default now()
);

create index if not exists idx_match_results_bulletin on match_results(bulletin_id);
create index if not exists idx_match_results_correct on match_results(is_correct);
create index if not exists idx_weekly_accuracy_bulletin on weekly_accuracy(bulletin_id);

-- Genel istatistik view
create or replace view accuracy_overview as
select
  count(*) as total_weeks,
  sum(total_matches) as total_matches,
  sum(correct_predictions) as total_correct,
  round(
    case when sum(total_matches) > 0
    then (sum(correct_predictions)::numeric / sum(total_matches)) * 100
    else 0 end, 2
  ) as overall_accuracy_pct,
  max(accuracy_pct) as best_week_pct,
  min(accuracy_pct) as worst_week_pct
from weekly_accuracy;
