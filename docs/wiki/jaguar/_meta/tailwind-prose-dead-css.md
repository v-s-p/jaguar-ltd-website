# Tailwind `prose` Sinifi — Dead CSS

[[Jaguar]] / _meta / lessons-learned

## Bulgu (22.05.2026)
`AboutPage.astro` (ve potansiyel baska yerler) `prose` Tailwind sinifi kullaniyor.
Ama `tailwind.config.mjs` → `plugins: []` — `@tailwindcss/typography` yuklu degil.

## Etki
`prose` silent no-op. AboutPage tarayici default'lariyla render ediliyor (tipografik tutarlilik yok).
Markdown icerigi baslik/paragraf/liste stilsiz goruntuleniyor.

## Etkilenen Dosyalar
- `src/components/pages/AboutPage.astro` — `prose` sinifi kullaniyor, efektsiz
- (Kontrol et: diger Page bilesenlerinde `prose` var mi?)

## Workaround (MachinePage — 22.05.2026)
`MachinePage.astro` icin scoped `<style>` bloggu eklendi:
```css
.machine-description :global(h2) { font-size: 1.1rem; font-weight: 700; ... }
.machine-description :global(p)  { margin-bottom: 0.75rem; line-height: 1.65; }
/* ... */
```
Bu, `prose` plugin olmadan markdown HTML'ini stilize ediyor.

## Cozum Secenekleri
- **A (Onerilir):** `npm install -D @tailwindcss/typography` + `tailwind.config.mjs`'e ekle:
  ```js
  plugins: [require('@tailwindcss/typography')]
  ```
  Ardindan AboutPage `<div class="prose">` hemen calisir; MachinePage scoped style sokulabilir.
- **B:** `prose` kullanimlarini sokup scoped style'lara gec. Tutarlilik icin A daha temiz.

## Status
Deploy gate degil. Sprint sonrasi tek PR'da cozulur.
Referans: `JAGUAR_DEV_LOG.md` — 2026-05-22 [09:30] notu.
