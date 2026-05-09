---
title: Routing and URLs
type: architecture
status: active
last_verified: 2026-05-03
---

## Purpose

Astro'nun statik path üretim mekanizması üzerinden 7 dil × 121 makine 
× kategori sayfalarının URL şemasını yönetir.

## Key Facts

- **Default dil URL'i:** Root path (`/`) Bulgarca'ya gider
- **Diğer diller:** `/en/`, `/tr/`, `/ru/`, `/es/`, `/ro/`, `/bcs/` 
  prefix
- **Kategori sayfaları:** `/{lang}/kategori/{kategori}` — örn. 
  `/tr/kategori/aluminyum`, `/tr/kategori/pvc`, `/tr/kategori/gocmaksan`
- **Makine detay:** `/{lang}/machines/{slug}` — örn. 
  `/tr/machines/ack-420-s-up-cutting-saw-machine`
- **Statik path mantığı:** `getStaticPaths` her bileşende veriyi import 
  edip params + props döndürür
- **catName mapping:** `aluminyum → Aluminium`, `pvc → PVC`, 
  `gocmaksan → Gocmaksan` (props.catName olarak iletiliyor)
- **Filtre:** `cats.some(c => c.toLowerCase() === catName.toLowerCase())`

## Connections

- [[Page-Components]] — `getStaticPaths` barındıran bileşenler
- [[i18n-System]] — Dil prefix mekanizması
- [[Data-Layer]] — Path üretiminde okunan JSON
- [[Architecture-Overview]] — Sistem haritası

## Source Files

- `src/pages/` — Astro file-based router giriş noktası
- `src/components/pages/KategoriPage.astro` — Kategori path üretimi
- `src/components/pages/MachinePage.astro` — Makine path üretimi
- `astro.config.mjs` — i18n routing yapılandırması

## Key Facts (ek)

- **src/pages/ tam yapısı:**
  - `index.astro`, `about.astro`, `contact.astro`, `gdpr.astro` — root (default dil)
  - `[lang]/index.astro`, `[lang]/about.astro`, `[lang]/contact.astro`, `[lang]/gdpr.astro`
  - `kategori/[kategori].astro`, `[lang]/kategori/[kategori].astro`
  - `machines/[slug].astro`, `[lang]/machines/[slug].astro`
  - `kategori/gocmaksan.astro` — Göçmaksan için sabit sayfa

## Open Questions

- Custom 404 sayfası var mı bilinmiyor
- Sitemap üretimi yapılandırılmış mı?