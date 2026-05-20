# Handoff - 2026-05-20

## Konu
Jaguar-ltd icin Gocmaksan PDF-first staging artefaktlarinin production JSON'a ve galeriye entegre edilmesi.

Odak:
- `pdf_extraction/gocmaksan/text/{slug}.md` staging markdown'larini `src/data/gocmaksan.json` icine kontrollu merge etmek
- PDF extraction gorsellerini duplicate/hash kontrolu ile `public/images/gocmaksan/` galerisine append etmek
- Mevcut image path'lerini, kategori/meta alanlarini ve PDF'siz makinelerde mevcut JSON'u korumak
- Tek commit + tek push ile `origin/main` yayinlamak

Bu dosya bir sonraki session'da Codex/Claude icin baslangic notu olarak kullanilsin.

---

## 1. Bu session oncesi bilinen durum

- `src/data/gocmaksan.json` icinde `47` makine vardi
- Dunku PDF-first extraction pass sonucunda `pdf_extraction/gocmaksan/text/` altinda `47` staging markdown vardi
- Bu staging markdown'larda kritik format bulgusu:
  - `detected technical tables` cogunlukla bos
  - `capacities / apparatus / feature bullets` cogunlukla bos
  - asil veri `raw intro/body text` icinde duz satir olarak duruyor
- Family PDF'lerde ayni PDF birden fazla makineye bagliydi:
  - ornek: B 26 / B 36 / B 45x1 / B 50
  - ornek: HB 12x3 / HB 12x6 / MH 8C
- PDF'siz kalan 8 slug icin staging bos veya unresolved durumdaydi

Kapsam disi tutulanlar:
- Gocmaksan scraper ana akis refactor'u
- Yilmaz PDF katalog extraction
- UI/product page component degisikligi
- backup JSON dosyasini commit'e almak

---

## 2. Bu session'da yapilanlar

### 2.1 Staging format analizi

Ilk incelenen 3 ornek:
- `pdf_extraction/gocmaksan/text/gms-b-45x1-gocmaksan-insaat-demiri-bukme-makinasi.md`
- `pdf_extraction/gocmaksan/text/gms-hb-12x6-gocmaksan-hasir-demir-bukme-makinasi.md`
- `pdf_extraction/gocmaksan/text/gms-kompaktor.md`

Sonuc:
- B 45x1 ve HB 12x6 icin model-spesifik satirlar `raw intro/body text` icinde mevcut
- `gms-kompaktor` PDF'siz; sadece ambiguity note var
- Parser sadece named section'lara bakarsa veri kacirir
- Parser raw text fallback ile model adini bulup sadece hedef model satirini parse etmeli

### 2.2 Parser script yazildi

Yeni dosya:
- `scripts/gocmaksan_staging_to_json.py`

Ana davranis:
- `pdf_extraction/gocmaksan/text/*.md` okur
- Once named section'lara bakar
- Bos ise `raw intro/body text` icine duser
- Slug / `machine context` / JSON `diller.en.name` uzerinden model varyantlarini uretir
- Raw text icinde hedef model satirini arar
- Model satirindan:
  - `TECHNICAL DATA`
  - `FEATURED FEATURES`
  - `CAPACITIES`
  cikarir
- Staging bos ise mevcut JSON'u korur
- Yalniz su alanlara dokunur:
  - `diller.en.description`
  - `specs.TECHNICAL DATA`
  - `specs.FEATURED FEATURES`
  - `specs.CAPACITIES`
  - `diller.en.images` sadece image merge modunda append edilir

Dokunulmayan alanlar:
- `slug`
- `brand`
- `categories`
- `subcategory`
- `pdf_catalog`
- `related_products`
- mevcut image path'leri

### 2.3 Dry-run raporu

Komut:
```powershell
py -3 scripts/gocmaksan_staging_to_json.py --dry-run
```

Sonuc:
- `Staging markdown count: 47`
- `JSON machine count: 47`
- `description filled from staging: 36/47`
- `TECHNICAL DATA filled from staging: 31/47`
- `FEATURED FEATURES filled from staging: 36/47`
- `CAPACITIES filled from staging: 31/47`

Staging'den bos kalan 8 slug:
- `gms-ayarli-kosebentler-gocmaksan`
- `gms-demirci-anahtarlari-gocmaksan`
- `gms-el-makaslari-gocmaksan`
- `gms-etriye-kollari-gocmaksan`
- `gms-kalip-sokmeler-gocmaksan`
- `gms-kompaktor`
- `gms-oturak-makaslari-gocmaksan`
- `gms-rl-2000-gocmaksan-cift-tamburlu-silindir`

Not:
- Bu 8 slug icin mevcut JSON korunacak sekilde davranildi

