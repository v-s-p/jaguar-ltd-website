# Data Architecture — Individual + Aggregate Pattern

[[Jaguar]] / _meta / architecture

## TL;DR
Individual file'lar **canonical**, aggregate **derived**. Düzenleme her zaman individual'da, CI sync'ler.

## Akış

```
src/data/machines/<firma>/<slug>.json     ← canonical
         ↓
scripts/sync_machines_to_json.py          ← aggregate üretir
         ↓
src/data/<firma>.json                     ← derived
         ↓
MachinePage / KategoriPage / HomePage     ← aggregate okur
```

## CI
`.github/workflows/cms-sync.yml` — push'ta otomatik. Lokal de manuel çalıştırılabilir:
```
py scripts/sync_machines_to_json.py
```

## Firmalar
| Firma | Individual dir | Aggregate |
|---|---|---|
| Yılmaz | `src/data/machines/yilmaz/` | `src/data/yilmaz.json` |
| Göçmaksan | `src/data/machines/gocmaksan/` | `src/data/gocmaksan.json` |

## Lessons Learned
- **22.05.2026 prose enrichment:** Script individual'a yazdı, "yanlış dosya" sandık. Aggregate sync'le tutarlıydı — panik gereksizdi.
- Düzenleme yaparken **her zaman** individual file'a git. Aggregate'i el ile edit etme — bir sonraki sync overwrite eder.
- Local'de mass change sonrası `py scripts/sync_machines_to_json.py` çalıştır → `git diff src/data/<firma>.json` ile aggregate'i de doğrula.

## CMS (Sveltia/Decap)
Sveltia CMS `public/admin/config.yml` üzerinden GitHub API ile individual file'ları düzenler. Her CMS commit ayrı bir `github-actions[bot]` push'u üretir — bu da cms-sync'i tekrar tetikler.

## CMS Sync Failure Notu (22.05.2026)
`github-actions[bot]` 403 hatası: repo Settings → Actions → General → Workflow permissions → "Read and write permissions" seçili değil. Non-blocking (aggregate manuel commit'te dahil) ama düzeltilmeli.
