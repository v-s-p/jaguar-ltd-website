---
title: Verification Pending
type: meta
status: active
last_verified: 2026-05-03
---

# Doğrulanması Gereken İddialar

Bu liste wiki kurulumu sırasında "Open Questions" altında biriken, 
repo taraması ile kapatılması gereken iddialardır.

## Yüksek Öncelik

- [x] `scripts/` klasörü içeriği — 15 betik doğrulandı (07-scraper-pipeline)
- [x] `tercume_merkezi.py` gerçekten var mı — EVET, `scripts/tercume_merkezi.py`
- [x] `auto_translator.py` `scripts/` altında mı — EVET, `scripts/auto_translator.py`
- [x] `astro.config.mjs` içeriği — integrations: `[tailwind()]`, i18n yok, 
      vite.fs.allow ile junction cache yolu (09-Build-and-Cache)
- [x] `src/pages/` dosya yapısı — 13 dosya/yol doğrulandı (05-Routing-and-URLs)
- [x] `src/types/Machine.ts` tam interface — 4 anahtar doğrulandı (02-Data-Layer)

## Orta Öncelik

- [x] `src/components/pages/` bileşen listesi — 6 bileşen: HomePage, 
      KategoriPage, MachinePage, AboutPage, ContactPage, GdprPage
- [x] `Layout.astro` var mı — EVET: `BaseLayout.astro` + `MainLayout.astro` 
      (`src/layouts/` altında)
- [x] `tailwind.config.mjs` özel theme — brand renkler + fontFamily Segoe UI
- [x] `radar2.py` rolü — yilmazmachine.com.tr HTML yapı keşif scripti (07-scraper-pipeline)
- [x] `plan.json` içeriği — 5 adımlı proje ilerleyiş takibi, step 5 tamamlanmamış
- [x] `mempalace.yaml` — 6 oda indeksliyor (arsiv, public, resimler, scripts, 
      site_analysis, src/frontend)

## Düşük Öncelik

- [ ] `BUTON_FIX.md`, `PDF_FIX.md`, `SPECS_KATALOG_FIX.md` özetleri 
      ilgili node'lara yansıtılmalı
- [ ] `site_analysis/` klasörü içeriği
- [ ] `resimler/` klasörü `public/images/` ile farkı ne?
- [ ] Custom 404 sayfası ve sitemap üretimi
- [ ] Production deploy hedefi

## Kapatma Protokolü

Her doğrulanan madde:
1. İlgili node'da Open Questions'tan kaldırılır
2. Key Facts'e taşınır (gerçek değerlerle)
3. Bu listede satır işaretlenir veya silinir
4. `last_verified` tarihi güncellenir

---

**Not:** Bu liste Claude Code ile repo taranarak kapatılabilir. Her madde 
ortalama 1-2 dosya okumayla cevaplanır.