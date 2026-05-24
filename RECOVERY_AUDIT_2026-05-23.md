# Yılmaz BG+RU Recovery DRY-RUN Raporu — 2026-05-23

**Kaynak commit:** `d6b5cc8` (14 Mayıs 2026 — tercume_merkezi.py'nin son başarılı çalışması)
**Hedef:** `src/data/machines/yilmaz/*.json` individual dosyalar
**Kapsam:** Read-only. Uygulama yapılmadı. Tüm bulgular hafızadan.

---

## ⚠️ Önceki Audit Düzeltmesi

**AUDIT_2026-05-23_schema-cms-compat.md'deki "43 BG + 42 RU" iddiası YANLIŞ.**

| İddia | Gerçek |
|---|---|
| 43 BG çevirisi | ✅ DOĞRU — 43 BG dolu |
| 42 RU çevirisi | ❌ YANLIŞ — **0 kullanılabilir RU** |

d6b5cc8'de 44 makine `diller.ru` key'ine sahip ama içerikleri tamamen boş, üstelik **eski Türkçe field şemasıyla** yazılmış: `isim`, `aciklama`, `katalog`, `ozellik_gruplari`, `piktogramlar`, `resimler` — tümü `""` veya `null`. RU'dan kurtarılacak gerçek içerik yok.

---

## 1. CMS Config Doğrulaması

**Dosya:** `public/admin/config.yml` — Netlify/Decap CMS

### 1a. BG + RU Sekmeleri

Her iki collection'da (`yilmaz`, `gocmaksan`) `diller.bg` ve `diller.ru` tanımlanmış:

```yaml
- name: bg
  label: "Български"
  widget: object
  fields:
    - { name: name, label: "Наименование", widget: string }
    - { name: description, label: "Описание", widget: text }

- name: ru
  label: "Русский"
  widget: object
  fields:
    - { name: name, label: "Название", widget: string }
    - { name: description, label: "Описание", widget: text }
```

### 1b. CMS'de Tanımlı BG/RU Field'ları

| Field | CMS'de var mı | MachinePage fallback var mı |
|---|---|---|
| `diller.bg.name` | ✅ | ✅ (`enLang.name`) |
| `diller.bg.description` | ✅ | ✅ (`enLang.description`) |
| `diller.bg.images` | ❌ TANIMLANMAMIŞ | ✅ (`enLang.images`) |
| `diller.bg.specs` | ❌ TANIMLANMAMIŞ | ✅ (`enLang.specs`) |
| `diller.bg.technical_data` | ❌ TANIMLANMAMIŞ | ✅ (`enLang.technical_data`) |
| `diller.bg.pdf_catalog` | ❌ TANIMLANMAMIŞ | ✅ (`enLang.pdf_catalog`) |

### 1c. CMS Config Durumu

**Kasıtlı tasarım gibi görünüyor:** CMS sadece BG/RU için name + description düzenlemesine izin veriyor. Images, specs, technical_data, pdf_catalog EN'den fallback alıyor. Recovery için sadece `name` + `description` + `specs` (BG key'leriyle) inject edilecek — CMS bunu destekliyor, doğrudan JSON dosyası yazılacak, CMS üzerinden gitme zorunluluğu yok.

