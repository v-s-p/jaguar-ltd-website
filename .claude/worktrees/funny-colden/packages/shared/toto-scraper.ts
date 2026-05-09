import axios from "axios";

export type ScrapedMatch = {
  id: number;
  home: string;
  away: string;
  matchName: string;
  matchDate?: string;
  matchTime?: string;
  gameRoundName?: string;
};

const BASE_API = "https://webapi.sportoto.gov.tr/api";

/**
 * Takım adından sponsor/reklam öneklerini temizler.
 * Örnek: "Mısırlı.com.tr Fatih Karagümrük" → "Fatih Karagümrük"
 * Örnek: "ikas Eyüpspor" → "Eyüpspor"
 * Örnek: "Corendon Alanyaspor" → "Alanyaspor"
 * Bilinen takım listesine göre eşleşme yapar, bulamazsa orijinal adı döner.
 */
function cleanTeamName(name: string): string {
  const knownTeams = [
    "Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor",
    "Başakşehir", "Kayserispor", "Konyaspor", "Antalyaspor",
    "Gaziantep FK", "Kasımpaşa", "Samsunspor", "Kocaelispor",
    "Rizespor", "Alanyaspor", "Gençlerbirliği", "Göztepe",
    "Eyüpspor", "Fatih Karagümrük", "Sivasspor", "Adana Demirspor",
    "Hatayspor", "Ankaragücü", "Pendikspor", "Ümraniyespor",
    "Real Madrid", "Barcelona", "Atletico Madrid", "Sevilla",
    "Athletic Bilbao", "Villarreal", "Celta Vigo", "Valencia",
    "Bayern München", "Borussia Dortmund", "Bayer Leverkusen",
    "Freiburg", "Union Berlin", "Schalke", "Wolfsburg",
    "Paris St Germain", "Monaco", "Marseille", "Lyon", "Lens",
    "Arsenal", "Chelsea", "Liverpool", "Manchester United",
    "Manchester City", "Tottenham", "Newcastle",
    "Juventus", "Milan", "Inter", "Napoli", "Roma", "Lazio",
    "Club Brugge", "Anderlecht",
  ];

  // Bilinen takım adlarından biri içinde geçiyor mu kontrol et
  for (const team of knownTeams) {
    if (name.includes(team)) {
      return team;
    }
  }

  // Bulunamazsa: nokta içeren kelimeleri (domain gibi) ve
  // tek başına duran sponsor kelimelerini başından at
  const cleaned = name
    .replace(/^[\w.]+\.(com|net|org|tr|co)(\.\w+)?\s+/i, "") // domain önekleri
    .replace(/^[a-z]+\s+(?=[A-ZÇĞİÖŞÜ])/u, "") // küçük harf tek kelime önekleri
    .trim();

  return cleaned || name;
}

/**
 * Güncel sezonu otomatik hesaplar.
 * Örnek: 2025 yılındaysa "2025/2026" döner.
 */
function getCurrentSeason(): string {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth() + 1;
  if (month >= 8) {
    return `${year}/${year + 1}`;
  } else {
    return `${year - 1}/${year}`;
  }
}

/**
 * Mevcut haftanın GameRound ID'sini çeker.
 * En son yayınlanan (en yüksek ID'li) haftayı döner.
 */
async function getLatestGameRoundId(): Promise<{ id: number; name: string }> {
  const season = getCurrentSeason();
  const url = `${BASE_API}/GameRound?year=${encodeURIComponent(season)}&isPublished=true`;

  const response = await axios.get(url, {
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      Accept: "application/json",
    },
    timeout: 15000,
  });

  const rounds = response.data?.object;
  if (!rounds || rounds.length === 0) {
    throw new Error(`${season} sezonu için hafta bulunamadı.`);
  }

  // En yüksek ID = en güncel hafta
  const latest = rounds.reduce((prev: any, curr: any) =>
    curr.id > prev.id ? curr : prev
  );

  return { id: latest.id, name: latest.name };
}

