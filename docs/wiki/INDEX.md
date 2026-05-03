---
title: Jaguar-ltd Wiki Index
type: index
status: active
last_verified: 2026-05-03
---

# Jaguar-ltd Knowledge Graph

Karpathy-Wiki yöntemi: her node bağımsız bir bilgi parçası, `[[bağlantı]]` 
ile graph'a bağlı. Kod taraması yerine wiki sorgusu → token tasarrufu.

## Nodes

| # | Node | Tip | Tek satır |
|---|---|---|---|
| 01 | [[Architecture-Overview]] | architecture | Astro 5 + 7 dil + 121 makine, statik B2B katalog |
| 02 | [[Data-Layer]] | data | machines.json (74) + gocmaksan.json (47) + Machine.ts |
| 03 | [[i18n-System]] | component | 7 dil sözlüğü, dil algılama, fallback zinciri |
| 04 | [[Page-Components]] | component | HomePage / KategoriPage / MachinePage |
| 05 | [[Routing-and-URLs]] | architecture | Dil prefix'li dinamik path üretimi |
| 06 | [[translation-pipeline]] | pipeline | Gemini + checkpoint'li auto translator |
| 07 | [[scraper-pipeline]] | pipeline | Yılmaz + Göçmaksan scraper'lar, blacklist |
| 08 | [[Migration-History]] | decision | v1 → v2 format geçişi, kararlar |
| 09 | [[Build-and-Cache]] | deployment | YAZILIM_KASASI symlink mimarisi |
| 10 | [[Open-Issues]] | decision | BG çevirisi, deploy, doğrulama bekleyenler |

## Quick Navigation

- **Yeni başlıyorsan:** [[Architecture-Overview]] → [[Data-Layer]] → [[Page-Components]]
- **Çeviri işi:** [[translation-pipeline]] → [[i18n-System]]
- **Veri eklemek:** [[scraper-pipeline]] → [[Data-Layer]] → [[Migration-History]]
- **Deploy:** [[Build-and-Cache]] → [[Open-Issues]]

## Maintenance

- VERIFY.md → Doğrulanmamış iddialar
- Yeni node eklerken: bu INDEX'e satır ekle, en az 2 [[bağlantı]] kur
- Canonical naming: PascalCase (component/architecture), kebab-case (pipeline)