**EN collection eksiklikleri (CMS'de):** `specs` ve `technical_data` field'ları Yılmaz collection'ında tanımlı değil. Sadece `name`, `description`, `pdf_catalog`, `images` var. Bu fields CMS üzerinden düzenlenemiyor şu an — ama bu recovery scope'unun dışında.

---

## 2. d6b5cc8 Veri Çıkarma — Doğrulama

**Commit:** `d6b5cc8` — `src/data/machines.json` (aggregate, 74 makine)

### 2a. Genel İstatistikler

| Metrik | Değer |
|---|---|
| Toplam makine | 74 |
| `diller.bg` key'i olan | 74/74 (100%) |
| BG description DOLU | **43/74** |
| BG description BOŞ (key var, içerik yok) | 31/74 |
| `diller.ru` key'i olan | 44/74 |
| RU description DOLU | **0/44** |
| RU content kullanılabilir | **0** |

### 2b. 43 BG Dolu Makine Listesi

```
ack-420-s-up-cutting-saw-machine
aim-4420
aim-7420
alm-6510-aluminyum-profil-isleme-ve-kesme-merkezi   ← DİKKAT: current'ta dosya YOK
ca-603-pvc-corner-cleaning-machine-4-6-cutters
ccl-1661-pvc-corner-cleaning-machine
cnc-609
cnc-611
crm-201-s-template-copy-router-machine-with-triple-hole-water-slot-drilling
crm-250-s-template-copy-router-machine
dc-421-psd-double-head-mitre-saw-machine-full-automatic
dc-550-pb-double-head-mitre-saw-machines
dc-550-skh-double-head-mitre-saw-machine-full-automatic
dkn-300-450-600-302-452-602-roller-conveyor-with-manual-stop-display-unit
fr-223-fr-223s-portable-template-copy-router
fr-226-s-automatic-copy-router-machine
gas-301
kd-350-d-miter-saw-machine
kd-350-m-miter-saw-machine
kd-400-d-miter-saw-machine
kd-400-m-mitre-saw-machine
km-215-s-semi-automatic-end-milling-machine
mca-801
mk-420-mk-420ps-mk-450-manual-up-cutting-saw-machine
mkn-serisi-150-300-301
nsm-352-nsm-353-kanat-isleme-merkezi
pim-6508-se
pwb-4100
pye-101-pye-102-pye-103-pye-104-manual-punch-press
rs-1000
ryk-420-w-radial-saw-machine
scm-420-l4-scm-420-l7-servo-controlled-serial-cutting-machine
sdt-275
sk-500-d-automatic-sawing-and-drilling-machine
skn-300-450-600-digital-roller-conveyor-with-automatic-length-stop
sm-201-sd
st-264-pvc-automatic-water-slot-machine
tk-503-pvc-tek-kose-kaynak-makinesi
vce-1570
vce-3500
vce-4000
vk-420-v-cutting-90-end-notching-machine
wgm-202
```

### 2c. 31 BG Boş Makine Listesi (key var, içerik yok — zaten çevrilmesi gerekiyor)

```
ack-700-up-cutting-saw-machine
aim-3410-aluminium-profile-machining-center
ca-601-semi-automatic-pvc-single-corner-cleaning-machine
cdc-600-compound-angle-double-head-saw-cutting-machine
dk-502-double-corner-pvc-welding-machine
dk-540-four-corner-pvc-welding-machine
fr-222-portable-template-copy-router
gpt-1000-glass-window-trolley
gt-1000-gasket-trolley
hp-1000-horizontal-profile-troley
kd-305-portable-miter-saw-machine
km-211-manual-end-milling-machine
km-212-portable-end-milling-machine
kp-110-pneumatic-aluminum-corner-crimping-machine
kp-130-cnc-cnc-automatic-corner-crimping-machine
kp-180-hydraulic-aluminium-corner-crimping-machine
ky-305-portable-miter-saw-machine
pc-4000-profile-carry-cart
pt-1000-product-transportation-troley
pt-2000-product-transportation-trolley-two-sided
rt-1000-rotating-table
ryk-420-radial-saw-machine
sdt-280-semi-automatic-multi-reinforcement-and-profile-cutting-machine
sk-500-automatic-sawing-machine
sm-201-single-head-reinforcement-stell-screwdriver
sm-206-fully-automatic-double-head-reinforcement-steel-screwdriver
tk-505-single-corner-pvc-welding-machine
vp-1000-vertica-profile-troley
vp-2000-vertica-profile-troley
was-1000-window-assembly-station
wb-4000-work-bench
```

---

## 3. Slug Match (DRY-RUN)

| Metrik | Değer |
|---|---|
| d6b5cc8 toplam slug | 74 |
| Current individual dosya | 88 |
| Eşleşen | **73** |
| Sadece d6b5cc8'de (current'ta yok) | **1** |
| Sadece current'ta (d6b5cc8'de yok — yeni eklenen) | **15** |

