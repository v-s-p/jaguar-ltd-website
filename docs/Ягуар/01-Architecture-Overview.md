---
title: Architecture Overview
type: architecture
status: active
last_verified: 2026-05-03
---

## Purpose

Jaguar-ltd, Bulgaristan B2B pazarına yönelik çok dilli (7 dil) bir 
endüstriyel makine kataloğudur. İki marka altında 121 makineyi 
statik olarak render eder: Yılmaz (74) ve Göçmaksan (47).

## Key Facts

- **Stack:** Astro 5 + Tailwind 3.4, statik site (SSG)
- **Node:** >=22.12.0
- **Diller:** 7 dil → `en`, `tr`, `ru`, `es`, `ro`, `bg`, `bcs`
- **Default dil:** `bg` (Bulgarca, root path)
- **Component yaklaşımı:** Sayfalar `src/components/pages/` altında, 
  her dil prefix'i aynı bileşeni render eder
- **Veri kaynakları:** İki ayrı JSON (`machines.json` + `gocmaksan.json`), 
  ortak type ile (`src/types/Machine.ts`)
- **Build cache:** Symlink ile `C:\YAZILIM_KASASI\.BUILD_CACHE\Jaguar-ltd\`

## Connections

- [[Data-Layer]] — Hangi veri yapısının render edildiği
- [[i18n-System]] — Dil yönetimi ve URL üretimi
- [[Page-Components]] — Sayfaların component'lere bölünmüş hali
- [[Routing-and-URLs]] — Astro statik path üretimi
- [[Build-and-Cache]] — Symlink tabanlı cache mimarisi

## Source Files

- `astro.config.mjs` — Astro yapılandırması (i18n + integrations)
- `package.json` — Bağımlılıklar (astro@^5, @astrojs/tailwind, tailwindcss)
- `tsconfig.json` — TypeScript yapılandırması
- `src/` — Tüm uygulama kaynağı

## Open Questions

- `astro.config.mjs` içeriği henüz wiki'ye eklenmedi (i18n config detayları)
- `tailwind.config.mjs` özel theme tanımları var mı bilinmiyor