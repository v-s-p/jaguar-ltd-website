# Yedek → Individual JSON Mapping Audit

**Tarih:** 2026-05-24
**Kaynak:** `yilmaz_yedek.json` (90 makine, 9 dil, eski TR şema)
**Hedef:** `src/data/machines/yilmaz/*.json` (88 makine, yeni EN şema)
**Prototype makine:** `aim-7510-aluminyum-profil-isleme-merkezi` ↔ `aim-7510-aluminium-profile-processing-centers`

---

## Adım 1 — AIM 7510 Yedek İçeriği (EN + RU)

### `diller.en`

- **isim:** `AIM 7510 ALUMINYUM PROFIL ISLEME MERKEZI`  (40 chr)
- **aciklama:** 952 chr
- **resimler:** 7 item
  - Örnek 1: `https://di33l1fv68t4r.cloudfront.net/wp-content/uploads/2021/04/17145121/aim-7510_6.png`
  - Örnek 2: `https://di33l1fv68t4r.cloudfront.net/wp-content/uploads/2025/07/25120848/TCAT01000000651-3.jpg`
  - Örnek 3: `https://di33l1fv68t4r.cloudfront.net/wp-content/uploads/2025/07/25120849/TCAT01000000641-3.jpg`
- **katalog:** `https://di33l1fv68t4r.cloudfront.net/wp-content/uploads/2021/04/23154751/AIM-7510.pdf`  (85 chr)
- **ozellik_gruplari:** 3 grup
  - `STANDART ACCESORIES` → list, 5 item, ilk: `CAMPROX software program for CNC programming`
  - `OPTIONAL ACCESSORIES` → list, 13 item, ilk: `Cutter tools, tool holders and collets set 6 pc cutters (2 pc. Ø5, 1 pc. Ø6, 1 pc. Ø8, 1 pc. Ø10, 1 pc. Ø12) – 12 pc. HSK F63 Tool holders – 6 pc. Collets ( 3 pc. Ø5-6, 1 pc. Ø7-8, 1 pc. Ø9-10, 1 pc. Ø11-12) – 12 pc. mold height`
  - `GENERAL FEATURES` → list, 18 item, ilk: `CNC automation system providing motion control at 5-axis`
- **piktogramlar:** 8 item
  - Yapı: key:value dict
  - `elektrik`: `15 kW / 400V AC 3P+PE / 50/60 Hz.`
  - `matkap_donus_hizi`: `3.000 RPM`
  - `donus_hizi`: `20.000 RPM`
  - `cap`: `D: Ø350 mm d: Ø30 mm`
  - `debi`: `250 L/min`
  - `basinc`: `6-8 bar`
  - `boyutlar`: `201x972x220`
  - `urun_agirligi`: `4.795 Kg / 4.490 Kg`

### `diller.ru`

- **isim:** `AIM 7510 ALUMINYUM PROFIL ISLEME MERKEZI`  (40 chr)
- **aciklama:** 1039 chr
- **resimler:** 7 item
  - Örnek 1: `https://di33l1fv68t4r.cloudfront.net/wp-content/uploads/2021/04/17145121/aim-7510_6.png`
  - Örnek 2: `https://di33l1fv68t4r.cloudfront.net/wp-content/uploads/2025/07/25120848/TCAT01000000651-3.jpg`
  - Örnek 3: `https://di33l1fv68t4r.cloudfront.net/wp-content/uploads/2025/07/25120849/TCAT01000000641-3.jpg`
- **katalog:** `https://di33l1fv68t4r.cloudfront.net/wp-content/uploads/2021/04/23154751/AIM-7510.pdf`  (85 chr)
- **ozellik_gruplari:** 3 grup
  - `СТАНДАРТНЫЕ АКСЕССУАРЫ` → list, 5 item, ilk: `Программное обеспечение CAMPROX для программирования ЧПУ`
  - `ДОПОЛНИТЕЛЬНЫЕ АКСЕССУАРЫ` → list, 13 item, ilk: `Набор фрез, держателей и цанг 6 шт. фрез (2 шт. Ø5, 1 шт. Ø6, 1 шт. Ø8, 1 шт. Ø10, 1 шт. Ø12) — 12 шт. HSK F63 Держатели инструментов — 6 шт. Цанги (3 шт. Ø5-6, 1 шт. Ø7-8, 1 шт. Ø9-10, 1 шт. Ø11-12) — 12 шт. высота пресс-формы`
  - `GENERAL FEATURES` → list, 18 item, ilk: `Система автоматизации ЧПУ, обеспечивающая управление движением по 5 осям`
