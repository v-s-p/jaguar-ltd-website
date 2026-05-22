## 2026-05-22 [14:00] — Faz C: Dil temizligi (stage)

7 dil -> 3 dil (BG/EN/RU). TR/ES/RO/BCS kaldirildi.

**Degistirilen:** `src/i18n/ui.ts` — `languages` + `ui` objesinden 4 dil blogu silindi (145 satir)
**Silinen locale dosyalari:** Yok — tum ceviriler ui.ts icinde
**Lokal smoke (npm run build):** 568 sayfa, 0 hata. BG/EN/RU dist/ uretildi, TR/ES/RO/BCS yok. Selector dropdown 3 dil.

**Staged (commit bekleniyor — Ken'in karari):** `src/i18n/ui.ts`

**Onerilen commit mesaji:**
```
chore: trim languages to BG/EN/RU (remove TR/ES/RO/BCS)

- src/i18n/ui.ts: languages + ui objects trimmed to bg/en/ru
- /tr/, /es/, /ro/, /bcs/ routes no longer generated (404)
- No redirects needed (pages were never live/indexed)
- LanguagePicker + getLanguagePaths() auto-updated (dynamic from ui.ts)
```

**Wiki note (yeni):** `docs/wiki/jaguar/_meta/language-cleanup.md`

**Bekleyen (Ken):**
- `git diff --stat` ile inceleme
- `git commit + push` (commit mesaji onerisi yukarida)
- Push sonrasi Cloudflare cache purge (onceki sprint'ten henuz yapilmadiysa birlikte)

---

## 2026-05-22 [11:00] — Sprint Kapanis: Deploy + Wiki

**Commit:** `acc8305` — `feat: gocmaksan prose enrichment + markdown render` (47 dosya, 285 insertion)
**Push:** `origin/main` — success (CMS rebase sonrasi: `git stash` + `git pull --rebase` + `git push`)
**GitHub Action `cms-sync`:** completed failure — pre-existing `github-actions[bot]` 403 push permission. Non-blocking (aggregate commit'e dahil edildi). Ken duzeltmeli: repo Settings -> Actions -> General -> "Read and write permissions".
**Cloudflare Pages deploy:** Push'ta otomatik tetiklendi (~1-2 dk build ETA).
**Cache purge:** Ken'e flag — wrangler auth/proje adi bilinmiyor, manuel purge: Cloudflare dashboard -> jaguar.ataerk.com zone -> Caching -> Purge Everything.

**Canli smoke (curl, nocache param ile):**
- Gocmaksan zengin (gms-sls-12): h2=3, ham ##=0 -> OK
- Gocmaksan stub (gms-oturak-makaslari): h2=0, ham ##=0 -> OK
- Yilmaz (ack-420-s): h2=0, ham ##=0, br=1 (paragraf korundu) -> OK, regression yok

**Wiki notes (yeni):**
- `docs/wiki/jaguar/_meta/data-architecture.md`
- `docs/wiki/jaguar/_meta/tailwind-prose-dead-css.md`

**Bekleyen (Ken):**
- `tercume_merkezi.py` BG/RU re-run (rate-limited, planli)
- `@tailwindcss/typography` plugin (AboutPage dead prose CSS)
- `.gitignore` cleanup: `_backup/`, `_enrichment_log.json`, `pdf_extraction/`, eski backup JSON'lari
- GitHub Actions write permission fix (yukarida)
- Cloudflare cache purge (yukarida)

---

## 2026-05-22 [09:30] — gms-b-45x1 Retry + MachinePage Markdown Render

**Retry:** `gms-b-45x1` — status: ok, 990 chars, `## Overview` confirmed. Re-sync: `scripts/sync_machines_to_json.py` aggregate güncellendi. Effective coverage: 39/47 (8 pdf_missing beklenen).

**Markdown render:** `MachinePage.astro` `set:html` + `marked` v18 (`breaks: true, gfm: true`).
Etkilenen:
- `src/components/pages/MachinePage.astro` — `descriptionHtml = marked.parse(aciklama)`, `<div set:html>`, scoped `<style>` `.machine-description :global(h2/h3/p/ul/li/strong)`, `seoDescription` strip → BaseLayout meta
- `src/components/pages/KategoriPage.astro` — `makeExcerpt()` helper, kart `{aciklama}` → `{makeExcerpt(aciklama)}` (EK: gocmaksan.astro da dahil edildi — aynı issue, `line-clamp-2` kartı)
- `src/pages/kategori/gocmaksan.astro` — aynı `makeExcerpt()`, kart strip uygulandı
- `package.json` — `marked ^18.0.4` eklendi
- CSS notu: Tailwind Typography plugin yüklü değil (`plugins: []`), `prose` sınıfı çalışmıyor. Scoped style bloğu MachinePage.astro içine eklendi.

**Smoke test:**
- Göçmaksan-zengin (sls-12): h2=3 ✓, ham ##=0 ✓ → OK
- Göçmaksan-stub (oturak-makaslari): h2=0 (beklenen) ✓, ham ##=0 ✓ → OK
- Yılmaz (ack-420-s): h2=0 ✓, ham ##=0 ✓, br=1 ✓ (paragraf korundu) → OK, regression yok

**Bekleyen — DEPLOY ETME:**
1. `py scripts/tercume_merkezi.py` — BG/RU çeviriler zengin EN prose'a tazelensin
2. `git add` + commit + push (Ken; CI sync push'ta tetiklenir)
3. Cloudflare cache purge
4. `_meta/data-architecture.md` wiki notu (Ken)

---

## 2026-05-22 — Göçmaksan Prose Enrichment Mass Run

**Yapılan:** 47 Göçmaksan makinesi için `diller.en.description` PDF kataloglarından zenginleştirildi.
Pipeline: `tools/enrich_gocmaksan_descriptions.py` (Gemini 2.5 Flash + PDF inline base64, REST API).
Yürütme: Hermes (ön koşul + sample real-write) → Claude Code (arch teşhis + mass run + sync + DEVLOG).

**Sonuç:**
- ok: 38 (## Overview / ## Key Benefits / ## Engineering Highlights başlıklı zengin prose)
- pdf_missing: 8 (Hand Tools 6 + Light Construction 2 — beklenen)
- gemini_error: 1 (gms-b-45x1, transient "high demand" — yeniden çalıştırılabilir)

**Backup:** `_backup/pre_enrichment_gocmaksan_20260522_084416/`
**Etkilenen dosyalar:** `src/data/machines/gocmaksan/*.json` (38 dosya) + `src/data/gocmaksan.json` (aggregate)
**Data architecture confirmed:** Individual files canonical (`src/data/machines/gocmaksan/<slug>.json`),
aggregate `src/data/gocmaksan.json` derived — sync: `scripts/sync_machines_to_json.py` lokal çalıştırıldı
(GitHub Action `.github/workflows/cms-sync.yml` aynı işi push'ta yapardı; lokalde mirror için yapıldı).

**Bekleyen — DEPLOY ETME:**
1. `MachinePage.astro` markdown render PR — yoksa "## Overview" string basar
2. `tercume_merkezi.py` re-run — BG/RU çeviriler zengin prose'a tazelensin
3. `git add` + commit + push + Cloudflare cache purge
4. (Sonra) `_meta/data-architecture.md` wiki notu ekle
5. gms-b-45x1 retry (1 gemini_error, `--slug gms-b-45x1-... ` ile)

---

- [2026-05-15 23:00:00] | Claude+Codex | Bug Fix Sprint | 1) machines.json→yilmaz.json HomePage.astro referans fix (b394b06) 2) teknikTablo svg/PRODUCT INFO kirli data filtresi + type separator (72f038f) 3) Gocmaksan specs root-level fallback: machine.specs (a526f9a) Site CANLI, build OK, 1152 sayfa. Sonraki: Gocmaksan technical_data scraper fix, BG/RU çeviri, Desktop→GIT_KASASI birleştirme.
- [2026-05-15 22:00:00] | Claude+Code | Gocmaksan Specs Tamamlandı | 47/47 makine specs dolu. Steel Factory 8/8 (Axis50S, Matrix55, Matrix55S, SLS12, Synclone45S, HB12x3, HB12x6, MH8C). Hand Tools 6/6. Tüm specs İngilizce. missing_specs=0. | Sonraki: BG/RU çeviri, UI branding, route conflict fix.
- [2026-05-15 21:00:00] | Claude+Code+Codex | Gocmaksan Sprint | gocmaksan_guncelleyici.py specs parser düzeltildi (FEATURED FEATURES + TECHNICAL DATA + CAPACITIES). 47 makine işlendi, 29/47 specs dolu. Resimler {slug}_{index} formatına rename edildi. 14 Steel Factory/Hand Tools makinesi specs boş — sayfa yapısı farklı, sonraki sprint. Build cache EPERM sorunu ortam kaynaklı. | Sonraki: 14 makine specs, BG/RU çeviri, UI branding, route conflict fix.
- [2026-05-15 19:30:00] | Claude+Codex | Resim Rename + Branding + 90 Makine | machines.json→yilmaz.json, /images/machines/→/images/yilmaz/, 38 dosyada referans güncellendi. 499 resim {slug}_{index} formatına rename edildi. alm-6510 ve mem-128 orphan makineler JSON'a eklendi (90 makine). missing_paths=0, build hatasız. | Sonraki: Gocmaksan sprint, BG/RU çeviri, UI branding.
- [2026-05-15 17:00:00] | Claude+Codex | Veri Yeniden Yapılandırma + Frontend Güncelleme | yilmaz_guncelleyici.py yeniden yazıldı: sitemap yerine hardcoded KATEGORI_AGACI (category/subcategory/type 3 seviye). 88 makine (86 Yılmaz + VCE 3500/4000 local). Specs key'leri EN'e çevrildi. KategoriPage subcategoryMap+subTranslationKeys güncellendi. MachinePage type badge + geri butonu fix + i18n key eklendi. Build hatasız. | Sonraki: resim SEO rename, Gocmaksan sprint, BG/RU çeviri.
- [2026-04-26 12:48:00] | Antigravity | Log dosyasının oluşturulması | Kullanıcı talimatı (ADIM 1) | Mimari düzeltme adımına geçildi.
- [2026-04-26 12:49:00] | Antigravity | Dil Dizisi Senkronizasyonu | src/data/siteMetadata.ts içindeki hatalı 10 dil, master plana uygun olarak 7 dil ("en", "tr", "ru", "es", "ro", "bg", "bcs") ile sınırlandırıldı. (ADIM 2) | Otonom çeviri betiği yazımına geçildi.
- [2026-04-26 12:50:00] | Antigravity | Stateful Otonom Çeviri Betiği Oluşturuldu | scripts/auto_translator.py yazıldı. translation_status.json ile hafıza (checkpoint), API limitlerinde graceful shutdown ve resume (kaldığı yerden devam) özellikleri eklendi. (ADIM 3) | Anayasa kurallarına geçildi.
- [2026-04-26 12:51:00] | Antigravity | Otonom Okuma Kuralı (Anayasa) Eklendi | Proje ana dizininde .cursorrules dosyası oluşturuldu ve ZORUNLU KURAL 1 ve KURAL 2 işlendi. (ADIM 4) | Raporlama yapılıyor.
- [2026-04-26 14:15:00] | Antigravity | JSON Veri Tipi ve Scraper Şeması Standartizasyonu | src/types/Machine.ts oluşturuldu (subcategory string[], specs 4 standart anahtar). yilmaz.json ve gocmaksan.json dosyalarındaki veri yapıları bu standarda dönüştürüldü. Python scraper (veri çekici) betikleri bu 4 standart anahtara uygun JSON çıktısı verecek şekilde güncellendi. | İşlem tamamlandı.
- [2026-04-26 14:31:00] | Antigravity | Görsel Temizliği ve UI Düzeltmesi | Scraper blacklist'i güçlendirildi (logo, toolquaz, uvaga, banner). yilmaz.json içindeki çöp resimler temizlendi. Astro bileşenlerinde subcategory (string[]) verisinin join() ile gösterimi sağlandı. | UI ve veri temizliği tamamlandı.

