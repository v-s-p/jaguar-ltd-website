import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import type { CheckedResult, CheckResultsOutput } from "./result-checker";

// ─── Types ─────────────────────────────────────────────────────────────────

type MatchResultRow = {
  bulletin_id: string;
  game_round_id: number;
  match_id: number;
  home_team: string;
  away_team: string;
  home_score: number | null;
  away_score: number | null;
  home_ht_score: number | null;
  away_ht_score: number | null;
  full_time_result: string | null;
  our_prediction: string;
  is_correct: boolean;
  processed_at: string;
};

type WeeklyAccuracyRow = {
  bulletin_id: string;
  game_round_id: number;
  total_matches: number;
  correct_predictions: number;
  accuracy_pct: number;
  processed_at: string;
};

type AccuracyOverviewRow = {
  total_weeks: number;
  total_matches: number;
  total_correct: number;
  overall_accuracy_pct: number;
  best_week_pct: number;
  worst_week_pct: number;
};

// ─── Client ────────────────────────────────────────────────────────────────

function createSupabaseClient(): SupabaseClient {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) throw new Error("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY missing");
  return createClient(url, key, { auth: { persistSession: false } });
}

// ─── Store ─────────────────────────────────────────────────────────────────

export async function saveMatchResults(
  bulletinId: string,
  gameRoundId: number,
  results: CheckedResult[]
): Promise<void> {
  const client: SupabaseClient = createSupabaseClient();
  const now = new Date().toISOString();

  const rows: MatchResultRow[] = results.map((r) => ({
    bulletin_id: bulletinId,
    game_round_id: gameRoundId,
    match_id: r.matchId,
    home_team: r.homeTeam,
    away_team: r.awayTeam,
    home_score: r.homeScore,
    away_score: r.awayScore,
    home_ht_score: r.homeHtScore,
    away_ht_score: r.awayHtScore,
    full_time_result: r.fullTimeResult,
    our_prediction: r.ourPrediction,
    is_correct: r.isCorrect,
    processed_at: now,
  }));

  const { error } = await client
    .from("match_results")
    .upsert(rows, { onConflict: "bulletin_id,match_id" });

  if (error) throw new Error(`saveMatchResults failed: ${error.message}`);
}

export async function saveWeeklyAccuracy(output: CheckResultsOutput): Promise<void> {
  const client: SupabaseClient = createSupabaseClient();
  const now = new Date().toISOString();

  const row: WeeklyAccuracyRow = {
    bulletin_id: output.bulletinId,
    game_round_id: output.gameRoundId,
    total_matches: output.totalMatches,
    correct_predictions: output.correctPredictions,
    accuracy_pct: output.accuracyPct,
    processed_at: now,
  };

  const { error } = await client
    .from("weekly_accuracy")
    .upsert(row, { onConflict: "bulletin_id" });

  if (error) throw new Error(`saveWeeklyAccuracy failed: ${error.message}`);
}

export async function markPredictionsResolved(
  client: SupabaseClient,
  bulletinId: string
): Promise<void> {
  const { error } = await client
    .from("predictions")
    .update({ status: "resolved" })
    .eq("bulletin_id", bulletinId);

  if (error) throw new Error(`markPredictionsResolved failed: ${error.message}`);
}

export async function getWeekResults(bulletinId: string): Promise<MatchResultRow[]> {
  const client: SupabaseClient = createSupabaseClient();
  const { data, error } = await client
    .from("match_results")
    .select("*")
    .eq("bulletin_id", bulletinId)
    .order("match_id", { ascending: true });

  if (error) throw new Error(`getWeekResults failed: ${error.message}`);
  return (data ?? []) as MatchResultRow[];
}

export async function getAllWeeklyAccuracy(): Promise<WeeklyAccuracyRow[]> {
  const client: SupabaseClient = createSupabaseClient();
  const { data, error } = await client
    .from("weekly_accuracy")
    .select("*")
    .order("created_at", { ascending: false });

  if (error) throw new Error(`getAllWeeklyAccuracy failed: ${error.message}`);
  return (data ?? []) as WeeklyAccuracyRow[];
}

export async function getAccuracyOverview(): Promise<AccuracyOverviewRow | null> {
  const client: SupabaseClient = createSupabaseClient();
  const { data, error } = await client
    .from("accuracy_overview")
    .select("*")
    .maybeSingle();

  if (error) throw new Error(`getAccuracyOverview failed: ${error.message}`);
  return data as AccuracyOverviewRow | null;
}