### 3a. Kritik: 1 Slug Sadece d6b5cc8'de Var

| Slug | Durum | BG İçeriği |
|---|---|---|
| `alm-6510-aluminyum-profil-isleme-ve-kesme-merkezi` | Individual dosya yok, aggregate'e de eklenmedi | ✅ Dolu BG var: name "ALM 6510 ОБРАБОТВАЩ И ОТРЕЗЕН ЦЕНТЪР ЗА АЛУМИНИЕВИ ПРОФИЛИ", description mevcut, specs mevcut |

**Etki:** Bu makineye ait BG çeviri kurtarılamaz — hedef dosya yok. Makine ya silinmiş ya da başka bir slug'la yeniden eklendi (aim-4420, aim-7420 bunun yeniden yazılmış hali olabilir).

### 3b. 15 Yeni Makine (BG Kurtarma Kapsamı Dışı — Taze Çeviri Gerekiyor)

```
ack-550-up-cutting-saw-machine
aim-7510-aluminium-profile-processing-centers
ck-412-pvc-glazing-bead-saw
cpm-4150-s
cpm-6161-double-station-composite-panel-processing-machine
dc-421-pbs-double-head-mitre-saw-machine-full-automatic
fr-221-s-pneumatic-template-copy-router
hdl-400-hdl-700-servo-controlled-automatic-length-stops
kd-350-p-miter-saw-machine
kd-400-p-miter-saw-machine
kd-402-s-double-mitre-saw-machine
ncr-300-4-axis-nc-controlled-router-machine
pim-6509-pvc-profile-processing-center
snm-560-m-aluminium-facade-notching-machine-manual
snm-560-srv-servo-controlled-aluminium-facade-notching-machine
```

---

## 4. Schema Doğrulaması (DRY-RUN)

### 4a. d6b5cc8 BG Obje Yapısı

```json
"bg": {
  "name": "KD 350 D ОТРЕЗНА МАШИНА С ЪГЛОВА НАСТРОЙКА",
  "description": "KD 350D ...",
  "specs": {
    "СТАНДАРТНИ АКСЕСОАРИ": [...],
    "ОПЦИОНАЛНИ АКСЕСОАРИ": [...],
    "ОБЩИ ХАРАКТЕРИСТИКИ": [...],
    "ТЕХНИЧЕСКИ ДАННИ": {}
  }
}
```

### 4b. Hedef Yılmaz Individual Dosya BG Yapısı (Beklenen)

```json
"bg": {
  "name": "...",
  "description": "..."
}
```

> CMS config sadece `name` + `description` bekliyor. MachinePage.astro specs için EN fallback kullanıyor. Ama `diller.bg.specs` field'ını inject etmek teknik olarak mümkün — sadece CMS UI'da görünmez, JSON'da kalır. **Karar gerekiyor:** BG specs inject edilecek mi?

### 4c. Field-by-Field Doğrulama

