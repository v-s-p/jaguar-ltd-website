# Faz C — Dil Temizligi (22.05.2026)

[[Jaguar]] / _meta / language-cleanup

## TL;DR
7 dil -> 3 dil. BG/EN/RU aktif. TR/ES/RO/BCS kaldirildi.
Tek dosya degisikligi: `src/i18n/ui.ts`.

## Etkilenen Dosyalar
| Dosya | Eylem |
|-------|-------|
| `src/i18n/ui.ts` | `languages` + `ui` objesinden tr/es/ro/bcs bloklari silindi |
| `src/i18n/utils.ts` | Degisiklik gerekmedi — `Object.keys(ui)` dinamik |
| `astro.config.mjs` | Degisiklik gerekmedi — Astro i18n plugin kullanilmiyor |
| `src/data/siteMetadata.ts` | Degisiklik gerekmedi — zaten `["bg", "en", "ru"]` |
| `src/components/LanguagePicker.astro` | Degisiklik gerekmedi — `Object.entries(languages)` dinamik |

## Silinen Dil Bloklari
- `tr` (Turkce) — 57 satir
- `es` (Espanol) — 30 satir
- `ro` (Romana) — 30 satir
- `bcs` (Balkan/BCS) — 28 satir

## Mimari Not
Bu projedeki i18n tamamen `src/i18n/ui.ts` merkezli:
- `languages` objesi = dil secici dropdown icerigi
- `ui` objesi = her dil icin ceviri key/value
- `getLanguagePaths()` = `Object.keys(ui)` -> Astro static path uretimi
- `getLangFromUrl()` = `url.pathname` + `lang in ui` kontrolu

Yani tek bir dosyada trim = tum akis otomatik guncellenir. Locale dosyalari yok.

## Smoke Test Sonuclari (22.05.2026)
- Build: 568 sayfa, 0 hata
- dist/ kok: bg/ en/ ru/ — tr/ es/ ro/ bcs/ yok
- LanguagePicker HTML: Bulgarca/English/Rusca 3x, Turkce/Espanol/Romana/Balkan 0x

## Lesson
i18n trim bu projede tek-dosya islem. Baska projelerde:
- Astro i18n plugin kullanilyorsa `astro.config.mjs` -> `i18n.locales` de guncellenmeli
- Ayri locale dosyalari varsa (`src/locales/tr.json` gibi) onlari da silmeli
- Import audit olmadan silme — baska yerde import varsa build patlar
