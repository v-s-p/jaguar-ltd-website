---
title: Scraper Pipeline
type: pipeline
status: active
last_verified: 2026-05-03
---

## Purpose

Yılmaz ve Göçmaksan üretici sitelerinden makine verilerini çekip 4 standart 
JSON anahtarına uygun çıktı üreten Python betikleri.

## Key Facts

- **Ortak şema:** Scraper'lar `src/types/Machine.ts` standardına uygun 
  JSON üretir
- **Standart anahtarlar:** `subcategory: string[]` ve `specs` 4 standart 
  anahtar (DEV_LOG kaynaklı)
- **Görsel filtreleme:** Blacklist sistemi → `logo`, `toolquaz`, `uvaga`, 
  `banner` gibi yardımcı görseller atılır
- **Çıktı dosyaları:** `src/data/yilmaz.json` + `src/data/gocmaksan.json`
- **Görsel konumu:** `public/images/yilmaz/` (Yılmaz), 
  `public/images/gocmaksan/` (Göçmaksan)
- **`radar2.py` rolü:** ✅ Doğrulandı — yilmazmachine.com.tr'nin tek bir 
  ürün sayfasını (`/urunler/aim-7420/`) çekip h2-h4, ul/ol ve p tag 
  sınıflarını basan tek-kullanımlık HTML yapı keşif scripti
- **scripts/ klasörü içeriği:** `radar_teknik.py`, `zenginlestirici.py`, 
  `resim_eslestirici.py`, `duzeltici.py`, `acil_fix.py`, `resim_temizle.py`, 
  `patch_isim.py`, `temizleyici.py`, `tercume_merkezi.py`, `auto_translator.py`, 
  `gocmaksan_guncelleyici.py`, `yilmaz_guncelleyici.py`, `migrate_v2.py`, 
  `enrich_machines.py`, `yilmaz_guncelleyici_backup.py`

## Connections

- [[Data-Layer]] — Üretilen JSON dosyaları
- [[Migration-History]] — Standart şema kararı
- [[Architecture-Overview]] — Sistem haritası

## Source Files

- `radar2.py` — HTML yapı keşif scripti (tek kullanımlık) ✅
- `scripts/yilmaz_guncelleyici.py` — Yılmaz verisi güncelleyici
- `scripts/gocmaksan_guncelleyici.py` — Göçmaksan verisi güncelleyici
- `scripts/resim_eslestirici.py` — Görsel eşleştirme
- `scripts/zenginlestirici.py` — Veri zenginleştirme
- `scripts/migrate_v2.py` — v1→v2 migration
- `scripts/enrich_machines.py` — Makine veri zenginleştirme
- `scripts/blacklist/` — Filtrelenen görsel dosyaları (klasör mevcut)
- `public/images/yilmaz/` — Yılmaz görselleri
- `public/images/gocmaksan/` — Göçmaksan görselleri

## Open Questions

- Blacklist tanımı hardcoded mi, ayrı config mi?
- Scraper çalıştırma protokolü/dökümantasyonu var mı?