- **piktogramlar:** 8 item
  - Yapı: key:value dict
  - `elektrik`: `15 kW / 400V AC 3P+PE / 50/60 Hz.`
  - `matkap_donus_hizi`: `3.000 RPM`
  - `donus_hizi`: `20.000 RPM`
  - `cap`: `D: Ø350 mm d: Ø30 mm`
  - `debi`: `250 L/min`
  - `basinc`: `6-8 bar`
  - `boyutlar`: `201x972x220`
  - `urun_agirligi`: `4.795 Kg / 4.490 Kg`

---

## Adım 2 — Mevcut Individual JSON ile Karşılaştırma (EN)

| Alan (yedek) | Yedek değer | Alan (current) | Current değer |
|---|---|---|---|
| isim (40 chr) | `AIM 7510 ALUMINYUM PROFIL ISLEME MERKEZI` | name (47 chr) | `AIM 7510 - Aluminium Profile Processing Centers` |
| aciklama (952 chr) | (gövde) | description (952 chr) | (gövde) |
| resimler [7 item] | `https://di33l1fv68t4r.cloudfront.net/wp-content/uploads/2021` | images [7 item] | `/images/yilmaz/aim-7510-aluminium-profile-processing-centers` |
| katalog (85 chr) | `https://di33l1fv68t4r.cloudfront.net/wp-content/uploads/2021/04/23154751/AIM-7510.pdf` | pdf_catalog | `/catalogs/yilmaz/ALUMINIUM-KATALOG.pdf` |
| ozellik_gruplari [3 grup] | (bkz. Adım 3) | specs [3 key] | (bkz. Adım 3) |
| piktogramlar [8 item] | (bkz. Adım 3) | technical_data [8 key] | (bkz. Adım 3) |

---

## Adım 3 — Mapping Kararları

### 3a. isim → name
- Yedek EN isim: `AIM 7510 ALUMINYUM PROFIL ISLEME MERKEZI`
- Current name:  `AIM 7510 - Aluminium Profile Processing Centers`
- **Karar:** ⚠️ FARKLI — kontrol gerek

### 3b. aciklama → description
- Yedek EN aciklama: 952 chr
- Current description: 952 chr
- İlk 100 char (yedek): `AIM 7510 is 5-axis servo-controlled machining centers which are is designed to perform drilling, gro`
- İlk 100 char (current): `AIM 7510 is 5-axis servo-controlled machining centers which are is designed to perform drilling, gro`
- Benzerlik: `96.64%`
- **Karar:** DIRECT — neredeyse aynı, minor fark

### 3c. ozellik_gruplari → specs (KRITIK)

**Yedek EN grup adları ve item sayıları:**

| Grup adı (yedek) | Item sayısı | Proposed current key |
|---|---|---|
| `STANDART ACCESORIES` | 5 | `??? (yeni key: 'STANDART ACCESORIES')` |
| `OPTIONAL ACCESSORIES` | 13 | `OPTIONAL ACCESSORIES` |
| `GENERAL FEATURES` | 18 | `GENERAL FEATURES` |

**Current specs keys:**
- `STANDARD ACCESSORIES`: 5 item
- `OPTIONAL ACCESSORIES`: 13 item
- `GENERAL FEATURES`: 18 item

- Yedek grup adları: `['STANDART ACCESORIES', 'OPTIONAL ACCESSORIES', 'GENERAL FEATURES']`
- Current specs adları: `['STANDARD ACCESSORIES', 'OPTIONAL ACCESSORIES', 'GENERAL FEATURES']`
- **Karar: ⚠️ RENAME GEREK — yedek adları current ile uyuşmuyor**

### 3d. piktogramlar → ??? (KRITIK)

**Yedek piktogramlar yapısı:**

- Yapı: **key:value dict** (8 anahtar)

