## 2026-06-02 — UI Temizlik + CI Pipeline Yeniden Tasarım

**Duration:** ~4h  
**Branch:** main  
**Commits:** `08f8749` → `0376819` → `9239f86` → `256ab8f` → `4cf6696`

### Done

**UI — 3 Display Değişikliği (`08f8749`):**
- Hero slider: YILMAZ makine kartlarında tam isim yerine sadece model kodu gösteriliyor (split on ` - `, brand kontrolü ile — display-only, JSON'a dokunulmadı)
- Alüminyum kategorisi: `Saw Cutting` subcategory, `Cutting` ile birleştirildi — 16 canonical JSON + `ordering.json` + `subcategory_labels.json` + `i18n/ui.ts` (3 dil) + `yilmaz.json` resync
- Partner yazısı: `hero.partner.since`'tan "Bulgaria / България / Болгария" kaldırıldı (3 dil)

**UI — Kart Tag Temizliği (`0376819`):**
- `KategoriPage.astro` + `MachinePage.astro`: makine kartlarından `subcategory` ve `type` tag'leri kaldırıldı — sadece isim + açıklama + buton kalıyor
- CDC 600 BG açıklaması: `AVTOMATICHNA` × 4 → `автоматична`, `DVUGLAVA` → `двуглава` (Latin transliterasyon hatası düzeltildi)

**CI — Kırık Referans Fix (`9239f86`):**
- `site_taxonomy_sync.py`: `MACHINES_JSON = "machines.json"` → `"yilmaz.json"` (per-brand migration sonrası güncellenmemişti)
- `taxonomy-sync.yml` PR body + `translate.yml` `git add` satırı aynı şekilde güncellendi
- Bu fix olmadan GitHub Actions `FileNotFoundError` ile crash ediyordu

**CI — Node.js 24 Opt-in (`256ab8f`):**
- 3 workflow'a `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true` eklendi
- 16 Haziran 2026 deprecation deadline'ı için gerekli

**CI — 3 Fazlı Güvenli Makine Ekleme Pipeline'ı (`4cf6696`):**
- **Sorun:** Eski `taxonomy-sync` + `translate` workflow'ları doğrudan `yilmaz.json`'a yazıyordu; CMS editi sonrası `cms-sync` bunları overwrite edebilirdi
- **Çözüm:** Siteye etkisi olmayan staging sistemi
  - `scrape_discovery.py` → sadece YENİ makineleri `src/data/_staging/new_machines_YYYY-MM.json`'a yazar, mevcut makinelerdeki farkı rapor eder (uygulamaz)
  - `translate_staging.py` → staging JSON'u Gemini ile BG+RU çevirir, siteye yazmaz
  - `apply_staging.py` → admin onayı sonrası sadece YENİ individual JSON dosyaları oluşturur, mevcutlara DOKUNMAZ; yilmaz.json rebuild eder
  - Her faz sonunda tüm adminlere detaylı email + adım adım talimat (GitHub Actions URL'leri dahil)
  - Eski `taxonomy-sync.yml` + `translate.yml` disabled olarak arşivlendi
- **Gerekli secrets:** `ADMIN_EMAILS`, `MAIL_SERVER`, `MAIL_USERNAME`, `MAIL_PASSWORD`

### Blockers
- Email secrets (`ADMIN_EMAILS` vb.) henüz GitHub'a eklenmedi — admin manuel ekleyecek

### Next
1. GitHub Secrets'a mail bilgilerini ekle (`Settings → Secrets → Actions`)
2. `scrape-discovery.yml`'i manuel tetikleyerek pipeline'ı test et
3. İlhan içerik sprint — GMS + Yılmaz makine verileri tamamlama

### Commit
`docs(devlog): 2026-06-02 UI cleanup + CI pipeline redesign`

---

## 2026-05-30 — Step 1.7.1: Header Mega-Menu Ordering Fix

**Duration:** ~30dk  
**Branch:** main  
**Commits:** `8d9dbc6` → `c6419be`

### Done

**Audit (Adım 1):**
- Rebar mega-menu **hardcoded** 6 `<li>` bulundu — `gocmaksan.astro`'dan kopyalanmış, ordering.json'a bağlı değil
- Aluminium + PVC zaten `getSubcategoryOrder()` kullanıyordu; Rebar kaçırılmıştı
- Ken'in tespiti doğrulandı: header sırası ≠ kategori sayfası sırası (bağımsız kaynak)

**Fix — Rebar Dynamic Binding (`8d9dbc6`):**
- `src/utils/ordering.ts`: `getHeaderSubcategoryOrder(material)` eklendi — `header_subcategory_override` kontrol eder, boşsa `getSubcategoryOrder()` fallback
- `Navbar.astro`: `gocmaksan.json` import, `rebarSubcategories = sortByOrder(..., getHeaderSubcategoryOrder('Rebar'), ...)`
- `navSubTranslationKeys`: 6 Rebar key eklendi (Bending/Cutting/Combined/SteelFactory/Light/HandTools)
- Hardcoded 6 `<li>` → dynamic `{rebarSubcategories.map(...)}` (Aluminium/PVC ile aynı pattern)
- `ordering.json`: `header_subcategory_override: []` boş array eklendi

**Override Feature (`c6419be`):**
- Ken isterse materyal başına header'a bağımsız sıra verebilir — `header_subcategory_override` doldur
- Boş = kategori sayfası ile aynı sıra (single source of truth)
- CMS: "Header Alt Kategori Override" field + hint eklendi

**Test (6/6):**
- Built HTML'de Rebar sırası: `Bending → Cutting → Combined → Steel Factory → Light → Hand Tools` ✅
- ordering.json ile tam eşleşme: `FULL MATCH: True` ✅
- override boş array → fallback çalışıyor ✅
- Kategori sayfası Rebar filter'ları etkilenmedi ✅
- Build: 569 sayfa, 0 hata ✅
- Aluminium + PVC regression yok ✅

**Faz 5 — CMS Live Test (Ken, prod'da):**
- `8d988bd` + `7b4c97e` — Ken ordering.json'u drag-drop ile iki kez güncelledi ✅
- Site Ordering CMS flow sonuna kadar test edildi (prod ortamda, Sveltia)

### Blockers
- None

### Next
1. İlhan içerik sprint devam (GMS + Yılmaz makine verileri)
2. Yılmaz temizlenmiş WebP görselleri machine JSON'larına bağlama planı
3. Step 1.8 planlama

### Commit
`docs(devlog): Step 1.7.1 header mega-menu ordering fix`

---

## 2026-05-30 — Step 1.7: Site Hierarchy Audit + Material-Based Ordering

**Duration:** ~2.5h  
**Branch:** main  
**Commits:** `7085765` → `d1c0bb8` → `104a9b9` → `493535b`

### Done

**Adım 0 — Critical Hierarchy Audit:**
- Header/Navbar kaynak kodu okundu; aktif component'in `Navbar.astro` olduğu tespit edildi (`Header.astro` legacy/unused)
- Routing yapısı haritalandı: `/kategori/aluminyum` + `/kategori/pvc` material-based ✅, `/kategori/gocmaksan` brand-based ❌
- Machine data field audit: `material` field yok; Yılmaz `categories: ["Aluminium"/"PVC"]`, Göçmaksan `categories: ["Bending Machines", ...]` (operation type)
- Brand→Material mapping doğrulandı: Göçmaksan 47 makine tümü Rebar, Yılmaz 57 Aluminium + 51 PVC + 20 her ikisi
- **Verdict:** Hybrid (B-lite) — Navbar zaten `t('cat.rebar')` = "Арматура" label kullanıyor, sadece URL slug hâlâ brand-based
- **Karar (Ken):** Seçenek A onaylandı — inline URL rename, sonra ordering normal akış

**Adım A — Rebar Route Rename (Inline Fix):**
- `KategoriPage.astro`: `gocmaksan` param → `rebar` param (brand mapping kod içinde: `brand: 'gocmaksan'`)
- `Navbar.astro`: 6 URL güncellendi — desktop 5 link + mobile 1 link (`/kategori/gocmaksan` → `/kategori/rebar`)
- `kategori/gocmaksan.astro`: 169 satır sayfa → meta-refresh redirect (`/kategori/rebar`)
- `astro.config.mjs`: `redirects` eklendi — `/bg/`, `/en/`, `/ru/` lang variant'ları 301

**Faz 1 — ordering.json Seed:**
- `src/data/ordering.json` oluşturuldu (385 satır)
- 3 materyal: Aluminium (11 subcat, 57 makine), PVC (12 subcat, 51 makine), Rebar (6 subcat, 47 makine)
- Multi-subcat makineler (Rebar) her subcategory'de ayrı pozisyon
- Başlangıç sırası: Processing Centers önce, Saw Cutting 2., vb. — CMS'ten override edilebilir

**Faz 2 — Sveltia CMS Config:**
- `public/admin/config.yml`: "🔢 Site Sıralaması" file collection eklendi
- 3 iç içe list widget: header_dropdown → subcategories_per_material → machines_per_subcategory
- `allow_add: false` (yapısal, yeni materyal CMS'ten eklenemez)
- Drag-drop default aktif tüm list widget'larda

**Faz 3 — Frontend Sort Logic:**
- `src/utils/ordering.ts` (yeni dosya): `sortByOrder<T>()`, `getMaterialOrder()`, `getSubcategoryOrder()`, `getMachineOrder()`
- Alphabetical fallback: ordering.json'da olmayan slug → liste sonuna
- `Navbar.astro`: Al + PVC subcategory linkleri ordering'e göre sıralı
- `KategoriPage.astro`: filter butonları + card grid compound sort (subcat sırası × makine sırası)
- Rebar mapping: `catToMaterial["Gocmaksan"] = "Rebar"` — data dokunulmadı

**Faz 4 — Build Verification (5/5 test):**
- `/kategori/rebar` build edildi, 47 GMS makine var ✅
- `/kategori/gocmaksan` meta-refresh redirect çalışıyor ✅
- `/en/kategori/gocmaksan` astro config redirect çalışıyor ✅
- Processing Centers filter butonu Saw Cutting'den önce ✅
- 57/57 Aluminium makine sayfada — sıfır regression ✅

### Blockers
- Faz 5 (CMS drag-drop live test): prod deploy sonrası Ken yapacak

### Next
1. Prod deploy → CMS'te "Site Sıralaması" drag-drop test (3 katman)
2. İlhan içerik sprint devam (GMS makine verileri)
3. Step 1.8 planlama (homepage featured machine ordering?)

### Commit
`docs(devlog): Step 1.7 site hierarchy audit + material-based ordering`

---

## 2026-05-29 — Yılmaz Temizlenmiş WebP Görseller + BG Processor Script

**Duration:** ~1h (solo — Ken)  
**Branch:** main  
**Commit:** `b6a0bae`

### Done

- 518 adet yüksek çözünürlüklü, temiz arka planlı Yılmaz makine WebP görsel yüklendi
- Klasör: `public/images/yilmaz/Yilmaz_Temiz_Makineler/` (mevcut `/images/yilmaz/` ana klasörüne dokunulmadı)
- Naming: `{slug}_{index}.webp` formatı (örn: `ack-420-s-up-cutting-saw-machine_1.webp`)
- `scripts/yilmaz_bg_processor.py` eklendi — arka plan temizleme pipeline scripti (214 satır)
- `package.json` + `package-lock.json`: sharp/jimp bağımlılıkları eklendi

### Blockers
- Görseller şu an makine sayfalarına bağlı değil — JSON'daki `images` field'ı hâlâ CDN URL'leri gösteriyor
- Bağlama planı: İlhan sprint'te CMS'ten veya ayrı bir migration script ile

### Next
1. CMS'ten image field'larını `Yilmaz_Temiz_Makineler/` klasörüne yönlendir
2. Migration script ile mevcut CDN URL'leri → lokal WebP path'leri toplu güncelle

### Commit
`docs(devlog): note Yilmaz cleaned WebP images upload (2026-05-29 solo session)`

---

## 2026-05-27 — Sprint F: İlhan CMS Davet

**İlhan (biraderi) Sveltia CMS'e davet edildi, girişi sağlandı.**
- GitHub repo collaborator olarak eklendi
- CMS erişimi aktif: `https://jaguar.ataerk.com/admin/`
- Sonraki adım: 47 GMS makine içerik girişi (Ken + İlhan manuel sprint)

---

## 2026-05-27 — Video Hybrid Feature (Step 1.5)

**Branch:** main
**Commit:** `144ead5` — feat(machine-page): hybrid youtube video thumbnail + modal popup

### Done

**VideoModal.astro** (yeni component, `src/components/VideoModal.astro`):
- YouTube ID regex: watch?v=, youtu.be/, embed/, shorts/, bare ID — tüm formatlar
- Thumbnail: `maxresdefault.jpg` → `hqdefault.jpg` onerror fallback
- Play overlay: beyaz daire + kırmızı üçgen, hover scale + teal border
- Modal: `fixed inset-0 z-50`, dark backdrop, lazy iframe (`data-src` → `src` sadece açılışta)
- ESC + backdrop click + X butonu kapatır; `removeAttribute('src')` = video stop
- Script: `is:inline define:vars={{ modalId }}` ile instance-isolated IIFE

**MachinePage.astro**:
- `import VideoModal` eklendi
- `video = activeLang.video || enLang.video || null` (EN fallback)
- PDF + Video buton bölümü: `flex flex-wrap gap-3`, her ikisi brand color, B4 (her biri ayrı conditional)
- Media bölümü: eski `<iframe>` → `<VideoModal videoUrl={video} machineTitle={isim} />`
- Galeri layout etkilenmedi

**ui.ts**:
- `machine.video_btn` eklendi: EN "Video" / BG "Видео" / RU "Видео"
- RU eksik anahtarlar tamamlandı: `machine.catalog`, `machine.media`, `machine.video`, `machine.gallery`

**public/admin/config.yml**:
- `{ name: video, label: "Video URL", widget: string, required: false }` — yilmaz + gocmaksan EN (pdf_catalog sonrası)

### Test Sonuçları

| Test | Sonuç |
|------|-------|
| Видео butonu (BG) | ✅ |
| "Video" / "Видео" butonu (EN / RU) | ✅ |
| Thumbnail click → modal açılır | ✅ |
| `body.overflow = hidden` (scroll lock) | ✅ |
| ESC → modal kapanır, iframe src temizlenir | ✅ |
| Backdrop click → modal kapanır | ✅ |
| B4: video yok → buton yok, section yok, DOM'da sıfır element | ✅ |
| GMS sls-12 regression | ✅ |
| Build: 568 sayfa, 0 hata | ✅ |

### Açık Kalan

- **Video URL girişi**: Ken/İlhan CMS'ten (`Video URL` field) veya JSON'dan manuel ekleyecek
- **Sveltia `video` field lazy-load notu**: iframe `src` sadece modal açılınca set → YT JS API yüklenmez (performans ✓)
- Video URL formatı: tam URL, youtu.be, embed — hepsi destekleniyor

---

## 2026-05-27 — D7 Faz 2E.1: EN technical_data CMS edit alanı (Sveltia keyvalue)

**Branch:** main
**Commit:** `b3560ef` — feat(cms): add technical_data keyvalue widget to en collections

### Done

**Audit (Faz 2E, Adım 1):**
- 135 makinede `diller.en.technical_data` tarandı: 118 dolu, 17 yok
- 78 unique key bulundu (top: Weight×81, Dimensions×74, Saw Rotation Speed×59 …)
- 3 seçenek değerlendirildi: A (keyvalue native), B (array refactor), C (78 static field)

**Apply (Faz 2E.1, Adım 2):**
- Sveltia-native `widget: keyvalue` keşfedildi — Decap CMS'te yok, Sveltia exclusive
- `public/admin/config.yml`: yilmaz + gocmaksan `diller.en` altına eklendi (images sonrası, specs öncesi)
- **Sıfır data migrasyonu, sıfır Astro kod değişikliği** — JSON format aynı kaldı

**CMS aktivitesi (Ken, paralel):**
- Ken `gms-sls-12` ve `aim-3410` makinelerini CMS'ten güncelledi → GitHub'a yazıldı
- Rebase ile conflict-free merge sağlandı

### Açık Kalan

- **BG/RU technical_data**: Şu an EN-only. Teknik ölçüler dil-bağımsız (kW, mm, kg) → ihtiyaç doğarsa 4 satırla genişletilir
- **GMS CMS specs sorusu**: BG/RU `diller.bg.specs` hâlâ null — Sveltia empty-object davranışı Ken'in manuel testi ile netleşecek
- **Sprint F**: Biraderi CMS davet (GitHub username + email + repo access gerekli)

---

## 2026-05-26 — D7 Sprint: Spec Block UI + Data Normalize + CMS Genişletme

**Branch:** main  
**Commits:** `2b229bb` → `02983d1` → `e79764d` → `adfdf10` → `ce0d6eb` → `57fb567` → `14f7fd7`

### Done

**D7 Faz 2D — Dynamic Spec Column Grid** (`2b229bb`)
- `MachinePage.astro`: `renderableSpecCount` (non-empty array guard) → ternary class chain
- 1 spec → `grid-cols-1`, 2 → `grid-cols-1 md:grid-cols-2`, 3+ → `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`
- Tailwind purge-safe: tüm class literal'leri source'da explicit yazıldı

**D7 Faz 2C — Spec Header i18n** (`02983d1`)
- `src/i18n/ui.ts`: BG+RU 5 spec label eklendi (`spec.general_features` … `spec.optional_accessories`)
- `MachinePage.astro`: `specLabels: Record<string, string>` lookup, `{specLabels[baslik] || baslik}` template

**D7 Faz 2B.1 — Spec Key Normalize** (`e79764d` + `adfdf10`)
- `tools/normalize_spec_keys.py`: Strategy B (snake_case) — KEY_MAP 5×3 (tüm dil/format varyantları)
- 135 dosya tarandı, 134 değiştirildi, 0 anomali — `_audit/NORMALIZE_DRYRUN_REPORT.md` üretildi
- Backup: `_pre_normalize_backup_<ts>/` (yilmaz + gocmaksan), git-ignored
- Post-apply sync: `scripts/sync_machines_to_json.py` çalıştırıldı

**Adım 7 — Fill Missing RU Specs** (`ce0d6eb`)
- `tools/fill_missing_yilmaz_ru_specs.py`: Gemini 2.5 Flash EN→RU spec çevirisi
- İşlenen: `aim-3410` (34 item / 3 grup) + `kp-130-cnc` (20 item / 3 grup)
- Validation: item count eşleşmesi + Cyrillic model code guard (`\b[А-ЯЁ]{2,}\b`)
- **Düzeltme notu:** aim-3410 ve kp-130 BG specs her zaman mevcuttu. Bu adım SADECE eksik olan RU specs'i ekledi.

**specLabels Title Case** (`57fb567`)
- 15 label (BG×5, EN×5, RU×5) → strict Title Case — global tutarlılık

**D7 Faz 2B.2 — Sveltia CMS Config Genişletme** (`14f7fd7`)
- `public/admin/config.yml`: 124 satır eklendi
- Yılmaz collection: EN/BG/RU her birine `specs` object widget (`standard_accessories`, `optional_accessories`, `general_features`)
- Yılmaz BG+RU: `pdf_catalog` string field eklendi
- GMS collection: EN/BG/RU her birine `specs` object widget (`general_features`, `capacities`, `supplied_equipment`)
- GMS BG+RU: `pdf_catalog` string field eklendi
- Tüm label'lar lokalize edildi (BG "Спецификации", RU "Характеристики" vb.)

### Validasyon

**JSON path doğrulama (statik):**
- `pim-6508-se` (yılmaz): EN/BG/RU × 3 spec field — 9/9 ✓, EN `pdf_catalog` mevcut ✓
- `aim-3410`: EN/BG/RU specs — 9/9 ✓ (3 dil specs her zaman mevcuttu)
- `kp-130-cnc`: EN/BG/RU specs — 9/9 ✓
- `gms-sls-12`: EN specs 3/3 ✓; BG/RU null → CMS'de boş ama düzenlenebilir ✓
- TEST_ITEM_X inject/remove: `diller.bg.specs.general_features` path doğrulandı ✓
- YAML lint: `config.yml` valid (node JSON parse ile konfirme edildi)

**CMS UI testi:** `https://jaguar.ataerk.com/admin/` GitHub OAuth gerektiriyor → manuel doğrulama gerekli (Ken'in tarayıcısında açılmalı)

### Bekleyen

- **8 GMS makinesi:** BG/RU description eksik (kapsam dışı bu sprint'te)
- **CMS live UI testi:** aim-3410 / kp-130 3-dil specs görünürlüğü — Ken manuel kontrol
- Cloudflare cache purge (gerekirse)

---

## 2026-05-24 [~2h] — Yılmaz RU name translation sprint (88/88 + BG tooling commit)

**Branch:** main

### Done
- **Spot-check (88 files):** `inject_yilmaz_from_yedek.py --apply` sonucu 88/88 ✅ — RU mevcut, BG intact, CDN image yok, Cyrillic spec anahtarları doğru, aim-4420/aim-7420 EN desc 887 karakter
- **Sync hotfix:** `src/data/yilmaz.json` aggregate stale'di (inject sonrası sync çalıştırılmamıştı) → `scripts/sync_machines_to_json.py` çalıştırıldı, template artık fresh data okuyor
- **Local render QC:** `localhost:4321` — ack-420-s, aim-4420, sm-201-sd, vce-4000 4 makine BG/RU/EN doğrulandı (`744d839` push)
- **`tools/translate_yilmaz_ru.py` yazıldı (~360 satır):**
  - Gemini 2.5-flash REST, temperature=0.2, `response_mime_type: application/json`
  - Description-as-context strateji: `diller.ru.description` prompt'a context olarak verildi
  - Few-shot (3 örnek) + 12 terimli TR→RU glossary
  - `_is_garbage_name()`: HTML/CDN URL içeren name → skip, sonraki dile düş
  - EN name hint: bare model code'larda (`AIM 4420`) Gemini Rusça makine tipi türetebiliyor
  - Latin model kodu guard: prefix'te `[А-ЯЁ]{2,}` regex → FLAG
  - Atomik apply: Phase 1 tüm Gemini call'lar → Phase 2 backup → Phase 3 batch write → Phase 4 sync hook
  - İdempotent retry: `classify_name()` Cyrillic'i skip eder, sadece kalan TR adlar yeniden işlenir
  - `--dry-run` (5 sample) / `--apply` modları
- **Dry-run × 2 iterasyon:** aim-3410 HTML garbage fix + AIM 4420 bare code → EN hint fix
- **`--apply` çalıştırıldı:** 86/88 ilk geçiş → 2 API timeout (mkn-serisi, sm-206) → retry → **88/88 ✅**
- **0 model kodu flag:** ACK/AIM/DC/KD/VCE vs. tümü Latin kaldı
- **`TRANSLATE_YILMAZ_RU_NAME_REPORT_2026-05-23.md` oluşturuldu** (88 satır TR→RU tablo)
- **Commit + push:** `6e48827` (91 file, 1102 ins)
- **BG tooling commit:** `tools/translate_yilmaz_bg.py`, `tools/recover_yilmaz_bg.py`, `tools/retranslate_bgru.py` + 4 audit/recovery report → `8883ba5`
- **`.gitignore` temizlik:** `_backup/`, `pdf_extraction/`, `*_enrichment_log.json`, `src/data/*_backup_*.json` eklendi

### Blockers
- None

### Next
1. 13 partial machine — `diller.bg.description = ""` (EN source < 100 chars, Yılmaz scraper gerekli)
2. Frontend conditional render — BG description boşsa EN'e fallback
3. Ghost data cleanup — vce-3500, vce-4000 diller.ru CDN URL temizliği
4. `tercume_merkezi.py` path fix — hâlâ `machines.json` target ediyor (renamed → `yilmaz.json`)
5. Göçmaksan schema migration — top-level specs → `diller.en.specs`

### Commit
`chore: devlog 2026-05-24 RU name translation sprint (88/88)`

---

## 2026-05-23 [~13:00] — i18n hotfix: field-level EN fallback (specs + teknikTablo + katalog)

**Sorun:** Önceki fix (697dce9) sadece `name/description/images` için EN fallback ekledi. `MachinePage.astro`'da 3 field kör nokta kaldı: `ozellikGruplari` (specs), `teknikTablo` (technical_data), `katalog` (pdf_catalog).

**Semptomlar:**
- Yılmaz BG/RU: teknik veri kartları + spec grupları tamamen kayboluyor (tablolar "uçtu")
- Göçmaksan BG/RU: katalog PDF butonu görünmüyor (sessiz regresyon)

**FAZ 1 — Data audit (inspect only):**
- Yılmaz: 86/88 makine `diller.en` only — BG/RU key yok. 2 exception (vce-3500, vce-4000): ghost skeleton var (name="", images=[], specs={STANDARD:[]}), değerler boş.
- Göçmaksan: 39/47 `diller.bg.description` + `diller.ru.description` — name/specs/technical_data BG/RU çevirisi YOK. Top-level `specs` her zaman EN.
- Render audit → 3 kırık satır: L45 `specs`, L46 `technical_data`, L48 `katalog`.

**FAZ 2 — Fix (`MachinePage.astro:45-48`, 3 satır):**
```js
// L45
const ozellikGruplari = activeLang.specs || enLang.specs || (machine as any).specs || ...
// L46
const teknikTablo     = activeLang.technical_data || enLang.technical_data || {};
// L48
const katalog         = activeLang.pdf_catalog || enLang.pdf_catalog || (machine as any).pdf_catalog || null;
```

**FAZ 3 — Verify (localhost:4321, 5 test case):**
- BG/RU Yılmaz (ack-420-s): teknik veri kartları (Power/RPM/Weight) ✅, STANDARD/OPTIONAL/GENERAL specs ✅, katalog butonu ✅
- BG/RU Göçmaksan (gms-axis-50s): description BG/RU ✅, CAPACITIES/FEATURED FEATURES ✅, katalog butonu ✅
- EN regresyon: yok ✅

**Commit:** `3886fe2`

**Bekleyen (ayrı sprint):**
- Yılmaz 88 makine BG+RU çevirisi — description, specs, technical_data hiç yok
- Göçmaksan 47 makine BG+RU — name, specs, teknikTablo çevirisi yok
- Ghost data cleanup: vce-3500, vce-4000 boş BG/RU skeleton

---

## 2026-05-23 [~10:45] — i18n render bug fix (MachinePage + KategoriPage + gocmaksan + hero)

**Sorun:** `MachinePage.astro:29` `activeLang` hardcoded `en` — tüm BG/RU machine detail sayfaları EN içerik render ediyordu. Aynı pattern `KategoriPage` ve `gocmaksan.astro`'da da mevcuttu.

**Root cause:** `activeLang = diller?.en || diller?.tr` — `lang` URL'den çekiliyordu ama hiç kullanılmıyordu.

**Fix pattern (4 dosya):**
```js
const activeLang = machine.diller?.[lang] || {};
const enLang     = machine.diller?.en     || {};
const isim       = activeLang.name || enLang.name || machine.slug;
const aciklama   = activeLang.description || enLang.description || '';
```
Field-level EN fallback: `bg.description` dolu ama `bg.name` null olan Gocmaksan makineleri için isim EN'den, açıklama BG'den gelir.

**isim data check:** Yılmaz `bg.isim`/`ru.isim` tamamı null — legacy field, kullanılmıyor. `en.name` canonical.

**Verify (3×2 matris):**
- BG gocmaksan: h1=Axis 50S (EN fallback) ✅, h2=Общ преглед (BG) ✅
- RU gocmaksan: h1=Axis 50S ✅, h2=Обзор (RU) ✅
- EN regress: Overview ✅
- BG/RU/EN Yılmaz: doğru EN isim ✅
- BG hero: "ACK 550 - UP-CUTTING SAW MACHINE" (artık Türkçe değil) ✅

**Commit:** `697dce9`

---

## 2026-05-23 [~10:00] — Navbar logo cleanup + Hero carousel görsel büyütme

**Yapılan:**
- `Navbar.astro`: Yılmaz + Göçmaksan logoları header'dan kaldırıldı, sadece Jaguar kaldı (alt section'larda zaten var) — `refactor(navbar)`
- `HomePage.astro`: Hero carousel container yüksekliği `h-[300/450px]` → `h-[320/520px]`, slide padding `p-8 md:p-16` → `p-3 md:p-5` — makine görselleri ~%60 büyüdü, `object-contain` korundu, kırpma yok — `feat(hero)`
- `.claude/launch.json` oluşturuldu (Astro dev server preview konfigürasyonu)

**FAZ 3 verify:** EN/BG/RU 3 dilde local preview — ✅ tüm dillerde hero büyük, navbar temiz

**Commits:** `4541058` (navbar), `f104acf` (hero)

---

## 2026-05-23 [07:30] — Gocmaksan BG+RU retranslation + aggregate sync

**Yapılan:** `tools/retranslate_bgru.py` ile 47 Göçmaksan makinesinin BG ve RU açıklamaları zengin EN prose'dan yeniden çevrildi.

**Sonuç:**
- ok: 37 (ilk geçiş) + 2 retry (gms-bs-50, gms-bt-24x5 — BG timeout) = **39 toplam**
- stub_skip: 8 (Hand Tools 6 + Light Construction 2 — PDF yok, beklenen)
- Backup: `_backup/pre_retranslate_20260523_071236/`

**FAZ 3 spot check (individual files):** 3/3 OK — EN≥500, BG≥800, RU≥800, `## Overview` header ✓

**CMS sync:** `scripts/sync_machines_to_json.py` lokal çalıştırıldı, `src/data/gocmaksan.json` aggregate regenerate edildi (39 individual files canonical, aggregate derived — GitHub Action `.github/workflows/cms-sync.yml` aynı işi push'ta yapardı; lokalde mirror için yapıldı). 40 files changed, 468 insertions.

**FAZ 3.5 spot check (aggregate):** 3/3 OK — BG+RU zengin, header ✓

**Architecture note:** `_meta/data-architecture.md` wiki nodu Ken ekleyecek.

**Bekleyen:**
- `git add src/data/machines/gocmaksan/ src/data/gocmaksan.json` + commit + push
- Cloudflare cache purge
- `@tailwindcss/typography` plugin (AboutPage dead prose CSS)
- GitHub Actions write permission fix (Settings → Actions → General → Read+Write)
- `.gitignore` cleanup: `_backup/`, `_enrichment_log.json`, `_retranslate_log.json`, `pdf_extraction/`, eski backup JSON'ları

---

## 2026-05-22 [15:00] — Filter pill case + RU light construction duzeltme (stage)

- gocmaksan.astro filter butonlarindan `uppercase` kaldirildi — artik "Огъване" degil "Огъване" (title case)
- ui.ts RU `cat.sub.light`: 'Лека техника' (Bulgarca!) -> 'Лёгкая техника' duzeltildi
- Build 568 sayfa OK. BG dist: Огъване/Рязане... RU dist: Гибка/Комбинированные/Лёгкая техника dogrulandi.

---

## 2026-05-22 [14:45] — Kategori filter pills i18n fix (stage)

- `gocmaksan.astro` filter pill label'lari hard-coded EN'den `t('cat.sub.*')` cagrilarina gecirildi
- BG default URL `/kategori/gocmaksan` artik Bulgarca pill gosteriyor (Огъване, Рязане, Комбинирани...)
- `data-filter` attribute canonical EN key'leri korundu (JS filter logic bozulmadi)
- Yilmaz etkilenmedi — aluminyum/pvc KategoriPage.astro'dan geciyor (zaten t() kullaniyor)
- Build 568 sayfa OK. Smoke: 6 BG label dogrulandi dist HTML'de.

---

## 2026-05-22 [14:30] — Navbar polish (stage)

- Machines dropdown button'a `pb-1` eklendi — chevron diğer nav link'lerle hizalandı
- Jaguar logo: `brightness-0 invert` eklendi (PNG → saf beyaz, Tailwind filter; Yilmaz logo ile aynı pattern)
- Etkilenen: `src/components/Navbar.astro` (2 satır), sadece navbar context — Footer dokunulmadı
- Build: 568 sayfa OK. Gorsel doğrulama Ken yapacak (`npm run dev` → localhost:4321)

---

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