### 2.4 JSON backup alindi

Backup:
- `src/data/gocmaksan_backup_BEFORE_PDF_MERGE_20260520.json`

Durum:
- backup dosyasi untracked birakildi
- commit'e alinmadi

### 2.5 JSON gercek yazildi

Komut:
```powershell
py -3 scripts/gocmaksan_staging_to_json.py
```

Kritik dogrulama:
- B 45x1 description artik model-spesifik:
  - `B 45x1 is a rebar bending machine with model-specific PDF data...`
- HB 12x6 description artik Steel Factory / mesh baglaminda:
  - `HB 12x6 is a mesh bending and cutting machine with model-specific PDF data for steel factory use...`

Ornek B 45x1 teknik duzeltme:
- `Weight kg`: `390 -> 392`
- kaynak: raw PDF model satiri

Ornek HB 12x6 teknik veri:
- `W-L-H cm`: `100 x 640 x 109`
- `Engine Power kW`: `7.5`
- `Voltage V`: `380`
- `Weight kg`: `1250`
- `Hydraulic Oil Tank Capacity lt`: `36`
- capacities:
  - `45 kg/mm2: Ø 12x1`
  - `65 kg/mm2: Ø 10x1`
  - `85 kg/mm2: Ø 8x1`

---

## 3. PDF resimleri galeriye entegre edildi

Kaynak:
- `pdf_extraction/gocmaksan/images/{slug}/`

Hedef:
- `public/images/gocmaksan/`

Script modu:
```powershell
py -3 scripts/gocmaksan_staging_to_json.py --merge-images
```

Davranis:
- Her PDF image icin MD5 hash hesaplandi
- Mevcut `public/images/gocmaksan/` dosyalariyla hash duplicate kontrolu yapildi
- Dosya boyutu `< 5KB` ise atlanacak sekilde filtre kondu
- Duplicate olmayan gorseller public galeriye kopyalandi
- JSON `diller.en.images` listelerine sadece append yapildi
- Mevcut image path'leri silinmedi

Filename standardi:
- SEO-friendly, lowercase
- format: `{english-machine-name-slug}_{index}.{ext}`
- ornek:
  - `axis-50s_2.png`
  - `hb-12x3_2.png`
  - `sls-12_40.png`
  - `synclone-45s_11.png`

Image merge raporu:
- `Toplam yeni resim eklenen: 209`
- `Duplicate atlanan: 187`
- `Boyut filtresi ile atlanan: 0`
- `Makine basina ortalama resim sayisi: 5.45`
- `Hala tek resimli makine sayisi: 27`
- `Image source dir bulunmayan slug: 0`

Guncel galeri sayisi:
- `public/images/gocmaksan` toplam dosya: `256`
- JSON image path toplam: `256`
- JSON makine sayisi: `47`

Yeni resim eklenen baslica sluglar:
- `gms-axis-50s-gocmaksan-spiral-demir-bukme-makinasi`: 9
- `gms-b-26-gocmaksan-insaat-demiri-bukme-makinasi`: 9
- `gms-bt-24x5-gocmaksan-portatif-insaat-demiri-bukme-makinasi`: 17
- `gms-h-36-s-gocmaksan-insaat-demiri-kesme-makinasi`: 16
- `gms-matrix-55s-gocmaksan-demir-kesme-hatti`: 24
- `gms-sls-12-gocmaksan-otomatik-etriye-bukme-makinasi`: 39
- `gms-synclone-45s-gocmaksan-demir-bukme-hatti`: 10

---

## 4. Commit ve push

Staged kapsam:
- `scripts/gocmaksan_staging_to_json.py`
- `src/data/gocmaksan.json`
- `public/images/gocmaksan/`

Commit:
```text
3c3cf24 feat: gocmaksan PDF-first data merge (description+specs+images from 39 PDF)
```

Push:
```text
1228923..3c3cf24 main -> main
```

Remote:
```text
https://github.com/v-s-p/jaguar-ltd-website.git
```

Not:
- Ilk push sandbox/network sebebiyle `github.com:443 via 127.0.0.1` baglanamadi
- izinli tekrar calistirilinca push basarili oldu

---

## 5. English copy cleanup sprint

PDF-first merge sonrasinda Gocmaksan English copy alanlarinda kalite sorunu tespit edildi:
- Turkce/English mixed heading sızıntısı
- katalog basliklarinin description/feature olarak gelmesi
- `S I N C E`, `www`, teknik tablo satirlari ve `Ø ...` kapasite kirintilarinin feature olmasi
- `model-specific PDF data` gibi ic surec dilinin product description'a yansimasi

Yeni script:
- `scripts/gocmaksan_english_copy_cleanup.py`

