import { GoogleGenerativeAI } from "@google/generative-ai";
import type { ScrapedMatch } from "./toto-scraper";

export type GemAnalysisResult = {
  matchName: string;
  prediction: "1" | "X" | "2" | "1X" | "X2";
  analysisText: string;
};

/**
 * Gemini API ile maç analizi yapar.
 * Her maç için tahmin ve analiz metni üretir.
 */
export async function analyzeMatchesWithGem(
  matches: ScrapedMatch[]
): Promise<GemAnalysisResult[]> {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    throw new Error("GEMINI_API_KEY environment variable is not set.");
  }

  console.log(`Gemini ile ${matches.length} maç analiz ediliyor...`);

  const genAI = new GoogleGenerativeAI(apiKey);
  const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });

  const matchList = matches
    .map((m, i) => `${i + 1}. ${m.matchName}`)
    .join("\n");

  const prompt = `
Sen bir profesyonel futbol analisti ve Spor Toto uzmanısın.
Aşağıdaki ${matches.length} maçı analiz et ve her biri için tahmin yap.

MAÇLAR:
${matchList}

Her maç için şu formatı kullan ve sadece JSON döndür, başka hiçbir şey yazma:

{
  "results": [
    {
      "matchName": "Ev Sahibi - Deplasman",
      "prediction": "1",
      "analysisText": "### Maç Adı Analizi\\n- **Form Durumu:** ...\\n- **Kafa Kafaya:** ...\\n- **Eksikler:** ...\\n- **Tahmin Gerekçesi:** ...\\n\\n**Sonuç: 1**"
    }
  ]
}

TAHMİN SEÇENEKLERİ:
- "1" = Ev sahibi kazanır
- "X" = Beraberlik  
- "2" = Deplasman kazanır
- "1X" = Ev sahibi kazanır veya beraberlik
- "X2" = Beraberlik veya deplasman kazanır

ÖNEMLİ:
- Sadece JSON döndür, markdown veya açıklama ekleme
- Her maç için gerçekçi ve farklı analizler yaz
- Türkçe yaz
- Tahminler çeşitli olsun, hepsi aynı olmasın
`;

  const result = await model.generateContent(prompt);
  const text = result.response.text();

  // JSON temizle ve parse et
  const cleaned = text
    .replace(/```json/g, "")
    .replace(/```/g, "")
    .trim();

  let parsed: { results: GemAnalysisResult[] };
  try {
    parsed = JSON.parse(cleaned);
  } catch (e) {
    console.error("Gemini JSON parse hatası:", e);
    console.error("Gelen metin:", text.slice(0, 500));
    throw new Error("Gemini geçerli JSON döndürmedi.");
  }

  if (!parsed.results || parsed.results.length === 0) {
    throw new Error("Gemini sonuç listesi boş döndü.");
  }

  console.log(`${parsed.results.length} maç analizi tamamlandı.`);
  return parsed.results;
}
