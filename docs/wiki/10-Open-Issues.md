---
title: Open Issues
type: decision
status: active
last_verified: 2026-05-03
---

## Purpose

Tamamlanmamış işlerin, beklenen kararların ve quota/dependency 
beklentilerinin merkezi listesi.

## Key Facts

- **121 makine BG çevirisi:** Gemini quota sıfırlanmasını bekliyor; 
  `auto_translator.py` checkpoint'li, kaldığı yerden devam edecek
- **Migration tamlığı:** v2 migration'ın tüm makinelere uygulandığı 
  doğrulanmamış (üretim spot-check gerekli)
- **`tercume_merkezi.py` durumu:** CLAUDE_MASTER'da bahsedilen ama 
  proje kökünde olmayan dosya — adı değişmiş veya `scripts/` altında 
  olabilir
- **Production deploy:** Hedef platform ve CI/CD durumu netleştirilmemiş
- **Custom 404 / sitemap:** Var/yok bilinmiyor
- **Diğer dil çevirileri:** ru, es, ro, bcs için durum bilinmiyor 
  (BG önceliği üzerinden konuşuldu)
- **Plan dosyası:** `plan.json` (1.2KB) içeriği wiki'ye yansıtılmadı

## Connections

- [[translation-pipeline]] — BG çevirisi bağlamı
- [[Migration-History]] — v2 doğrulama bağlamı
- [[Build-and-Cache]] — Deploy soruları

## Source Files

- `plan.json` — Plan dosyası (içeriği bilinmiyor)
- `JAGUAR_DEV_LOG.md` — Son güncel kayıt 26 Nisan 2026

## Open Questions

- Plan.json'da hangi sıralama tutuluyor?
- Son 1 haftalık DEV_LOG eksikliği bilinçli mi?