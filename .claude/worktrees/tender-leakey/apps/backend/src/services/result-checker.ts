import axios from "axios";
import { cleanTeamName } from "./toto-scraper";

const TOTO_API_BASE = "https://webapi.sportoto.gov.tr/api";

// ─── Types ─────────────────────────────────────────────────────────────────

export type MatchResult = {
  matchId: number;          // 1-15 sıra
  homeTeam: string;
  awayTeam: string;
  homeScore: number | null;
  awayScore: number | null;
  homeHtScore: number | null;
  awayHtScore: number | null;
  fullTimeResult: string | null;  // "1", "0", "2"
};

export type CheckedResult = MatchResult & {
  ourPrediction: string;
  isCorrect: boolean;
};

export type CheckResultsOutput = {
  bulletinId: string;
  gameRoundId: number;
  totalMatches: number;
  correctPredictions: number;
  accuracyPct: number;
  results: CheckedResult[];
};

type PredictionRow = {
  match_id: number;
  prediction: string;
};

// ─── API response types ────────────────────────────────────────────────────

type TotoMatchItem = {
  match: {
    homeTeam: { name: string; mediumName: string };
    awayTeam: { name: string; mediumName: string };
    score: {
      homeRegular: number | null;
      awayRegular: number | null;
      homeHT: number | null;
      awayHT: number | null;
    } | null;
    fullTimeWin: number | null;  // 1=ev, 0=beraberlik, 2=deplasman
  };
};

// ─── Helpers ───────────────────────────────────────────────────────────────

export function checkPrediction(prediction: string, actualResult: string | null): boolean {
  if (!actualResult) return false;
  const pred = prediction.toUpperCase();
  const actual = actualResult;

  // Direkt eşleşme
  if (pred === actual) return true;

  // Çifte şans
  if (pred === "1X") return actual === "1" || actual === "0";
  if (pred === "X2") return actual === "0" || actual === "2";
  if (pred === "12") return actual === "1" || actual === "2";

  // "X" → beraberlik
  if (pred === "X") return actual === "0";

  return false;
}

function mapFullTimeWin(raw: number | null): string | null {
  if (raw === null || raw === undefined) return null;
  if (raw === 1) return "1";
  if (raw === 0) return "0";
  if (raw === 2) return "2";
  return null;
}

// ─── Fetch ─────────────────────────────────────────────────────────────────

export async function fetchMatchResults(gameRoundId: number): Promise<MatchResult[]> {
  const response = await axios.get<{
    object: TotoMatchItem[];
    isSucceed: boolean;
  }>(`${TOTO_API_BASE}/GameMatch/GetGameMatches/`, {
    params: { gameRoundId },
    timeout: 15000,
  });

  if (!response.data.isSucceed || !response.data.object?.length) {
    throw new Error(`Spor Toto API: gameRoundId=${gameRoundId} için sonuç yok`);
  }

  return response.data.object.map((item, index) => {
    const home = item.match.homeTeam.mediumName || cleanTeamName(item.match.homeTeam.name);
    const away = item.match.awayTeam.mediumName || cleanTeamName(item.match.awayTeam.name);
    const score = item.match.score;
    return {
      matchId: index + 1,
      homeTeam: home,
      awayTeam: away,
      homeScore: score?.homeRegular ?? null,
      awayScore: score?.awayRegular ?? null,
      homeHtScore: score?.homeHT ?? null,
      awayHtScore: score?.awayHT ?? null,
      fullTimeResult: mapFullTimeWin(item.match.fullTimeWin),
    };
  });
}

// ─── Main ──────────────────────────────────────────────────────────────────

export async function checkResults(
  bulletinId: string,
  gameRoundId: number,
  predictions: PredictionRow[]
): Promise<CheckResultsOutput> {
  const apiResults = await fetchMatchResults(gameRoundId);

  const predMap = new Map<number, string>(
    predictions.map((p) => [p.match_id, p.prediction])
  );

  const results: CheckedResult[] = apiResults.map((r) => {
    const ourPrediction = predMap.get(r.matchId) ?? "";
    const isCorrect = ourPrediction ? checkPrediction(ourPrediction, r.fullTimeResult) : false;
    return { ...r, ourPrediction, isCorrect };
  });

  const totalMatches = results.filter((r) => r.ourPrediction !== "").length;
  const correctPredictions = results.filter((r) => r.isCorrect).length;
  const accuracyPct =
    totalMatches > 0
      ? Math.round((correctPredictions / totalMatches) * 10000) / 100
      : 0;

  return { bulletinId, gameRoundId, totalMatches, correctPredictions, accuracyPct, results };
}