| Field | d6b5cc8'de var mı | İçerik kalitesi | Hedef field | Dönüşüm gerekiyor mu |
|---|---|---|---|---|
| `bg.name` | ✅ 43/43 | Gerçek BG çeviri, tüm büyük harf formatında | `diller.bg.name` | ❌ Hayır — doğrudan kopyalanabilir |
| `bg.description` | ✅ 43/43 | Gerçek BG çeviri, ortalama 155-232 karakter | `diller.bg.description` | ❌ Hayır — doğrudan kopyalanabilir |
| `bg.specs["СТАНДАРТНИ АКСЕСОАРИ"]` | ✅ 43/43 | Gerçek BG çeviri | `diller.bg.specs["STANDARD ACCESSORIES"]` | ⚠️ KEY RENAME gerekiyor |
| `bg.specs["ОПЦИОНАЛНИ АКСЕСОАРИ"]` | ✅ 43/43 | Gerçek BG çeviri | `diller.bg.specs["OPTIONAL ACCESSORIES"]` | ⚠️ KEY RENAME gerekiyor |
| `bg.specs["ОБЩИ ХАРАКТЕРИСТИКИ"]` | ✅ 43/43 | Gerçek BG çeviri | `diller.bg.specs["GENERAL FEATURES"]` | ⚠️ KEY RENAME gerekiyor |
| `bg.specs["ТЕХНИЧЕСКИ ДАННИ"]` | ✅ 43/43 mevcut | ❌ Her zaman boş `{}` | DROP | ✅ Atla |
| `bg.images` | ❌ HİÇBİR makinede yok | — | (EN fallback) | N/A |
| `bg.technical_data` | ❌ HİÇBİR makinede yok | — | (EN fallback) | N/A |
| `bg.pdf_catalog` | ❌ HİÇBİR makinede yok | — | (EN fallback) | N/A |

### 4d. BG Name Kalite Notu

d6b5cc8'deki BG name'ler tüm büyük harf formatında:
- `"ACK 420 S ОТРЕЗНА МАШИНА С ДОЛНО ПОДАВАНЕ"`
- `"KD 350 D ОТРЕЗНА МАШИНА С ЪГЛОВА НАСТРОЙКА"`
- `"NSM 352 NSM 353 ЦЕНТЪР ЗА ОБРАБОТКА НА КРИЛА"`

Mevcut EN name'ler karma büyük-küçük harf: `"KD 350 D - Miter Saw Machine"`. Format tutarsızlığı var — estetik tercih meselesi, işlevsel sorun değil.

### 4e. Görsel Path Durumu

| Tip | d6b5cc8 | Notlar |
|---|---|---|
| BG images | 0 makine | BG hiçbir zaman image almadı |
| EN images (local) | 30/74 makine `/images/yilmaz/...` | Current individual dosyalarda tüm 88 makine local path kullanıyor |
| EN images (CDN) | 0 makine | d6b5cc8'de CDN yok; CDN sorunu sadece vce-3500/vce-4000 `diller.ru`'da (güncel dosyalarda) |

BG recovery için image path normalizasyonu GEREKMİYOR — BG images hiç olmadı, EN fallback kullanılacak.

### 4f. Technical Data Key Uyumu

d6b5cc8'deki EN `technical_data` key'leri **MEVCUT individual dosyalardan farklı**:

| d6b5cc8 EN key | Güncel individual dosya key | Durum |
|---|---|---|
| `Motor Power` | `Power` | FARKLI |
| `Blade Speed` | `Saw Rotation Speed` | FARKLI |
| `Blade Diameter` | `Saw Diameter` | FARKLI |
| `Air Pressure` | `Pressure` | FARKLI |
| `Air Consumption` | `Flow Rate` | FARKLI |
| `Dimensions` | `Dimensions (cm)` | FARKLI |
| `Weight` | `Weight` | AYNI |

> Bu fark BG recovery'yi etkilemez çünkü d6b5cc8'de BG `technical_data` hiç yok. Ama `tercume_merkezi.py`'nin EN technical_data'yı BG'ye kopyaladığı iddia edilmişti — bu aggregate'deki eski key'lerle çalışıyordu, mevcut individual dosyalarla DEĞİL.

---

## 5. Apply Stratejisi

### 5a. Doğrudan Kopyalanabilir Field'lar (Transform Yok)

| Field | Kaynak | Hedef | Risk |
|---|---|---|---|
| `bg.name` | `d6b5cc8.diller.bg.name` | `diller.bg.name` | DÜŞÜK — Gerçek BG çeviri, tüm büyük harf format farklılığı estetik |
| `bg.description` | `d6b5cc8.diller.bg.description` | `diller.bg.description` | DÜŞÜK — Gerçek BG çeviri |

### 5b. Transform Gerektiren Field'lar