Davranis:
- yalniz `diller.en.name`, `diller.en.description`, `specs.FEATURED FEATURES` alanlarini temizler
- `TECHNICAL DATA`, `CAPACITIES`, `images`, kategori/meta ve related alanlara dokunmaz
- family bazli, normal sentence-case English copy uretir
- hand-tool gibi feature gerektirmeyen alanlarda mevcut yapilari zorla sisirmez

Backup:
- `src/data/gocmaksan_backup_BEFORE_EN_COPY_CLEANUP_20260520.json`
- untracked birakildi, commit'e alinmadi

Dry-run / apply sonucu:
- `machine count: 47`
- `descriptions changed: 47`
- `feature lists changed: 41`
- `feature keys removed: 0`
- `names changed: 6`
- cleanup once suspicious:
  - `suspicious_descriptions: 33`
  - `suspicious_feature_lists: 4`
- cleanup sonrasi suspicious:
  - `suspicious_descriptions: 0`
  - `suspicious_feature_lists: 0`

Ornek duzeltilen copy:
- `H 38S is a hydraulic rebar cutting machine for construction-site steel processing.`
- `Power 24 is a portable hydraulic rebar cutting machine for construction-site use.`
- `B 45x1 is a rebar bending machine for construction-site steel processing.`
- `HB 12x6 is a mesh bending and cutting machine for steel factory applications.`
- `SLS 12 is an automatic stirrup bending machine for steel factory production.`

Alan siniri dogrulandi:
- unexpected non-copy field diffs: `0`
- yani technical data, capacities, images ve meta alanlar degismedi

Validation:
- `npm run build` ilk sandbox denemesinde `spawn EPERM` ile dustu
- izinli tekrar calistirildi ve basarili oldu
- build sonucu: `1136 page(s) built`
- sadece mevcut route warning'i goruldu:
  - `/kategori/gocmaksan` route conflict warning

---

## 6. Bu session sonunda git durumu

Commit sonrasi bizim publish kapsamimiz temiz:
- `scripts/gocmaksan_staging_to_json.py` tracked ve pushlandi
- `src/data/gocmaksan.json` tracked ve pushlandi
- yeni `public/images/gocmaksan/` gorselleri tracked ve pushlandi

Hala mevcut, bu commit disi degisiklikler:
- `M scripts/requirements.txt`
- `?? pdf_extraction/`
- `?? public/catalogs/gocmaksan/gms-bs-36-gocmaksan-insaat-demiri-bukme-makinasi.pdf`
- `?? public/catalogs/gocmaksan/gms-bs-45-gocmaksan-insaat-demiri-bukme-makinasi-sy0wu.pdf`
- `?? public/catalogs/gocmaksan/gms-bs-50-gocmaksan-insaat-demiri-bukme-makinasi.pdf`
- `?? public/catalogs/gocmaksan/gms-bs-60-gocmaksan-insaat-demiri-bukme-makinasi.pdf`
- `?? public/catalogs/yilmaz/`
- `?? scripts/gocmaksan_missing_pdf_fetch.py`
- `?? scripts/gocmaksan_pdf_extraction.py`
- `?? src/data/gocmaksan_backup_BEFORE_PDF_MERGE_20260520.json`
- eski backup dosyalari:
  - `src/data/machines_backup_20260516_1934.json`
  - `src/data/machines_backup_20260516_1946.json`
  - `src/data/yilmaz_backup_BEFORE_IMG_REBUILD_20260516_2013.json`

Onemli:
- `src/data/gocmaksan_backup_BEFORE_PDF_MERGE_20260520.json` bilerek commit'e alinmadi
- `pdf_extraction/` staging artefaktlari da bu commit'e alinmadi

---

## 7. Bilinen riskler / dikkat noktasi

### 7.1 Family-shared feature notlari

Bir cok family PDF icin feature'lar family-shared olarak raporlandi.

Bu kabul edilebilir cunku:
- model-spesifik teknik satir ayrildi
- feature metni zaten family/product-series seviyesinde
- parser raporda family-shared notunu koruyor

### 7.2 Model-specific row bulunamayanlar

Dry-run notlarinda model-specific row bulunamayan sluglar:
- `gms-mg-26-junior-portatif-bukme-makinasi`
- `gms-sh-60-gocmaksan-insaat-demiri-kesme-makinasi`

Bu sluglarda mevcut JSON verisi tamamen silinmedi; staging dolu alan varsa merge edildi, bos alanlar korundu.

### 7.3 Description kalitesi

Description politikasi:
- PDF raw prose varsa onu kullan
- yoksa family/title context'ten model-spesifik teknik-safe description uret
- eski yanlis kopya description'i ancak daha iyi staging-derived alternatif varsa degistir

