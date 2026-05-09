export type ScrapedMatch = {
  id: number;
  home: string;
  away: string;
  matchName: string;
};

// This is a mock scraper. In a real-world scenario, this function would
// use a library like Cheerio or Puppeteer to scrape the Spor Toto bulletin.
export async function scrapeWeeklyTotoBulletin(): Promise<ScrapedMatch[]> {
  console.log("Scraping weekly Spor Toto bulletin...");

  // Mock data, similar to what would be scraped from the bulletin.
  const mockMatches = [
    { home: "Trabzonspor", away: "Kasımpaşa" },
    { home: "Zecorner Kayserispor", away: "Rams Başakşehir" },
    { home: "Samsunspor", away: "Kocaelispor" },
    { home: "Fatih Karagümrük", away: "Galatasaray" },
    { home: "Gaziantep FK", away: "Tümosan Konyaspor" },
    { home: "Antalyaspor", away: "Gençlerbirliği" },
    { home: "Çaykur Rizespor", away: "Corendon Alanyaspor" },
    { home: "Fenerbahçe", away: "Göztepe" },
    { home: "Eyüpspor", away: "Beşiktaş" },
    { home: "Union Berlin", away: "Borussia Dortmund" },
    { home: "Marsilya", away: "Lens" },
    { home: "Arsenal", away: "Manchester United" },
    { home: "Villarreal", away: "Real Madrid" },
    { home: "Juventus", away: "Napoli" },
    { home: "Roma", away: "Milan" },
  ];

  const scrapedMatches: ScrapedMatch[] = mockMatches.map((match, index) => ({
    id: index + 1,
    ...match,
    matchName: `${match.home} - ${match.away}`,
  }));

  console.log(`Scraped ${scrapedMatches.length} matches.`);
  return scrapedMatches;
}