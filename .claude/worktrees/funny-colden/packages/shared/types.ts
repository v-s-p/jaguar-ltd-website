export type Plan = "free" | "premium";

export type MatchItem = {
  id: number;
  home: string;
  away: string;
  prediction: string;
  xgHome: number;
  xgAway: number;
};

export type AnalyzeResponse = {
  plan: Plan;
  matches: MatchItem[];
  coupons: string[];
};

export type PredictionStatus = "pending" | "processing" | "completed" | "failed";

export type Prediction = {
  id: number; // Corresponds to Supabase table's primary key
  bulletin_id: string; // e.g., '2024-W25'
  match_id: number; // e.g., 1-15
  match_name: string; // e.g., 'Galatasaray - Fenerbahce'
  prediction: string; // e.g., '1', 'X', '2', '1X'
  analysis_text: string; // The GEM analysis
  status: PredictionStatus;
};