Bu nedenle B 45x1 ve HB 12x6 gibi kritik yanlis description'lar duzeldi.

### 7.4 Image filename notu

Yeni image filename'leri JSON'daki English machine name uzerinden turetildi.
Bu istenen Yilmaz standardina uygun: `{slug}_{index}.{ext}`.

Ancak slug burada product URL slug'i degil, English name slug'i:
- `axis-50s_2.png`
- `power-trowel_2.png`
- `sls-12_2.png`

Bu bilincli uygulandi.

---

## 8. Sonraki session icin net baslangic plani

### Asama A - Build / smoke test

Commit pushlandi ama bu session'da full Astro build calistirilmadi.

Ilk onerilen kontrol:
```powershell
npm run build
```

Beklenen:
- route/page generation sorunsuz olmali
- image path'leri public altinda mevcut oldugu icin runtime'da kirik gorsel olmamali

### Asama B - Product-level spot check

Kontrol edilecek sayfalar:
- B 45x1
- HB 12x6
- SLS 12
- Axis 50S
- Matrix 55S

Kontrol basliklari:
- description dogru mu
- technical data gorunuyor mu
- capacities gorunuyor mu
- galeri yeni resimleri listeliyor mu
- tek-resimli kalan makineler beklenen PDF'siz/duplicate durumlar mi

### Asama C - Staging artefaktlarini commit stratejisi

Hala untracked duran PDF-first extractor/staging tarafinda karar ver:

Secenek 1:
- extractor scriptlerini ve staging artefaktlarini ayri commit ile takip altina al

Secenek 2:
- staging artefaktlarini repo disi/ignored operasyonel cikti olarak tut

Secenek 3:
- sadece extractor scriptlerini commit'le, `pdf_extraction/` artefaktlarini ignore et

Pratik tavsiye:
- Once build ve product spot check
- Sonra staging artefaktlarini nasil saklayacagina karar ver

### Asama D - Yilmaz PDF hattina don

Onceki handoff'tan kalan mantikli sonraki is:
- `public/catalogs/yilmaz/ALUMINIUM-KATALOG.pdf`
- `public/catalogs/yilmaz/PVC-KATALOG.pdf`
- `public/catalogs/yilmaz/makine-Kiyaslama-tablolari.pdf`

Hedef:
- Yilmaz icin family-catalog PDF-first staging akisini tasarlamak
- model bazli section ayirici ve comparison table potansiyelini test etmek

---

## 9. Hizli komutlar

Son commit:
```powershell
git log -1 --oneline
```

Gocmaksan JSON parse ve image count:
```powershell
$data = Get-Content -Raw src/data/gocmaksan.json | ConvertFrom-Json
$counts = $data | ForEach-Object { $_.diller.en.images.Count }
[pscustomobject]@{
  machines = $data.Count
  totalImages = ($counts | Measure-Object -Sum).Sum
  avgImages = [math]::Round(($counts | Measure-Object -Average).Average, 2)
  singleImageMachines = ($counts | Where-Object { $_ -eq 1 } | Measure-Object).Count
}
```

Critical description check:
```powershell
$data = Get-Content -Raw src/data/gocmaksan.json | ConvertFrom-Json
'gms-b-45x1-gocmaksan-insaat-demiri-bukme-makinasi',
'gms-hb-12x6-gocmaksan-hasir-demir-bukme-makinasi' |
  ForEach-Object {
    $m = $data | Where-Object slug -eq $_
    [pscustomobject]@{
      slug = $_
      name = $m.diller.en.name
      image_count = $m.diller.en.images.Count
      description = $m.diller.en.description
    }
  }
```

Parser dry-run:
```powershell
py -3 scripts/gocmaksan_staging_to_json.py --dry-run
```

Re-run JSON + image merge, only if intentionally regenerating:
```powershell
py -3 scripts/gocmaksan_staging_to_json.py --merge-images
```

Build check:
```powershell
npm run build
```

---

## 10. Kisa karar ozeti

- Gocmaksan PDF-first staging production JSON'a entegre edildi
- `36/47` description staging'den doldu
- `31/47` technical data staging'den doldu
- `36/47` featured features staging'den doldu
- `31/47` capacities staging'den doldu
- PDF'siz/bos kalan `8` slug korunarak gecildi
- `209` yeni PDF image duplicate filtreli sekilde galeriye eklendi
- `187` duplicate image atlandi
- Gocmaksan public galeri toplam `256` dosyaya cikti
- Commit `3c3cf24` pushlandi
- Backup JSON ve staging artefaktlari commit disi birakildi
- English copy cleanup ile description/features alanlari temizlendi
- Cleanup sonrasi `npm run build` basarili: `1136 page(s) built`