/**
 * Verilen GameRound ID'sine ait maçları çeker.
 */
async function getMatchesByRoundId(roundId: number): Promise<ScrapedMatch[]> {
  const url = `${BASE_API}/GameMatch/GetGameMatches/?gameRoundId=${roundId}`;

  const response = await axios.get(url, {
    headers: {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      Accept: "application/json",
    },
    timeout: 15000,
  });

  const items = response.data?.object;
  if (!items || items.length === 0) {
    throw new Error(`gameRoundId=${roundId} için maç bulunamadı.`);
  }

  const matches: ScrapedMatch[] = [];

  items.forEach((item: any, index: number) => {
    const match = item.match;
    if (!match) return;

    const home = cleanTeamName(
      match.homeTeam?.name ||
      match.homeTeam?.mediumName ||
      item.homeTeamName ||
      "Bilinmiyor"
    );

    const away = cleanTeamName(
      match.awayTeam?.name ||
      match.awayTeam?.mediumName ||
      item.awayTeamName ||
      "Bilinmiyor"
    );

    const matchDate = match.date ? new Date(match.date) : null;

    matches.push({
      id: index + 1,
      home,
      away,
      matchName: `${home} - ${away}`,
      matchDate: matchDate ? matchDate.toLocaleDateString("tr-TR") : undefined,
      matchTime: matchDate
        ? matchDate.toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" })
        : undefined,
      gameRoundName: item.gameRoundName || undefined,
    });
  });

  return matches;
}

/**
 * ANA FONKSİYON
 * Spor Toto resmi API'sinden haftalık maç listesini çeker.
 * Hata durumunda mock veriye düşer.
 */
export async function scrapeWeeklyTotoBulletin(): Promise<ScrapedMatch[]> {
  console.log("Spor Toto bülteni çekiliyor (Resmi API)...");

  try {
    const { id: roundId, name: roundName } = await getLatestGameRoundId();
    console.log(`Aktif hafta: ${roundName} (ID: ${roundId})`);

    const matches = await getMatchesByRoundId(roundId);
    console.log(`${matches.length} maç başarıyla çekildi.`);
    return matches;
  } catch (error) {
    console.error("API hatası:", error);
    console.warn("Mock veriye geçiliyor...");
    return getMockMatches();
  }
}

/**
 * Yedek mock veri - API erişilemez olduğunda kullanılır.
 */
function getMockMatches(): ScrapedMatch[] {
  console.log("Mock maç verisi kullanılıyor...");
  const mockMatches = [
    { home: "Trabzonspor", away: "Kasımpaşa" },
    { home: "Kayserispor", away: "Başakşehir" },
    { home: "Samsunspor", away: "Kocaelispor" },
    { home: "Fatih Karagümrük", away: "Galatasaray" },
    { home: "Gaziantep FK", away: "Konyaspor" },
    { home: "Antalyaspor", away: "Gençlerbirliği" },
    { home: "Rizespor", away: "Alanyaspor" },
    { home: "Fenerbahçe", away: "Göztepe" },
    { home: "Eyüpspor", away: "Beşiktaş" },
    { home: "Union Berlin", away: "Borussia Dortmund" },
    { home: "Marsilya", away: "Lens" },
    { home: "Arsenal", away: "Manchester United" },
    { home: "Villarreal", away: "Real Madrid" },
    { home: "Juventus", away: "Napoli" },
    { home: "Roma", away: "Milan" },
  ];
  return mockMatches.map((match, index) => ({
    id: index + 1,
    home: match.home,
    away: match.away,
    matchName: `${match.home} - ${match.away}`,
  }));
}

// Test satırı - test bittikten sonra silebilirsin
scrapeWeeklyTotoBulletin().then((matches) =>
  console.log(JSON.stringify(matches, null, 2))
);
