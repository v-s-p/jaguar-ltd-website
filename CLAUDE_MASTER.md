# JAGUAR LTD — ACİL FIX PROTOKOLÜ
# Claude Code'a ver: "Bu dosyayı oku ve adım adım uygula"

## SORUNUN TAMAMI

machines.json hala ESKİ formatta:
- diller.TR (en yerine tr)
- kategoriler: ["Aluminyum"] (categories yerine)
- alt_kategoriler: ["KESIM"] (subcategory yerine)

gocmaksan.json YENİ formatta:
- diller.EN
- categories: ["Bending Machines"]
- subcategory: "Standard"

KategoriPage ve MachinePage bu iki farklı yapıyı karıştırıyor → PVC'de slug ismi, bozuk resimler.

---

## ADIM 1 — machines.json'ı migrate et

```bash
cd C:\Users\Kenan\Desktop\AI\Jaguar-ltd\scripts
python migrate_v2.py
```

migrate_v2.py şunları yapmalı (kontrol et, yoksa yaz):
- diller.tr → diller.en
- isim → name (ve "ACK 420 S - Up-Cutting..." → "ACK 420 S" temizle)
- aciklama → description
- resimler → images
- ozellik_gruplari → specs
- kategoriler: ["Aluminyum"] → categories: ["Aluminium"]
- kategoriler: ["PVC"] → categories: ["PVC"]
- alt_kategoriler: ["KESIM"] → subcategory: "Cutting"
- brand: "yilmaz" ekle

Kategori dönüşüm tablosu:
```python
KAT_EN = {
    "Aluminyum": "Aluminium", "Alüminyum": "Aluminium", "PVC": "PVC"
}
ALT_EN = {
    "KESIM": "Cutting",
    "ISLEME MERKEZLERI": "Machining Centers",
    "ISLEME MERKEZI": "Machining Centers",
    "FREZE": "Routing & Milling",
    "KOSE PRES": "Corner Crimping",
    "KERTME": "End Milling",
    "PRES": "Punch Press",
    "TASIMA": "Transport & Storage",
    "AKTARMA": "Conveyors",
    "TALAS TOPLAMA": "Swarf Extraction",
    "MONTAJ": "Assembly",
    "KAYNAK": "Welding",
    "CAPAK ALMA": "Corner Cleaning",
    "VIDALAMA": "Screwdriving",
}

def fix_name(isim):
    # "ACK 420 S - Up-Cutting Saw Machine" → "ACK 420 S"
    if ' - ' in isim:
        first = isim.split(' - ')[0].strip()
        if re.match(r'^[A-Z]{2,6}[\s\d]', first):
            return first
    return isim
```

Doğrulama:
```python
m = data[0]
assert m['brand'] == 'yilmaz'
assert m['categories'] == ['Aluminium', 'PVC'] or m['categories'] == ['Aluminium'] or m['categories'] == ['PVC']
assert 'en' in m['diller']
assert 'name' in m['diller']['en']
assert '-' not in m['diller']['en']['name'] or m['diller']['en']['name'].count('-') <= 1
```

---

## ADIM 2 — KategoriPage.astro'yu düzelt

Dosya: src/components/pages/KategoriPage.astro

### 2a. getStaticPaths — catName değerlerini JSON'a uygun yap:
```typescript
export async function getStaticPaths() {
  return [
    { params: { kategori: 'aluminyum' }, props: { catName: 'Aluminium', brand: 'yilmaz' } },
    { params: { kategori: 'pvc' },       props: { catName: 'PVC',        brand: 'yilmaz' } },
    { params: { kategori: 'gocmaksan' }, props: { catName: 'Gocmaksan',  brand: 'gocmaksan' } },
  ];
}
```

### 2b. Veri import — getStaticPaths'te async import kullan:
```typescript
export async function getStaticPaths() {
  const yilmaz = (await import('../../data/machines.json')).default;
  const gocmaksan = (await import('../../data/gocmaksan.json')).default;
  // ... paths
}
```

### 2c. Filtre mantığı — TÜM veriler için ortak:
```typescript
const filteredMachines = allMachines.filter((m: any) => {
  if (brand === 'gocmaksan') return m.brand === 'gocmaksan';
  const cats: string[] = m.categories || [];
  return cats.some((c: string) => c.toLowerCase() === catName.toLowerCase());
});
```

### 2d. subcat hesabı — marka'ya göre:
```typescript
const subcat = m.brand === 'gocmaksan'
  ? (m.category || '')      // gocmaksan: category field kullan
  : (m.subcategory || '');  // yilmaz: subcategory field kullan
```

### 2e. Resim ve isim — ortak fallback zinciri:
```typescript
const en = m.diller?.en || {};
const isim = en.name || en.isim || m.slug;
const resim = en.images?.[0] || en.resimler?.[0] || '/placeholder.png';
const aciklama = en.description || en.aciklama || '';
```

---

## ADIM 3 — MachinePage.astro'yu düzelt

Dosya: src/components/pages/MachinePage.astro

### 3a. activeLang — önce EN dene, TR fallback:
```typescript
const activeLang = machine.diller?.en || machine.diller?.tr || {};
const isim     = activeLang.name        || activeLang.isim        || machine.slug;
const aciklama = activeLang.description || activeLang.aciklama    || '';
const resimler = activeLang.images      || activeLang.resimler    || [];
const specs    = activeLang.specs       || activeLang.ozellik_gruplari || {};
```

### 3b. Badge — subcategory göster:
```typescript
{machine.subcategory && (
  <span class="text-xs font-bold uppercase tracking-wider px-2 py-1 rounded border border-gray-200 text-gray-500">
    {machine.subcategory}
  </span>
)}
```

---

## ADIM 4 — Test

```bash
npx astro dev
```

Kontrol edilecekler:
1. /tr/kategori/aluminyum → 56+ makine, isimler "ACK 420 S" formatında
2. /tr/kategori/pvc → 66+ makine, RESIMLER görünüyor (slug ismi değil)
3. /tr/kategori/gocmaksan → 47 makine, filtreler çalışıyor
4. /tr/machines/ack-420-s-up-cutting-saw-machine → Detay sayfası, resimler var
5. /tr/machines/bs-45 → Göçmaksan detay, resimler var

---

## VERİ YAPISI REFERANS (migrate sonrası her makine böyle olmalı)

### Yılmaz:
```json
{
  "slug": "ack-420-s-up-cutting-saw-machine",
  "brand": "yilmaz",
  "categories": ["Aluminium", "PVC"],
  "subcategory": "Cutting",
  "diller": {
    "en": {
      "name": "ACK 420 S",
      "description": "ACK 420 S is designed...",
      "images": ["/images/machines/ack-420-s-up-cutting-saw-machine-4.png"],
      "specs": { "STANDARD FEATURES": [...], "OPTIONAL FEATURES": [...] }
    }
  }
}
```

### Göçmaksan:
```json
{
  "slug": "bs-45",
  "brand": "gocmaksan",
  "category": "Bending Machines",
  "subcategory": "Standard",
  "diller": {
    "en": {
      "name": "BS 45",
      "description": "Manufactured with half a century...",
      "images": ["/images/gocmaksan/bs-45-1.jpg"],
      "specs": {}
    }
  }
}
```

---

## ADIM 5 — Bulgarca tercüme (Gemini quota sıfırlandıktan sonra)

```bash
python scripts/tercume_merkezi.py
```

API key: C:\Users\Kenan\Desktop\.ENVs\kuafor-backend\.env → GEMINI_API_KEY
Her makine için diller.bg eklenecek.