| Piktogram key | Değer |
|---|---|
| `elektrik` | `15 kW / 400V AC 3P+PE / 50/60 Hz.` |
| `matkap_donus_hizi` | `3.000 RPM` |
| `donus_hizi` | `20.000 RPM` |
| `cap` | `D: Ø350 mm d: Ø30 mm` |
| `debi` | `250 L/min` |
| `basinc` | `6-8 bar` |
| `boyutlar` | `201x972x220` |
| `urun_agirligi` | `4.795 Kg / 4.490 Kg` |

**Current technical_data:**

| technical_data key | Değer |
|---|---|
| `Power` | `15 kW / 400V AC 3P+PE / 50/60 Hz.` |
| `Drill Rotation Speed` | `3.000 RPM` |
| `Saw Rotation Speed` | `20.000 RPM` |
| `Saw Diameter` | `D: Ø350 mm / d: Ø30 mm` |
| `Flow Rate` | `250 L/min` |
| `Pressure` | `6-8 bar` |
| `Dimensions (cm)` | `201x972x220` |
| `Weight` | `4.795 Kg / 4.490 Kg` |

- Ortak key'ler (case-insensitive): **0/8**
  - Piktogramda var, technical_data'da yok: ['basinc', 'boyutlar', 'cap', 'debi', 'donus_hizi', 'elektrik', 'matkap_donus_hizi', 'urun_agirligi']
  - Technical_data'da var, piktogramda yok: ['dimensions (cm)', 'drill rotation speed', 'flow rate', 'power', 'pressure', 'saw diameter', 'saw rotation speed', 'weight']

**Karar:** piktogramlar = `technical_data` ile aynı kavram. Rename + direct inject ✅

### 3e. resimler → images

**Yedek resimler (ilk 3):**
- `https://di33l1fv68t4r.cloudfront.net/wp-content/uploads/2021/04/17145121/aim-7510_6.png` ← CDN/external ⚠️
- `https://di33l1fv68t4r.cloudfront.net/wp-content/uploads/2025/07/25120848/TCAT01000000651-3.jpg` ← CDN/external ⚠️
- `https://di33l1fv68t4r.cloudfront.net/wp-content/uploads/2025/07/25120849/TCAT01000000641-3.jpg` ← CDN/external ⚠️

**Current images (ilk 3):**
- `/images/yilmaz/aim-7510-aluminium-profile-processing-centers_1.png` ← local ✅
- `/images/yilmaz/aim-7510-aluminium-profile-processing-centers_2.jpg` ← local ✅
- `/images/yilmaz/aim-7510-aluminium-profile-processing-centers_3.jpg` ← local ✅

**Karar:** Yedek CDN URL, current local path. **Mevcut local path'ler KORU** — yedek resimleri inject etme.

### 3f. katalog → pdf_catalog
- Yedek katalog: `https://di33l1fv68t4r.cloudfront.net/wp-content/uploads/2021/04/23154751/AIM-7510.pdf`
- Current pdf_catalog: `/catalogs/yilmaz/ALUMINIUM-KATALOG.pdf`
- **Karar: ⚠️ Yedek CDN URL, current local. Current'ı koru.**

---

## Adım 4 — RU specs (ozellik_gruplari) Grup Adları

**Yedek RU ozellik_gruplari grup adları (3 grup):**

| # | RU Grup Adı | Item sayısı |
|---|---|---|
| 1 | `СТАНДАРТНЫЕ АКСЕССУАРЫ` | 5 |
| 2 | `ДОПОЛНИТЕЛЬНЫЕ АКСЕССУАРЫ` | 13 |
| 3 | `GENERAL FEATURES` | 18 |

- EN grup adları: `['STANDART ACCESORIES', 'OPTIONAL ACCESSORIES', 'GENERAL FEATURES']`
- RU grup adları: `['СТАНДАРТНЫЕ АКСЕССУАРЫ', 'ДОПОЛНИТЕЛЬНЫЕ АКСЕССУАРЫ', 'GENERAL FEATURES']`

**Durum: FARKLI — RU kendi Kiril key adlarına sahip**