| Alan | Transform | Açıklama |
|---|---|---|
| `bg.specs` key rename | `СТАНДАРТНИ АКСЕСОАРИ` → `STANDARD ACCESSORIES`<br>`ОПЦИОНАЛНИ АКСЕСОАРИ` → `OPTIONAL ACCESSORIES`<br>`ОБЩИ ХАРАКТЕРИСТИКИ` → `GENERAL FEATURES` | MachinePage.astro specs objesini generic `Object.entries()` ile okuyor — BG key adları **teknik olarak çalışır**, ama EN key'lerle normalize etmek tutarlılık sağlar |
| `bg.specs["ТЕХНИЧЕСКИ ДАННИ"]` | DROP — her zaman `{}` | Veri kaybı yok |

### 5c. Inject Edilemeyecek / Olmayan Field'lar

| Field | Durum | Etki |
|---|---|---|
| `bg.images` | d6b5cc8'de hiç yok | EN fallback devreye girer (commit `3886fe2` fix sayesinde) |
| `bg.technical_data` | d6b5cc8'de hiç yok | EN fallback devreye girer |
| `bg.pdf_catalog` | d6b5cc8'de hiç yok | EN fallback devreye girer |
| `ru.*` | 0 kullanılabilir içerik | Taze çeviri gerekiyor |

### 5d. Ghost Data Sorunu

`vce-3500` ve `vce-4000` zaten güncel individual dosyalarda ghost BG skeleton'a sahip (`images: []`, `specs: {tüm key'ler boş}`). Recovery inject'i bu skeleton'un ÜSTÜNE yazmalı — mevcut ghost temizlenip yerine gerçek BG gelecek.

### 5e. Recovery Scope Özeti

| Kategori | Makine Sayısı | İşlem |
|---|---|---|
| BG dolu → inject edilebilir (individual dosya eşleşiyor) | **42** | d6b5cc8'den name + description + specs (key rename ile) inject et |
| BG dolu → inject YAPILAMAZ (alm-6510, individual dosya yok) | **1** | Kayıp — individual dosya yoksa inject hedefi yok |
| BG boş (d6b5cc8'de key var ama içerik yok) + current'ta eşleşiyor | **31** | Taze çeviri gerekiyor |
| Yeni makineler (d6b5cc8'de hiç yok) | **15** | Taze çeviri gerekiyor |
| RU kurtarılabilir | **0** | Taze çeviri gerekiyor (88 makine) |

**Net kurtarılabilir:** 42 BG (inject) + 1 BG kayıp (alm-6510) = 43'ten 42'si kurtarılabilir.  
**Taze çeviri gerekli:** 46 BG + 88 RU

---

## 6. Ek: Specs Key Rename Haritası

Recovery scripti yazılırken kullanılacak literal key eşleştirmesi:

```
"СТАНДАРТНИ АКСЕСОАРИ"  → "STANDARD ACCESSORIES"
"ОПЦИОНАЛНИ АКСЕСОАРИ"  → "OPTIONAL ACCESSORIES"
"ОБЩИ ХАРАКТЕРИСТИКИ"   → "GENERAL FEATURES"
"ТЕХНИЧЕСКИ ДАННИ"      → (DROP)
```

---

## Özet Tablosu

| Konu | Bulgu |
|---|---|
| CMS BG/RU sekmeleri | ✅ Tanımlı (name + description only) |
| CMS specs/images/technical_data BG/RU | ❌ CMS'de YOK (JSON inject gerekli) |
| Kurtarılabilir BG makine | **42** |
| Kurtarılamaz BG (dosya yok) | 1 (alm-6510) |
| Kurtarılabilir RU | **0** (önceki audit YANLIŞ) |
| Slug eşleşme oranı | 73/74 (%98.6) |
| Yeni eklenen, BG yok | 15 makine |
| Transform gerekli | BG specs key rename (4 key) |
| Image normalizasyonu gerekli | ❌ Hayır (BG images hiç olmadı) |
| Ghost data temizliği | ✅ vce-3500, vce-4000 ghost BG üzerine yazılacak |
