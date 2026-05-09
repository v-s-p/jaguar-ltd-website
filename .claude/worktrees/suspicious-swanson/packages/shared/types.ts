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
