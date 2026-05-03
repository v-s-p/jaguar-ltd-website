---
title: Translation Pipeline
type: pipeline
status: active
last_verified: 2026-05-03
---

## Purpose

121 makinenin 7 dile (özellikle Bulgarca) otomatik çevirisini Gemini API 
üzerinden yürüten checkpoint'li, kaldığı yerden devam eden batch script.

## Key Facts

- **Ana script:** `scripts/auto_translator.py` ✅ (`scripts/` altında doğrulandı)
- **Merkez script:** `scripts/tercume_merkezi.py` ✅ (`scripts/` altında doğrulandı)
- **Stateful yapı:** `translation_status.json` ile checkpoint tutar
- **Resilience:** API limit hatasında graceful shutdown, restart'ta 
  kaldığı yerden devam
- **API sağlayıcısı:** Google Gemini
- **API key konumu:** `C:\Users\Kenan\Desktop\.ENVs\kuafor-backend\.env` 
  → `GEMINI_API_KEY`
- **Hedef alan:** Her makinenin `diller.bg` (ve diğer 6 dil) içeriği
- **Mevcut durum:** 121 makine BG çevirisi henüz tamamlanmadı, 
  Gemini quota sıfırlanmasını bekliyor
- **Test çıktısı:** `tercume_test_sonuc.json` (~17KB) — örnek çeviri 
  sonuçları
- **Yardımcı:** `setup_i18n.py` (~2.4KB) — i18n bootstrap

## Connections

- [[Data-Layer]] — Doldurulan `diller.*` alanları
- [[i18n-System]] — Çevirilerin tüketildiği katman
- [[Open-Issues]] — Quota bekleyen bekleyen iş

## Source Files

- `scripts/auto_translator.py` — Ana otonom translator ✅
- `scripts/tercume_merkezi.py` — Çeviri merkez betiği ✅
- `scripts/zenginlestirici.py` — Veri zenginleştirici (scripts/ altında)
- `mempalace.yaml` — MemPalace indeksleme yapılandırması (proje kökünde, 
  6 oda: arsiv, public, resimler, scripts, site_analysis, src/frontend)

## Open Questions

- `translation_status.json` mevcut state'i nedir?