**Seçenekler:**
1. RU key adlarını aynen kullan
2. EN key adlarıyla normalize et (BG'deki gibi Cyrillic yerine EN key)

---

## Adım 5 — Slug Matching (90 yedek ↔ 88 current)

Model kodu eşleştirme (slug'ın ilk 2 parçası, ör: `aim-7510`):

| Kategori | Sayı |
|---|---|
| Eşleşen (her iki tarafta) | **78** |
| Yedekte var, current'ta yok | **2** |
| Current'ta var, yedekte yok | **0** |

### Eşleşen — İlk 10 Örnek

| Model kodu | Yedek slug | Current slug |
|---|---|---|
| `ack-420` | `ack-420-s-alttan-cikma-kesme-makinesi` | `ack-420-s-up-cutting-saw-machine` |
| `ack-550` | `ack-550-alttan-cikma-kesme-makinesi` | `ack-550-up-cutting-saw-machine` |
| `ack-700` | `ack-700-alttan-cikma-kesme-makinesi` | `ack-700-up-cutting-saw-machine` |
| `aim-3410` | `aim-3410-aluminyum-profil-isleme-merkezi` | `aim-3410-aluminium-profile-machining-center` |
| `aim-4420` | `aim-4420` | `aim-4420` |
| `aim-7420` | `aim-7420` | `aim-7420` |
| `aim-7510` | `aim-7510-aluminyum-profil-isleme-merkezi` | `aim-7510-aluminium-profile-processing-centers` |
| `ca-601` | `ca-601-yari-otomatik-pvc-tek-kose-temizleme-makinesi` | `ca-601-semi-automatic-pvc-single-corner-cleaning-machine` |
| `ca-603` | `ca-603-pvc-kose-temizleme-makinesi-4-6-bicakli` | `ca-603-pvc-corner-cleaning-machine-4-6-cutters` |
| `ccl-1661` | `ccl-1661-pvc-kaynak-ve-kose-temizleme-makinesi` | `ccl-1661-pvc-corner-cleaning-machine` |

### Yedekte var, Current'ta yok

- `alm-6510` → `alm-6510-aluminyum-profil-isleme-ve-kesme-merkezi`
- `mem-128` → `mem-128-yari-otomatik-coklu-orta-kayit-alistirma-makinesi`

### Current'ta var, Yedekte yok (yeni makineler)

*(yok)*

---

## Önerilen Eski → Yeni Mapping Tablosu

| Yedek alan | Tip | → | Current alan | Transform |
|---|---|---|---|---|
| `isim` | string | → | `diller.{lang}.name` | DIRECT |
| `aciklama` | string | → | `diller.{lang}.description` | DIRECT |
| `ozellik_gruplari[grp].items` | list | → | `diller.{lang}.specs[grp]` | Grup adı kontrolü (bkz. 3c) |
| `piktogramlar` | dict{k:v} | → | `diller.{lang}.technical_data` | DIRECT (key adları eşleşiyor) |
| `resimler` | list[URL] | → | **KULLANMA** | Current local path'ler daha iyi |
| `katalog` | string(URL) | → | **KULLANMA** | Current pdf_catalog zaten doğru |

---

## Inject Script Risk Listesi

| # | Risk | Etki | Öneri |
|---|---|---|---|
| R1 | `resimler` CDN URL | Mevcut local path'ler ezilir, resimler kırılır | **images inject etme** — sadece name/description/specs/technical_data |
| R2 | `katalog` CDN URL | `pdf_catalog` bozulur | **katalog inject etme** — current değer koru |
| R3 | `ozellik_gruplari` grup adları | EN grup adı `STANDARD ACCESSORIES` current specs key ile eşleşiyor mu? | Adım 3c sonucuna göre karar |
| R4 | RU specs key dili | BG'de Kiril key, RU'da EN key tutarsızlığı | Karar: seçenek 1/2/3 (Adım 4) |
| R5 | 13 eşleşmeyen current makine | Yedekte karşılığı yok → RU inject edilemez | Bu makineler için ayrı Gemini RU çevirisi |
| R6 | `aciklama` minor fark | Yedek EN ≠ current EN (whitespace/unicode) | Hangi kaynak doğru? Genellikle current tercih |
| R7 | `diller.en` mevcut alanlar | İnject sırasında specs/images/technical_data override edilmemelidir | Sadece `ru` (ve boş `bg.description`) için inject; `en` dokunulmamalı |

---
*Generated by `tools/_tmp_audit.py` — 2026-05-24*
