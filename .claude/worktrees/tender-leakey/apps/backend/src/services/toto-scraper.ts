import axios from "axios";

export type ScrapedMatch = {
  id: number;
  home: string;
  away: string;
  matchName: string;
};

const TOTO_API_BASE = "https://webapi.sportoto.gov.tr/api";
const CURRENT_YEAR = "2025/2026";

export function cleanTeamName(name: string): string {
  return name
    .replace(/^[\w]+\.[\w.]+\s+/i, "")    // sponsor domain prefix: "Mısırlı.com.tr Fatih..." → "Fatih..."
    .replace(/^(Natura\s+Dünyası\s+)/i, "")
    .replace(/^(Zecorner\s+)/i, "")
    .replace(/^(Corendon\s+)/i, "")
    .replace(/^(Rams\s+)/i, "")
    .replace(/^(Tümosan\s+)/i, "")
    .trim();
}

async function getLatestGameRoundId(): Promise<number> {
  const response = await axios.get<{
    object: Array<{ id: number; name: string; roundCloseDate: string; isPublished: boolean }>;
    isSucceed: boolean;
  }>(`${TOTO_API_BASE}/GameRound`, {
    params: { year: CURRENT_YEAR, isPublished: true },
    timeout: 10000,
  });

  if (!response.data.isSucceed || !response.data.object?.length) {
    throw new Error("Spor Toto API: hafta listesi alınamadı");
  }

  const rounds = response.data.object;
  const latest = rounds.reduce((prev, curr) => (curr.id > prev.id ? curr : prev));
  console.log(`En son hafta: ${latest.name} (id: ${latest.id})`);
  return latest.id;
}

export async function scrapeWeeklyTotoBulletin(): Promise<ScrapedMatch[]> {
  console.log("Spor Toto resmi API'den maçlar çekiliyor...");

  try {
    const roundId = await getLatestGameRoundId();

    const response = await axios.get<{
      object: Array<{
        match: {
          homeTeam: { name: string; mediumName: string };
          awayTeam: { name: string; mediumName: string };
        };
      }>;
      isSucceed: boolean;
    }>(`${TOTO_API_BASE}/GameMatch/GetGameMatches/`, {
      params: { gameRoundId: roundId },
      timeout: 10000,
    });

    if (!response.data.isSucceed || !response.data.object?.length) {
      throw new Error("Spor Toto API: maç listesi boş");
    }

    const matches: ScrapedMatch[] = response.data.object.map((item, index) => {
      const home = item.match.homeTeam.mediumName || cleanTeamName(item.match.homeTeam.name);
      const away = item.match.awayTeam.mediumName || cleanTeamName(item.match.awayTeam.name);
      return {
        id: index + 1,
        home,
        away,
        matchName: `${home} - ${away}`,
      };
    });

    console.log(`${matches.length} maç çekildi (${CURRENT_YEAR} hafta ${roundId})`);
    return matches;
  } catch (err) {
    console.error("Spor Toto API hatası, mock veriye düşülüyor:", err instanceof Error ? err.message : err);
    return getMockMatches();
  }
}

function getMockMatches(): ScrapedMatch[] {
  console.warn("UYARI: Mock veri kullanılıyor!");
  const mockData = [
    { home: "Trabzonspor", away: "Galatasaray" },
    { home: "Kasımpaşa", away: "Kayserispor" },
    { home: "Gaziantep FK", away: "Alanyaspor" },
    { home: "Fenerbahçe", away: "Beşiktaş" },
    { home: "Karagümrük", away: "Rizespor" },
    { home: "Samsunspor", away: "Konyaspor" },
    { home: "Başakşehir", away: "Ankaragücü" },
    { home: "Sivasspor", away: "Hatayspor" },
    { home: "Eyüpspor", away: "Antalyaspor" },
    { home: "Borussia Dortmund", away: "Bayern Münih" },
    { home: "Real Madrid", away: "Barcelona" },
    { home: "Arsenal", away: "Chelsea" },
    { home: "PSG", away: "Marsilya" },
    { home: "Juventus", away: "Milan" },
    { home: "Napoli", away: "Inter" },
  ];
  return mockData.map((m, i) => ({ id: i + 1, ...m, matchName: `${m.home} - ${m.away}` }));
}
