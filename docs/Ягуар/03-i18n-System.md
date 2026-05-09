---
title: i18n System
type: component
status: active
last_verified: 2026-05-03
---

## Purpose

Sitenin 7 dilde render edilmesini sağlayan merkezi çoğul dil altyapısı. 
URL'den dil algılama, statik metin sözlüğü ve fallback zinciri içerir.

## Key Facts

- **Desteklenen 7 dil:** `en`, `tr`, `ru`, `es`, `ro`, `bg`, `bcs`
- **Default dil:** `bg` (Bulgarca, root path `/`)
- **Diğer diller:** `/en/`, `/tr/`, `/ru/` vb. prefix ile
- **Sözlük:** `src/i18n/ui.ts` — Navigasyon, butonlar, footer metinleri 
  7 dilde
- **Yardımcılar:** `src/i18n/utils.ts` — URL'den dil algılama, 
  SEO uyumlu URL üretimi
- **Language Picker:** `src/components/LanguagePicker.astro` — Header/Footer 
  dropdown
- **Fallback zinciri:** Aktif dil → İngilizce → Bulgarca (orijinal)
- **Önceki durum:** 10 dil tanımlıydı (hatalı), 26 Nisan'da 7'ye sınırlandı

## Connections

- [[Architecture-Overview]] — Sistem haritasındaki yeri
- [[Routing-and-URLs]] — Dil prefix'li route'ların üretimi
- [[Page-Components]] — Bileşenlerin aktif dile göre render'ı
- [[translation-pipeline]] — `diller.*` alanlarının doldurulması

## Source Files

- `src/i18n/ui.ts` — 7 dilde statik metin sözlüğü
- `src/i18n/utils.ts` — Dil algılama + URL fonksiyonları
- `src/components/LanguagePicker.astro` — Dropdown UI
- `src/data/siteMetadata.ts` — Dil dizisi (7 dil)

## Open Questions

- `astro.config.mjs` içindeki i18n config detayları (defaultLocale, 
  locales array, routing strategy) henüz wiki'ye yansıtılmadı