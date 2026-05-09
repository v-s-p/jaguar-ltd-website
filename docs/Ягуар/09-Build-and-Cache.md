---
title: Build and Cache
type: deployment
status: active
last_verified: 2026-05-03
---

## Purpose

Build artifactlerinin (`.astro`, `.cache`, `dist`, `node_modules`) ana 
projeden ayrı bir disk konumunda symlink ile tutulduğu cache mimarisi.

## Key Facts

- **Symlink hedefi:** `C:\YAZILIM_KASASI\.BUILD_CACHE\Jaguar-ltd\`
- **Symlink edilen klasörler:**
  - `.astro` — Astro derleme cache
  - `.cache` — Genel cache
  - `dist` — Production build çıktısı
  - `node_modules` — Bağımlılıklar (~228KB lock dosyası)
- **Git ayrımı:** `.git` da symlink → `C:\YAZILIM_KASASI\.GIT_KASASI\Jaguar-ltd\.git`
- **Komutlar:**
  - `npm run dev` → `astro dev`
  - `npm run build` → `astro build`
  - `npm run preview` → `astro preview`
- **Build doğrulama:** Tüm 7 dil için statik sayfaların hatasız üretildiği 
  doğrulandı (walkthrough.md)
- **astro.config.mjs integrations:** `[tailwind()]` — sadece Tailwind CSS, 
  i18n entegrasyonu yok (dil prefix'leri manuel file-based routing ile yapılmış)
- **Vite fs.allow:** Junction bağlantısı ile `.BUILD_CACHE` node_modules'e 
  `C:/YAZILIM_KASASI/.BUILD_CACHE/Jaguar-ltd/node_modules` ve 
  `C:/Users/Kenan/Desktop/.BUILD_CACHE/Jaguar-ltd/node_modules` izni verilmiş

## Connections

- [[Architecture-Overview]] — Üst seviye sistem
- [[Routing-and-URLs]] — Build edilen statik path'ler

## Source Files

- `package.json` — Script tanımları
- `astro.config.mjs` — Build yapılandırması
- `tsconfig.json` — TypeScript build ayarları
- `tailwind.config.mjs` — Tailwind yapılandırması

## Open Questions

- Production deploy hedefi neresi? (Vercel/Netlify/Cloudflare Pages?)
- CI/CD pipeline var mı?