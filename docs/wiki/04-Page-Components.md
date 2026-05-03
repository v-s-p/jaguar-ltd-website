---
title: Page Components
type: component
status: active
last_verified: 2026-05-03
---

## Purpose

Astro statik render gücünü verimli kullanmak için sayfaların component 
tabanlı mimariye dönüştürülmüş hâli. Aynı bileşen tüm dil prefix'lerinde 
kod tekrarı olmadan render edilir.

## Key Facts

- **Konum:** `src/components/pages/`
- **Tüm page bileşenleri:** `HomePage.astro`, `KategoriPage.astro`, 
  `MachinePage.astro`, `AboutPage.astro`, `ContactPage.astro`, `GdprPage.astro`
- **Shared layouts:** `src/layouts/BaseLayout.astro` + `src/layouts/MainLayout.astro`
- **KategoriPage sorumluluğu:** Marka veya kategori bazlı liste 
  (Aluminium / PVC / Gocmaksan)
- **MachinePage sorumluluğu:** Tek makinenin detay sayfası
- **Veri import:** `getStaticPaths` içinde async import 
  (`await import('../../data/machines.json')`)
- **Veri okuma deseni:** `machine.diller?.en || machine.diller?.tr || {}` 
  (fallback zinciri)
- **Marka koşullu mantık:** `brand === 'gocmaksan'` durumunda farklı alan 
  kullanımı (`category` vs `categories`)

## Connections

- [[Architecture-Overview]] — Üst seviye bağlam
- [[Data-Layer]] — Render edilen veri yapısı
- [[Routing-and-URLs]] — `getStaticPaths` üretimi
- [[i18n-System]] — Aktif dile göre render

## Source Files

- `src/components/pages/HomePage.astro` — Ana sayfa
- `src/components/pages/KategoriPage.astro` — Kategori liste sayfası
- `src/components/pages/MachinePage.astro` — Makine detay sayfası

## Open Questions

_(Tüm kritik sorular kapatıldı — 2026-05-03)_