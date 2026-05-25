# Göçmaksan Schema Audit — D7 Faz 1

**Tarih:** 2026-05-25  
**Branch:** main @ d9fcdf1  
**Amaç:** Göçmaksan'ı Yılmaz şema kalıbına dökmek için baseline diff.  
**Kısıt:** Read-only — hiçbir JSON/kod değiştirilmedi.

---

## 1. Yedek Dosya Taraması

**Konum:** `C:\Users\Kenan\Desktop\AI\_ARSIV_Jaguar-ltd_20260515\src\data\`

### Göçmaksan ile ilgili dosyalar

| Dosya | Boyut | Makine | Top-level Keys | Langs |
|---|---|---|---|---|
| `gocmaksan_backup_20260424_0944.json` | 4.9 KB | 3 | slug, brand, **category** (tek), subcategory, pdf_catalog, diller | en |
| `gocmaksan_backup_20260424_0954.json` | 4.1 KB | 3 | slug, brand, **category** (tek), subcategory, pdf_catalog, diller | en |
| `gocmaksan_backup_20260424_0959.json` | 3.2 KB | 3 | slug, brand, **category** (tek), subcategory, pdf_catalog, related_products, diller | en |
| `gocmaksan_backup_20260425_2046.json` | 57.8 KB | 46 | slug, brand, **category** (tek), subcategory, pdf_catalog, related_products, diller | en |
| `gocmaksan_backup_20260425_2056.json` | 63.9 KB | 46 | slug, brand, **categories** (array), subcategory, pdf_catalog, related_products, diller | en |
| `gocmaksan_backup_20260425_2106.json` | 65.6 KB | 47 | slug, brand, categories, subcategory, pdf_catalog, related_products, diller | en |
| **`gocmaksan_backup_20260426_1159.json`** | **76.1 KB** | **47** | slug, brand, categories, subcategory, pdf_catalog, related_products, diller | **en + bg** |
| `gocmaksan_backup_20260515_1520.json` | 57.1 KB | 47 | slug, brand, categories, subcategory, pdf_catalog, related_products, **specs** (top-level), diller | en + bg |

### Notlar
- **20260426_1159** en büyük (76 KB) ve en zengin backup: specs `diller.en.specs` içinde, yani Yılmaz şemasıyla uyumlu. Bu backup Faz 2 migration için **referans olarak kullanılabilir**.
- **20260515_1520**: specs top-level'a taşınmış ama `diller.bg` kaybedilmiş (BG description'lar gitti). Bu backup **kullanılmamalı**.
- İlk 3 backup'ta `category` (string) var, sonrakilerde `categories` (array) — schema geçiş izi görünüyor.
- `machines.json.yedek`: 2 byte, boş/placeholder.

---

## 2. Mevcut Göçmaksan Şeması

### Kaynak dosyalar
- Aggregate: `src/data/gocmaksan.json` — **47 makine**
- Individual: `src/data/machines/gocmaksan/*.json` — **47 dosya** (aggregate ile birebir aynı şema)

### Top-level Keys (aggregate + individual)
```json
["slug", "brand", "categories", "subcategory", "pdf_catalog", "related_products", "specs", "diller"]
```

### `diller` Keys
```
en, bg, ru
```

### `diller.en` Keys (tüm 47 makinede sabit)
```json
["name", "description", "images", "pdf_catalog"]
```
> ⚠️ `specs` ve `technical_data` diller.en içinde **yok** — top-level `specs`'e taşınmış.

### `diller.bg` Keys (mevcut içerik)
```json
["description"]
```
> ⚠️ `name` yok, sadece description.

### `diller.ru` Keys (mevcut içerik)
```json
["description"]
```
> ⚠️ Aynı sorun: `name` yok.

### Tam Şema Örneği — `gms-axis-50s-gocmaksan-spiral-demir-bukme-makinasi`
```json
{
  "slug": "gms-axis-50s-gocmaksan-spiral-demir-bukme-makinasi",
  "brand": "gocmaksan",
  "categories": ["Steel Factory Solutions", "Bending Machines"],
  "subcategory": ["Spiral", "Steel Factory"],
  "pdf_catalog": "/catalogs/gocmaksan/gms-axis-50s-...pdf",
  "related_products": ["B 50", "B 45x1", "B 36"],
  "specs": {
    "TECHNICAL DATA": {
      "Bending motor": "5.5 KW",
      "Weight": "1140kg",
      ...
    },
    "CAPACITIES": ["Ø 50: 1", "Ø 40: 1", ...],
    "FEATURED FEATURES": ["Spiral bending up to 50 mm", ...]
  },
  "diller": {
    "en": {
      "name": "Axis 50S",
      "description": "## Overview\n...",
      "images": ["/images/gocmaksan/..._1.webp", ...],
      "pdf_catalog": "/catalogs/gocmaksan/...pdf"
    },
    "bg": {
      "description": "## Преглед\n..."
    },
    "ru": {
      "description": "## Обзор\n..."
    }
  }
}
```

---

## 3. Yılmaz vs Göçmaksan Şema Diff

### Yan Yana Karşılaştırma

| Alan | Yılmaz (baseline) | Göçmaksan (mevcut) | Durum |
|---|---|---|---|
| `slug` | string | string | ✅ Aynı |
| `brand` | string | string | ✅ Aynı |
| `categories` | string[] | string[] | ✅ Aynı |
| `subcategory` | **string** | **string[]** | ❌ Tip uyumsuz |
| `type` | string (88/88) | **yok** (0/47) | ❌ Eksik alan |
| `category` (legacy) | string (legacy, bazılarında) | **yok** | — |
| `related_products` | **yok** | string[] (32/47 dolu) | ⚠️ Fazladan alan |
| `specs` (top-level) | **yok** | object | ❌ Yanlış konum |
| `pdf_catalog` (top-level) | **yok** | string (35/47) | ❌ Yanlış konum |
| `diller.en.name` | ✅ string | ✅ string | ✅ Aynı |
| `diller.en.description` | ✅ string | ✅ string | ✅ Aynı |
| `diller.en.images` | ✅ string[] | ✅ string[] | ✅ Aynı |
| `diller.en.specs` | ✅ object (tüm makinelerde) | **yok** — top-level'da | ❌ Yanlış konum |
| `diller.en.technical_data` | ✅ object (80/88) | **yok** — TECHNICAL DATA specs altında | ❌ Yanlış konum |
| `diller.en.pdf_catalog` | ✅ string (88/88) | ✅ string (39/47 dolu) | ✅ Konum doğru, kapsam eksik |
| `diller.bg.name` | ✅ string | **yok** (0/47) | ❌ Eksik |
| `diller.bg.description` | ✅ string | ✅ string (39/47) | ✅ Konum doğru |
| `diller.bg.specs` | ✅ object (bazılarında) | **yok** | ⚠️ Eksik (BG çevirisi gerekecek) |
| `diller.ru.name` | — | **yok** (0/47) | ❌ Eksik |
| `diller.ru.description` | — | ✅ string (39/47) | ✅ Konum doğru |

### 5 Bilinen Sapma — Doğrulama

1. **`subcategory` tipi** — `string` (Yılmaz) vs `string[]` (Göçmaksan): **DOĞRULANDI**  
   Göçmaksan'da 47/47 makine array. Örnek: `["Spiral", "Steel Factory"]`

2. **`specs` konumu** — `diller.en.specs` (Yılmaz) vs top-level `specs` (Göçmaksan): **DOĞRULANDI**  
   Göçmaksan'da specs hiçbir zaman diller içinde değil. Backup `20260426_1159` specs'i `diller.en.specs`'te tutuyordu — sonra top-level'a taşındı.

3. **`pdf_catalog` çift yeri** — Göçmaksan'da hem top-level hem `diller.en.pdf_catalog` aynı anda var: **DOĞRULANDI**  
   35 makinede iki yerde aynı path. Yılmaz sadece `diller.en.pdf_catalog` kullanıyor.

4. **`type` field** — Yılmaz'da 88/88 var, Göçmaksan'da 0/47: **DOĞRULANDI**

5. **`related_products` fazlalığı** — Yılmaz'da bu field hiç yok, Göçmaksan'da 32/47 dolu: **DOĞRULANDI**  
   İçerik: makine isim stringleri (`["B 50", "B 45x1", "B 36"]`), slug değil.

### Ek Sapmalar (yeni)

6. **`diller.bg.name` / `diller.ru.name` eksik** — Tüm 47 makinede BG ve RU dil bloklarında `name` anahtarı yok.  
   Yılmaz'da her lokalizasyonda `name` mevcut.

7. **`diller.en.technical_data` yok** — Yılmaz'da 80/88 makinede `diller.en.technical_data` ayrı bir field. Göçmaksan'da TECHNICAL DATA specs objesinin içine gömülü.

8. **`category` (tekil, legacy)** — Erken backup'larda var (24 Nisan tarihlilerde), mevcut şemada temizlenmiş.

---

## 4. Spec Key Mapping Önerisi

### Mevcut Göçmaksan Spec Key'leri

| Key | Tip | Makine Sayısı | Örnek İçerik |
|---|---|---|---|
| `TECHNICAL DATA` | object (dict) | 40 | `{"Bending motor": "5.5 KW", "Weight": "1140kg"}` |
| `CAPACITIES` | array (string[]) | 40 | `["Ø 50: 1", "Ø 40: 1", "Ø 32: 1"]` |
| `FEATURED FEATURES` | array (string[]) | 40 | `["Touchscreen control panel", "Pneumatic safety door"]` |
| `CAPACITY` | array (string[]) | 5 | `["Ø 8 - Ø 26"]` — sadece el aletleri |
| `SUPPLIED EQUIPMENT` | array (string[]) | 1 | `["Stirrup Head: 6-8mm", "2 Knives For Each Measure"]` |
| *(empty)* | — | 1 | `gms-kalip-sokmeler-gocmaksan` (Lever, Hand Tool) |

### Önerilen Mapping → Yılmaz Şemasına

| Göçmaksan (mevcut) | → Yılmaz Hedef | Konum | Aksiyon |
|---|---|---|---|
| `specs["FEATURED FEATURES"]` | `diller.en.specs["GENERAL FEATURES"]` | `diller.en.specs` içine | Key yeniden adlandır + taşı |
| `specs["TECHNICAL DATA"]` | `diller.en.technical_data` | `diller.en` içine ayrı field olarak | Çıkart + taşı |
| `specs["CAPACITIES"]` | `diller.en.specs["GENERAL FEATURES"]`'e **merge** | `diller.en.specs` içine | Önerim: GENERAL FEATURES listenin altına ekle veya `"CAPACITIES"` key'ini koru |
| `specs["CAPACITY"]` | `diller.en.specs["GENERAL FEATURES"]` içine | `diller.en.specs` içine | Aynı treatment, 5 el aleti makinesi |
| `specs["SUPPLIED EQUIPMENT"]` | `diller.en.specs["STANDARD ACCESSORIES"]` | `diller.en.specs` içine | Key yeniden adlandır + taşı |

> **Not:** `CAPACITIES` için 2 seçenek var:  
> - **Option A (temiz):** Yılmaz key'lerine tamamen uy → GENERAL FEATURES'e birleştir  
> - **Option B (veri kaybetme):** `"CAPACITIES"` key'ini Göçmaksan'a özgü key olarak koru, Yılmaz render'ı zaten `specs` objesi içindeki tüm key'leri gösteriyor

### Specs Konumu Özeti
- Mevcut: `machine.specs` (top-level)  
- Hedef: `machine.diller.en.specs` + `machine.diller.bg.specs`  
- `technical_data` ayrı field olarak: `machine.diller.en.technical_data`

---

## 5. BG/RU Coverage

### Özet Tablo

| Alan | BG | RU |
|---|---|---|
| `name` dolu | **0 / 47** | **0 / 47** |
| `description` dolu (>10 karakter) | **39 / 47** | **39 / 47** |
| Eksik `description` | 8 makine | 8 makine (aynı liste) |

### Eksik BG ve RU Description Olan Makineler (8'i aynı)

```
gms-ayarli-kosebentler-gocmaksan        (El Aleti — Adjustable Corner Clamps)
gms-demirci-anahtarlari-gocmaksan       (El Aleti — Blacksmith Wrenches)
gms-el-makaslari-gocmaksan              (El Aleti — Hand Shears)
gms-etriye-kollari-gocmaksan            (El Aleti — Stirrup Arms)
gms-kalip-sokmeler-gocmaksan            (El Aleti — Lever / Form Puller)
gms-kompaktor                           (Hafif İnşaat — Compactor)
gms-oturak-makaslari-gocmaksan          (El Aleti — Bench Shears)
gms-rl-2000-gocmaksan-cift-tamburlu-silindir  (Hafif İnşaat — Road Roller)
```

**Örüntü:** 6 el aleti (Hand Tools) + 2 hafif inşaat makinesi. Bu 8'i muhtemelen ilk scraping turunda atlandı.

### Kritik: BG ve RU name'leri tüm 47 makinede eksik
Yılmaz'da `diller.bg.name` mevcut. Göçmaksan için 47 BG + 47 RU name çevirisi gerekiyor.

---

## 6. Hafif İnşaat Makineleri Durumu

### 4 Makine Mevcut (JSON'da var)

| Slug | İsim | EN Desc | BG Desc | Images | Specs |
|---|---|---|---|---|---|
| `gms-bcz-600-gocmaksan-tugla-kesme-makinasi` | BCZ 600 | ✅ | ✅ | 4 | ✅ |
| `gms-kompaktor` | Compactor | ✅ | ❌ | 1 | ✅ |
| `gms-perdah-makinasi` | Power Trowel | ✅ | ✅ | 5 | ✅ |
| `gms-rl-2000-gocmaksan-cift-tamburlu-silindir` | RL 2000 | ✅ | ❌ | 1 | ✅ |

### Değerlendirme

- **BCZ 600** — Tam dolu (4 görsel, BG çevirisi var). Hazır.
- **Power Trowel (Perdah)** — Tam dolu (5 görsel, BG çevirisi var). Hazır.
- **Compactor (Kompaktor)** — Zayıf: sadece 1 görsel, BG description yok. İçerik scraping gerekiyor.
- **RL 2000** — Zayıf: sadece 1 görsel, BG description yok. İçerik scraping gerekiyor.

### Kompaktor ve RL 2000 için eksik içerik
Her iki makine `categories: ["Light Construction"]` (tek kategori), yani filtre butonunda "Light Construction" altında görünüyorlar ama detay sayfaları zayıf. Muhtemelen scraping turunda Göçmaksan sitesinden yeterli içerik çekilemedi.

### Başka Light Construction makinesi var mı?
Tüm 47 makinede Light Construction filtresi: **sadece bu 4 makine** (BCZ 600, Kompaktör, Perdah, RL 2000). Başka yoktur.

---

## Özet — Migration İçin Öncelik Sırası (Faz 2 için)

### Yüksek öncelik (breaking / görünür)
1. **`subcategory` string'e dönüştürme** — Navbar filter mantığı string bekliyor (Bending Machines, Cutting Machines vb.). Primary category seçilmeli.
2. **`diller.bg.name` + `diller.ru.name` ekleme** — MachinePage navbar/title için kullanılıyor, şu an EN fallback çalışıyor ama eksik.
3. **`specs` → `diller.en.specs`'e taşıma** — Yılmaz ile aynı render pipeline'ını kullanmak için.

### Orta öncelik (schema temizliği)
4. **`TECHNICAL DATA` → `diller.en.technical_data`'ya taşıma**
5. **`FEATURED FEATURES` → `GENERAL FEATURES` yeniden adlandırma**
6. **`pdf_catalog` top-level'ı silme** (diller.en'de zaten var)

### Düşük öncelik (içerik)
7. **8 makinede BG/RU description tamamlama** (Gemini ile çeviri)
8. **Kompaktor + RL 2000 görsel ve içerik enrichment**
9. **`related_products` sluglara dönüştürme veya silme** (cross-link feature için)

---

*Oluşturuldu: 2026-05-25 — Sadece okuma, hiçbir dosya değiştirilmedi.*
