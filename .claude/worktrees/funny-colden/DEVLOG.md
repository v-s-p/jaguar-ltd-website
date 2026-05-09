# S8 Professor — Geliştirme Günlüğü

---

## 📅 2026-03-06 — Oturum 1

### ✅ Tamamlananlar

#### 1. Spor Toto Scraper (Gerçek API)
- `packages/shared/toto-scraper.ts` ve `apps/backend/src/services/toto-scraper.ts` güncellendi
- Resmi API bulundu: `https://webapi.sportoto.gov.tr/api`
- Endpoint'ler:
  - `GET /api/GameRound?year=2025/2026&isPublished=true` → Hafta listesi + ID
  - `GET /api/GameMatch/GetGameMatches/?gameRoundId={id}` → Maç listesi
- Sponsor isimleri temizleniyor (`cleanTeamName` fonksiyonu)
- Hata durumunda mock veriye düşüyor (güvenli)
- Test: 31. Hafta, 15 maç başarıyla çekildi

#### 2. Gemini Entegrasyonu (Gerçek API)
- `packages/shared/gemini-service.ts` ve `apps/backend/src/services/gemini-service.ts` güncellendi
- Model: `gemini-2.5-flash`
- Paket: `@google/generative-ai` yüklendi (`apps/backend/`)
- Her maç için: form, H2H, eksikler, tahmin gerekçesi + sonuç üretiyor
- JSON parse ile güvenli çalışıyor

#### 3. Backend Uçtan Uca Test
- `/admin/process-weekly-toto` endpoint'i çalışıyor
- 15 maç analizi Supabase'e kaydedildi (`toto-2026-w10`)
- `/predictions/latest` endpoint'i çalışıyor
- RevenueCat webhook hazır (free/premium plan)

#### 4. Güvenlik
- `apps/backend/.gitignore` oluşturuldu (`.env` korunuyor)
- `.env` hiç GitHub'a push edilmedi ✅

---

### 📁 Proje Yapısı
```
S8 Professor/
├── apps/
│   ├── backend/          ← Express + Supabase + Gemini
│   │   ├── src/
│   │   │   ├── server.ts
│   │   │   ├── routes.ts
│   │   │   ├── auth.ts
│   │   │   └── services/
│   │   │       ├── toto-scraper.ts  ← Gerçek API ✅
│   │   │       └── gemini-service.ts ← Gemini 2.5 Flash ✅
│   │   └── supabase/
│   │       └── migrations/
│   └── mobile/           ← Henüz başlanmadı
└── packages/
    └── shared/           ← Ortak tipler ve servisler
```

---

### 🔧 Ortam
- Backend port: 4000
- Supabase URL: `https://qrblkavdyiwfcfculutl.supabase.co`
- GitHub repo: `https://github.com/v-s-p/s8-professor-app`
- Branch: `chore/eas-build-pipeline`

### 📦 Yüklü Paketler (backend)
- `axios`, `cheerio` — scraping
- `@google/generative-ai` — Gemini
- `@supabase/supabase-js` — veritabanı
- `express`, `helmet`, `cors` — sunucu
- `zod` — validasyon

---

### 🎯 Uygulama Konsepti
- Haftalık Spor Toto tahmini uygulaması
- Backend haftada bir Cuma güncellenir (admin endpoint)
- Kullanıcı telefonunda backend yok — sadece Supabase'den okur
- **Free:** İlk 3 maç analizi + 3 maçlık kupon
- **Premium:** 15 maç analizi + 3-4 kombine kupon
- Ödeme: Haftalık/aylık abonelik (RevenueCat)

---

### 📌 Sıradaki Adımlar
1. **Mobile app** (React Native / Expo) — `/predictions/latest` endpoint'inden veri çekecek
2. **Free/Premium ayrımı** — ilk 3 maç vs tüm maçlar
3. **Kombine kupon üretimi** — Gemini tahminlerinden 3-4 kupon seçimi

---

### 🔮 2. Aşama (Sonraya)
- **API-Football** (RapidAPI, ücretsiz tier günde 100 istek) entegrasyonu
- Gemini'ye gerçek zamanlı form, H2H ve sakat/cezalı oyuncu verisi beslenecek
- Analiz kalitesi önemli ölçüde artacak

---

### 💻 Yararlı Komutlar
```powershell
# Backend başlat
cd "C:\Users\Kenan\Desktop\S8 Professor\apps\backend" && npm run dev

# Admin endpoint test
Invoke-WebRequest -Uri "http://localhost:4000/v1/admin/process-weekly-toto" -Method POST -Headers @{"X-Admin-Secret"="H9bIduYyNLUZK1Q2R4VtaAWSnJgCTqc8"} -UseBasicParsing

# Tahminleri oku
Invoke-WebRequest -Uri "http://localhost:4000/v1/predictions/latest" -UseBasicParsing | Select-Object -ExpandProperty Content

# GitHub push
cd "C:\Users\Kenan\Desktop\S8 Professor" && git add . && git commit -m "mesaj" && git push
```
