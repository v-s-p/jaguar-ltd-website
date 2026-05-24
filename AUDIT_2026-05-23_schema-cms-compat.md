# Schema & CMS Uyumluluk Audit — 2026-05-23

**Kapsam:** `src/data/machines/yilmaz/` (88 dosya) + `src/data/machines/gocmaksan/` (47 dosya)  
**Yedek Arşiv:** `C:\Users\Kenan\Desktop\AI\_ARSIV_Jaguar-ltd_20260515\src\data\`  
**Amaç:** Yılmaz şemasını baseline al, Göçmaksan dönüşüm haritası çıkar, CMS form mapping yap  
**Kısıtlama:** Read-only. Fix yok. Commit yok.

---

## 1. Yılmaz — Field Path Analizi

### 1a. Toplam: 88 makine dosyası

### 1b. Top-Level Fields

| Field | Tip | Doluluk | Dil Bağımlı | Notlar |
|---|---|---|---|---|
| `slug` | string | 100% | hayır | Dosya adıyla birebir eşleşiyor |
| `brand` | string | 100% | hayır | Sabit `"yilmaz"` |
| `categories` | string[] | 100% | hayır | `["PVC"]`, `["Aluminium"]`, veya `["Aluminium","PVC"]` |
| `category` | string | 100% | hayır | **Duplikasyon/legacy** — genellikle `categories[0]` ile aynı, ama bazı makinelerde tutarsız (bkz. Anomali §6.2) |
| `subcategory` | string | 100% | hayır | Tek string. Değerler: Cutting, Assembling, Processing Centers, Swarf Extraction, Transferring, Conveying, Cleaning, vb. |
| `type` | string | ~100% | hayır | Değerler: Single Head Cutting, Trolley, Conveyors, Vacuum Swarf Extractor, Sash Assembly Station, vb. |
| `diller` | object | 100% | evet | Tüm dil içerikleri bu object altında |

### 1c. `diller.en.*` Fields (88/88 makinede mevcut)

| Field Path | Tip | Doluluk | Notlar |
|---|---|---|---|
| `diller.en.name` | string | 100% | Makinenin tam EN adı |
| `diller.en.description` | string | 100% | Düz metin, markdown değil. Kısa (1-4 cümle) ile uzun (5+ paragraf) arası değişiyor |
| `diller.en.images` | string[] | 100% | `/images/yilmaz/slug_N.ext` formatı, local path. Sayı: 2-16 arası |
| `diller.en.specs` | object | 100% | Her zaman tam 3 key (boş olsa bile): `STANDARD ACCESSORIES`, `OPTIONAL ACCESSORIES`, `GENERAL FEATURES` — değer tipi: string[] |
| `diller.en.technical_data` | object | 100% mevcut, ~82% dolu | Boş `{}` olan makineler: vakum aspiratörler, mekanik assembly istasyonları (elektrik/motor speci olmayan makineler). Populated örnekler: Power, Saw Rotation Speed, Saw Diameter, Flow Rate, Pressure, Dimensions (cm), Weight. Anahtar isimleri makineden makineye değişiyor (örn. AIM makinelerinde `Drill Rotation Speed` ek key var) |
| `diller.en.pdf_catalog` | string | ~99% | `/catalogs/yilmaz/PVC-KATALOG.pdf` veya `/catalogs/yilmaz/ALUMINIUM-KATALOG.pdf` — iki katalog tüm markayı paylaşıyor |

### 1d. Dil Dağılımı (88 makine)

| Dil | Anahtar Mevcut | Gerçek İçerik Var | Notlar |
|---|---|---|---|
| `en` | 88/88 (100%) | 88/88 (100%) | Tüm makineler dolu |
| `bg` | 2/88 (2.3%) | **0/88 (0%)** | vce-3500 + vce-4000: tamamen boş (ghost) — `name: ""`, `description: ""`, `images: []`, `specs: {tüm key'ler: []}`, `technical_data: {}` |
| `ru` | 2/88 (2.3%) | 2/88 (2.3%) | vce-3500 + vce-4000: gerçek RU içerik VAR — ama görsel URL'ler CDN external (`https://di33l1fv68t4r.cloudfront.net/...`), diğer tüm Yılmaz makinelerinde yerel `/images/...` path var |

> **Not:** Git commit `d6b5cc8` (14 Mayıs 2026) aggregate `machines.json`'da 43 BG + 42 RU Yılmaz çevirisi mevcuttu. Commit `90472af` (15 Mayıs) bu çeviriler silinmeden önce yeniden oluşturdu. Kurtarma mümkün.

### 1e. Yedek Arşiv Bulgusu

**Konum:** `C:\Users\Kenan\Desktop\AI\_ARSIV_Jaguar-ltd_20260515\src\data\`

- `src/data/machines/yilmaz/` klasörü **YOK** — arşivde bireysel dosya yok, sadece aggregate
- `yilmaz_zengin_yedek_20260419_1716.json` — **ESKİ TÜRKÇE ŞEMA**: `diller.tr.isim`, `diller.tr.aciklama`, `diller.tr.resimler`, `diller.tr.ozellik_gruplari`, `diller.tr.piktogramlar`, `kategoriler`, `alt_kategoriler`. CDN external image URL'leri. Mevcut individual dosyalardaki EN şemasından **farklı ve eski** — richer değil
- `yilmaz.json` (arşiv aggregate) — EN şemasıyla ama `technical_data` içinde HTML scraper artifactları var (örn. `"ACK 420 S – Up-Cutting Saw Machine": "PRODUCT INFO"`, `"svg%3E": "×"`)
- **Sonuç:** Arşiv, mevcut individual dosyalardan ZENGİN BİR ŞEMA İÇERMİYOR. Canonical kaynak mevcut repo'daki `src/data/machines/yilmaz/*.json` dosyaları.

---

## 2. Göçmaksan — Field Path Analizi

### 2a. Toplam: 47 makine dosyası (bireysel dosyalar mevcut)

### 2b. Top-Level Fields

| Field | Tip | Doluluk | Dil Bağımlı | Notlar |
|---|---|---|---|---|
| `slug` | string | 100% | hayır | `gms-` prefiksi, genellikle Türkçe makine adından türetilmiş |
| `brand` | string | 100% | hayır | Sabit `"gocmaksan"` |
| `categories` | string[] | 100% | hayır | Değerler: Bending Machines, Cutting Machines, Steel Factory Solutions, Light Construction, Hand Tools. Birden fazla kategori mümkün |
| `subcategory` | **string[]** | 100% | hayır | **Yılmaz'dan farklı: ARRAY**. Değerler: Standard, Steel Factory, Stirrup, Hand Tools, Light Construction |
| `pdf_catalog` | string | ~74% dolu | hayır | Top-level AND `diller.en.pdf_catalog` olarak çift yerde → **duplikasyon**. 12/47 dosyada `""` (boş string). gms-kompaktor, hand-tool makinelerinde boş |
| `related_products` | string[] | 100% | hayır | Boş `[]` olabilir. Yılmaz'da bu field **YOK** |
| `specs` | object | 100% | hayır | **Top-level, Yılmaz'dan farklı.** Key varyasyonları var (bkz. §2c) |
| `diller` | object | 100% | evet | |

### 2c. `specs` Key Varyasyonları

| Key Adı | Tip | Kaç Dosyada | Notlar |
|---|---|---|---|
| `FEATURED FEATURES` | string[] | ~40+ | Çoğu makine |
| `TECHNICAL DATA` | object (key:value) | ~40+ | Boş `{}` olabilir |
| `CAPACITIES` | string[] | ~35+ | Boş `[]` olabilir |
| `SUPPLIED EQUIPMENT` | string[] | ~2 | gms-sls-12 ve benzer endüstriyel makine türü |
| `CAPACITY` (tekil) | string[] | ~7 | Hand tool makineleri — `CAPACITIES`'den farklı key adı. Dikkat: inconsistency |

### 2d. `diller.en.*` Fields (47/47 makinede mevcut)

| Field Path | Tip | Doluluk | Notlar |
|---|---|---|---|
| `diller.en.name` | string | 100% | |
| `diller.en.description` | string | 100% | Markdown formatında (## başlıklar, paragraflar). Uzun (300-800+ kelime). Stub makinelerde tek cümle (hand tools) |
| `diller.en.images` | string[] | 100% | Mix: `/images/gocmaksan/...` (local) ve bazı makinelerde `slug_N.webp` pattern |
| `diller.en.pdf_catalog` | string | ~75% | Top-level `pdf_catalog` ile genellikle aynı değer — **duplikasyon**. Bazı makinelerde (gms-kompaktor) `diller.en.pdf_catalog` field'ı **hiç yok** |

### 2e. Dil Dağılımı (47 makine)

| Dil | Anahtar Mevcut | Gerçek İçerik Var | Notlar |
|---|---|---|---|
| `en` | 47/47 (100%) | 47/47 (100%) | |
| `bg` | 39/47 (83%) | 39/47 (83%) | Yalnızca `description` field — `name`, `images`, `specs`, `pdf_catalog` YOK |
| `ru` | 39/47 (83%) | 39/47 (83%) | Yalnızca `description` field — aynı kısıt |

**8 Makine BG/RU Eksik:**

| Slug | Kategori | Neden Eksik |
|---|---|---|
| gms-ayarli-kosebentler-gocmaksan | Hand Tools | EN desc < 500 char → retranslate_bgru.py skip |
| gms-demirci-anahtarlari-gocmaksan | Hand Tools | EN desc < 500 char → skip |
| gms-el-makaslari-gocmaksan | Hand Tools | EN desc < 500 char → skip |
| gms-etriye-kollari-gocmaksan | Hand Tools | EN desc < 500 char → skip |
| gms-kalip-sokmeler-gocmaksan | Hand Tools | EN desc < 500 char → skip |
| gms-kompaktor | Light Construction | EN desc < 500 char → skip |
| gms-oturak-makaslari-gocmaksan | Hand Tools | EN desc < 500 char → skip |
| gms-rl-2000-gocmaksan-cift-tamburlu-silindir | Light Construction | EN desc < 500 char → skip |

> `retranslate_bgru.py`'daki `MIN_EN_CHARS = 500` guard bu 8 makineyi stub olarak değerlendiriyor.

---

## 3. Karşılaştırma Tablosu

| Field Adı | Yılmaz | Göçmaksan | Durum | Dönüşüm Notu |
|---|---|---|---|---|
| `slug` | string | string | **AYNI** | — |
| `brand` | `"yilmaz"` | `"gocmaksan"` | **AYNI (tip)** | Değer farklı |
| `categories` | string[] | string[] | **AYNI** | Kategori değerleri farklı domain |
| `subcategory` | **string** | **string[]** | **FARKLI (tip)** | Göçmaksan array → dönüşümde ilk eleman alınabilir veya join |
| `category` | string (legacy) | **YOK** | **YILMAZ-ÖZEL** | Redundant field, `categories[0]` kopyası |
| `type` | string | **YOK** | **YILMAZ-ÖZEL** | Göçmaksan için eklenecek |
| `pdf_catalog` (top-level) | **YOK** | string | **GOCMAKSAN-ÖZEL** | Duplikasyon sorunlu; Yılmaz'da sadece `diller.en.pdf_catalog` |
| `related_products` | **YOK** | string[] | **GOCMAKSAN-ÖZEL** | Yılmaz şemasında yok; dönüşümde karar gerekiyor |
| `specs` (top-level) | **YOK** | object | **GOCMAKSAN-ÖZEL** | Yılmaz'da `diller.en.specs` içinde |
| `specs["STANDARD ACCESSORIES"]` | `diller.en.specs` içinde | **YOK** | **YILMAZ-ÖZEL** | — |
| `specs["OPTIONAL ACCESSORIES"]` | `diller.en.specs` içinde | **YOK** | **YILMAZ-ÖZEL** | — |
| `specs["GENERAL FEATURES"]` | `diller.en.specs` içinde | **YOK** | — | ↔ `specs["FEATURED FEATURES"]` |
| `specs["FEATURED FEATURES"]` | **YOK** | top-level specs | — | ↔ `diller.en.specs["GENERAL FEATURES"]` |
| `specs["TECHNICAL DATA"]` (object) | **YOK** | top-level specs | **FARKLI** | ↔ `diller.en.technical_data` — aynı veri, farklı path + nesting |
| `specs["CAPACITIES"]` | **YOK** | top-level specs | **GOCMAKSAN-ÖZEL** | Yılmaz şemasında karşılık yok |
| `specs["SUPPLIED EQUIPMENT"]` | **YOK** | top-level specs | **GOCMAKSAN-ÖZEL** | Nadiren görülen key |
| `diller.en.name` | `diller.en` içinde | `diller.en` içinde | **AYNI** | — |
| `diller.en.description` | plain text | markdown | **FARKLI (format)** | Göçmaksan Markdown, Yılmaz düz metin. MachinePage.astro `marked.parse()` her ikisini de işliyor |
| `diller.en.images` | local `/images/yilmaz/` | local `/images/gocmaksan/` | **AYNI (tip)** | Path prefix farklı |
| `diller.en.pdf_catalog` | mevcut | mevcut (bazılarında eksik) | **AYNI** | Göçmaksan'da top-level ile duplikasyon var |
| `diller.en.technical_data` | `diller.en` içinde | **YOK** (top-level `specs["TECHNICAL DATA"]` içinde) | **FARKLI (path)** | |
| `diller.bg.description` | **YOK** | mevcut (39/47) | **GOCMAKSAN-ÖZEL** | — |
| `diller.ru.description` | **YOK** | mevcut (39/47) | **GOCMAKSAN-ÖZEL** | — |
| `diller.bg.name` | **YOK** | **YOK** | **İKİSİNDE DE EKSİK** | — |
| `diller.ru.name` | **YOK** | **YOK** | **İKİSİNDE DE EKSİK** | — |

---

## 4. Göçmaksan → Yılmaz Dönüşüm Haritası

Her Göçmaksan field'ı için Yılmaz hedef path ve transform notu:

| Göçmaksan Field | Yılmaz Hedef Path | Transform | Risk |
|---|---|---|---|
| `slug` | `slug` | Değişiklik yok | — |
| `brand` | `brand` | Değişiklik yok | — |
| `categories` | `categories` | Değişiklik yok; kategori değerleri farklı domain ama yapı aynı | — |
| `subcategory` (array) | `subcategory` (string) | `array[0]` al veya `array.join(" / ")` | Veri kaybı: çoklu subcategory bilgisi kaybolur. Önerilen: join |
| `pdf_catalog` (top-level `""` veya path) | **REMOVE** | `diller.en.pdf_catalog` içindeki değeri kullan; top-level field kaldırılır | Top-level ile diller.en arası hangisi canonical? Genelde aynı. Boş string durumunda null olarak normalize et |
| `related_products` | **KARAR GEREKİYOR** | Yılmaz şemasında karşılık yok. Seçenekler: (a) kaldır, (b) yeni top-level field olarak ekle | Veri kaybı riski yüksek; özellik durumuna göre karar verilmeli |
| `specs["FEATURED FEATURES"]` (array) | `diller.en.specs["GENERAL FEATURES"]` | Key rename + path taşıma (top-level → diller.en içi) | Key adı değişiyor — MachinePage.astro bunu generik `Object.entries()` ile okuyor, eski key adı hala çalışır ama normalize etmek temizler |
| `specs["TECHNICAL DATA"]` (object) | `diller.en.technical_data` | Unnest + path taşıma | Boş `{}` → `{}` kalır. Bazı Göçmaksan makinelerinde HTML entity var (`&quot;`) |
| `specs["CAPACITIES"]` (array) | Yılmaz karşılığı **YOK** | Seçenek 1: `diller.en.specs` içine yeni key olarak ekle. Seçenek 2: description sonuna append. Seçenek 3: `diller.en.technical_data` içine flatten (uygunsuz) | Göçmaksan'a özgü veri türü. Bire-bir dönüşüm mümkün değil |
| `specs["SUPPLIED EQUIPMENT"]` (array) | `diller.en.specs["STANDARD ACCESSORIES"]` | Key rename + path taşıma | Semantic uyum zayıf (supplied ≠ standard) ama en yakın karşılık |
| `specs["CAPACITY"]` (tekil, hand tools) | `diller.en.technical_data` veya `diller.en.specs["GENERAL FEATURES"]` | Değer tek satır, format küçük | Makine türüne göre karar |
| `diller.en.name` | `diller.en.name` | Değişiklik yok | — |
| `diller.en.description` | `diller.en.description` | Değişiklik yok; markdown kalır (MachinePage.astro işliyor) | — |
| `diller.en.images` | `diller.en.images` | Değişiklik yok | — |
| `diller.en.pdf_catalog` | `diller.en.pdf_catalog` | Değişiklik yok | Top-level duplikasyonu kaldırılmalı |
| `diller.bg.description` | `diller.bg.description` | Değişiklik yok | — |
| `diller.ru.description` | `diller.ru.description` | Değişiklik yok | — |
| **YOK** → `category` | `category` | Yılmaz'da legacy field: `categories[0]` kopyası. Dönüşümde otomatik generate edilebilir | Legacy field — yeni sistemde kaldırmak mantıklı |
| **YOK** → `type` | `type` | Göçmaksan'da bu field yok. CMS'de manuel girilmesi gerekir | Boş string veya "N/A" ile başlatılabilir |

---

## 5. Yılmaz Şeması — CMS Form Mapping

> Kavramsal haritalama. Kod değil. Göçmaksan dönüşümü sonrası her iki marka da bu forma oturursa tek unified CMS yeterli.

### Grup 1: Genel

| Field | Input Tipi | Required | Notlar |
|---|---|---|---|
| `slug` | text (read-only, auto-generate) | Evet | Kayıt sonrası değiştirilemez; `name` → slugify |
| `brand` | select (yilmaz / gocmaksan) | Evet | |
| `categories` | checkbox-group (PVC / Aluminium / Bending Machines / vb.) | Evet | Multi-select |
| `subcategory` | text veya select | Hayır | Opsiyonel |
| `type` | text | Hayır | Kısa açıklayıcı (örn. "Single Head Cutting") |

### Grup 2: Diller (Dil Tabları: EN | BG | RU)

Her dil tabında:

| Field | Input Tipi | Required | Notlar |
|---|---|---|---|
| `name` | text (tek satır) | EN: Evet, BG/RU: Hayır | |
| `description` | textarea / markdown editor | EN: Evet, BG/RU: Hayır | Markdown destekli (marked.js uyumlu) |

### Grup 3: Görseller (EN tab altında veya ayrı)

| Field | Input Tipi | Required | Notlar |
|---|---|---|---|
| `images` | image-upload repeater | EN: Evet | Drag-reorder, çoklu seçim. İlk görsel ana görsel (MachinePage'de `images[0]`) |

### Grup 4: Specs (EN tab altında)

Her grup ayrı list/repeater:

| Field | Input Tipi | Required | Notlar |
|---|---|---|---|
| `specs["STANDARD ACCESSORIES"]` | list-repeater (text item) | Hayır | Boş array kabul |
| `specs["OPTIONAL ACCESSORIES"]` | list-repeater (text item) | Hayır | |
| `specs["GENERAL FEATURES"]` | list-repeater (text item) | Hayır | Göçmaksan dönüşümünde `FEATURED FEATURES` bu gruba map'lenir |

### Grup 5: Teknik Tablo (EN tab altında)

| Field | Input Tipi | Required | Notlar |
|---|---|---|---|
| `technical_data` | key-value repeater | Hayır | Key: text, Value: text. Tüm makine tiplerinde farklı anahtar setleri var — serbest girilmeli |

### Grup 6: PDF

| Field | Input Tipi | Required | Notlar |
|---|---|---|---|
| `pdf_catalog` | text (URL path) veya file-upload | Hayır | Path formatı: `/catalogs/{brand}/...`. Göçmaksan dönüşümünde top-level ayrı field kaldırılır, sadece bu field kalır |

### (Opsiyonel) Grup 7: Göçmaksan Özgün Alanlar

Bu alanlar Göçmaksan tutulursa:

| Field | Input Tipi | Required | Notlar |
|---|---|---|---|
| `related_products` | list-repeater (text) | Hayır | Ürün slug veya model adı |
| `specs["CAPACITIES"]` | list-repeater (text) | Hayır | Göçmaksan makine tiplerine özgü |

---

## 6. Anomali Listesi

### 6.1 Ghost Data — BG Bloklama Sorunu

| Makine | Durum | Etkisi |
|---|---|---|
| `vce-3500` | `diller.bg` mevcut ama TÜM alanlar boş: `name: ""`, `description: ""`, `images: []`, `specs` içi tüm key'ler `[]`, `technical_data: {}` | `images: []` → truthy empty array → MachinePage L41 `activeLang.images || enLang.images` → sol operand `[]` döner (truthy) → EN görsel fallback ÇALIŞMIYOR. BG ziyaretçiler görselsiz sayfa görür |
| `vce-4000` | vce-3500 ile aynı ghost BG yapısı | Aynı görsel fallback sorunu |

**Ek anomali:** Aynı 2 makinede `diller.ru` ise gerçek içerik var ama görsel URL'leri external CDN (`https://di33l1fv68t4r.cloudfront.net/...`) — diğer tüm Yılmaz makineleri local `/images/...` kullanıyor. CDN URL'leri fragile, kontrol dışı.

### 6.2 Legacy `category` / `categories` Tutarsızlığı

Yılmaz dosyalarında hem `category` (string) hem `categories` (array) var. İkisi genellikle aynı (`categories[0] === category`), ancak:

| Makine | `categories` | `category` | Tutarsızlık |
|---|---|---|---|
| `gpt-1000-glass-window-trolley` | `["Aluminium","PVC"]` | `"PVC"` | `categories[0]` "Aluminium" ama `category` "PVC" |
| `dkn-300-450-600-...` | `["Aluminium","PVC"]` | `"PVC"` | Aynı tutarsızlık |

MachinePage.astro navigation URL'yi `categories.includes('Aluminium')` ile belirliyor (L25-27) — bu doğru olanı kullanıyor. `category` field'ı sitenin hiçbir yerinde kullanılmıyor olabilir ama data tutarsızlığı risk.

### 6.3 Göçmaksan `subcategory` Tip Uyumsuzluğu

| Brand | `subcategory` tipi | Örnek |
|---|---|---|
| Yılmaz | `string` | `"Cutting"` |
| Göçmaksan | `string[]` | `["Standard", "Steel Factory"]` |

MachinePage.astro L87'de `Array.isArray(machine.subcategory)` kontrolü var — UI bu farkı zaten handle ediyor. Ama tek şema altında toplamak için normalize edilmeli.

### 6.4 Göçmaksan `pdf_catalog` Duplikasyonu

Top-level `pdf_catalog` ile `diller.en.pdf_catalog` genellikle aynı değeri taşıyor. Sorunlu durumlar:

- 12 dosyada top-level `pdf_catalog: ""` (boş string) ama `diller.en.pdf_catalog` yok veya farklı
- `gms-kompaktor`: top-level `""` + `diller.en` içinde `pdf_catalog` field'ı hiç yok
- MachinePage.astro L48 katalog fallback zinciri: `activeLang.catalog || activeLang.katalog || activeLang.pdf_catalog || enLang.catalog || enLang.katalog || enLang.pdf_catalog || (machine as any).pdf_catalog` — top-level `pdf_catalog`'u son sırada kontrol ediyor

### 6.5 Göçmaksan `specs` Key İsimleri Tutarsızlığı

| Sorun | Dosyalar | Etki |
|---|---|---|
| `CAPACITY` (tekil) yerine `CAPACITIES` | Hand tool makineleri (gms-el-makaslari, gms-ayarli-kosebentler, vb.) | UI'da başlık `CAPACITY` görünüyor, diğer makinelerden farklı |
| `SUPPLIED EQUIPMENT` key'i | gms-sls-12 ve benzer fabrika makineleri | Standart dışı key — dönüşüm haritasında özel case |

### 6.6 Yılmaz `technical_data` Scraper Artifactları (Arşiv)

Arşiv `yilmaz.json`'da (commit `d6b5cc8` öncesi dönem):
```json
"technical_data": {
  "ACK 420 S – Up-Cutting Saw Machine": "PRODUCT INFO",
  "svg%3E": "×"
}
```
HTML scraper artığı. Mevcut individual dosyalarda bu sorun **giderilmiş** (örnek: `kd-350-d` `technical_data` temiz). Ama yeni scraper çalıştırmalarında tekrar oluşabilir.

### 6.7 Yılmaz Makineler — BG Eksik Listesi (86 makine)

Mevcut individual dosyalarda BG içeriği olan Yılmaz makinesi: **0** (vce-3500/vce-4000 ghost, sayılmaz).

Kurtarılabilir (commit `d6b5cc8`): 43 BG + 42 RU
Kalan (çeviri gerektirir): ~45 BG + ~46 RU

> Tam slug listesi için: `git show d6b5cc8:src/data/machines.json | grep -c '"bg"'`

### 6.8 Legacy `piktogramlar` Field Kalıntısı

MachinePage.astro L47:
```javascript
const piktogramlar = activeLang.piktogramlar || activeLang.specifications || {};
```

Mevcut Yılmaz individual dosyaların **hiçbirinde** `piktogramlar` field'ı yok (grep: 0 eşleşme). Eski Türkçe şemada (`diller.tr.piktogramlar`) mevcuttu. Bu satır dead code — her zaman `{}` döner. Göçmaksan'da da yok.

### 6.9 `diller.en.technical_data: {}` Olan Yılmaz Makineleri

Boş `technical_data` olan makineler elektrik/motor speci olmayan kategorilerde toplanıyor:
- Tüm Vacuum/Swarf Extractor makineleri: vce-1570, vce-3500, vce-4000
- Assembly istasyonları: nsm-352-nsm-353
- Gasket milling: wgm-202
- (ve muhtemelen bazı taşıma arabası makineleri)

Bu CMS'de sorun değil — boş `{}` kabul edilebilir. Ama scraper/enrich pipeline bu makinelerde teknik veri olmayacağını biliyor mu kontrolü yapılabilir.

---

## Özet

| Konu | Yılmaz | Göçmaksan |
|---|---|---|
| Toplam dosya | 88 | 47 |
| Şema stabilitesi | ✅ Tutarlı | ⚠️ `specs` key'leri değişken |
| EN içerik | ✅ 100% | ✅ 100% |
| BG içerik | ❌ 0% gerçek (2 ghost) | ⚠️ 83% (description only) |
| RU içerik | ⚠️ 2% (2 makine, external CDN) | ⚠️ 83% (description only) |
| pdf_catalog | ✅ diller.en içinde | ⚠️ çift yerde, bazıları boş |
| related_products | ❌ yok | ✅ var (CMS kararı gerekli) |
| `type` field | ✅ var | ❌ yok |
| `subcategory` tip | string | string[] |
| Legacy fields | `category` (redundant) | — |
| CMS-form uyumu | ✅ Yılmaz şeması CMS'e doğrudan oturuyor | ⚠️ `specs` path + subcategory tip dönüşümü gerekli |
