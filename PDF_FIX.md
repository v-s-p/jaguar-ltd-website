# JAGUAR LTD — PDF + GÖÇMAKSAN VERİ FIX
# Claude Code'a ver: "Bu dosyayı oku ve adım adım uygula"

## SORUN 1 — Yılmaz PDF'leri online URL, lokal olmalı

Mevcut durum: machines.json'da catalog field'ı CDN URL'e işaret ediyor
Hedef: public/catalogs/yilmaz/ klasörüne indirilip lokal path kullanılmalı
Örnek: "catalog": "https://...yilmaz.../kd-350.pdf" → "catalog": "/catalogs/yilmaz/kd-350.pdf"

### Script: scripts/pdf_indir.py (yeni yaz)

```python
import requests, json, time, re
from pathlib import Path

JSON    = Path("src/data/machines.json")
PDF_DIR = Path("public/catalogs/yilmaz")
PDF_DIR.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.headers['User-Agent'] = 'Mozilla/5.0 Chrome/124'

with open(JSON) as f:
    data = json.load(f)

updated = 0
for m in data:
    en = m.get("diller", {}).get("en", {})
    cat_url = en.get("catalog")
    
    if not cat_url or not cat_url.startswith("http"):
        continue
    if en.get("catalog", "").startswith("/catalogs/"):
        continue  # Zaten lokal, atla
    
    # Dosya adı: slug bazlı
    filename = f"{m['slug']}.pdf"
    save_path = PDF_DIR / filename
    
    print(f"[{m['slug']}] indiriliyor...")
    time.sleep(0.5)
    
    try:
        r = session.get(cat_url, timeout=30)
        if r.status_code == 200 and b'%PDF' in r.content[:10]:
            save_path.write_bytes(r.content)
            en["catalog"] = f"/catalogs/yilmaz/{filename}"
            updated += 1
            print(f"  OK: {len(r.content)//1024}KB")
        else:
            print(f"  SKIP: HTTP {r.status_code}")
    except Exception as e:
        print(f"  HATA: {e}")

with open(JSON, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nTamamlandi: {updated} PDF lokal'e alindi")
```

Çalıştır:
```bash
cd C:\Users\Kenan\Desktop\AI\Jaguar-ltd
python scripts/pdf_indir.py
```

---

## SORUN 2 — Göçmaksan makinelerinde PDF yok

### Durum analizi
Göçmaksan sitesinde PDF ayrı bir alan — sayfa içinde küçük PDF ikonu/buton var.
Scraper bu PDF linkini çekmiyor çünkü Webflow sitesinde farklı bir DOM yapısı var.

Makine sayfası örneği: https://www.gocmaksan.com/eng/demir-tesisi-cozumleri/gms-sls-12
PDF linki sayfada: <a href="https://cdn.prod.website-files.com/.../gms-sls-12-otomatik-etriye-bukme-makinasi.pdf">PDF</a>

### Script: scripts/gocmaksan_pdf_enrich.py (yeni yaz)

```python
import requests, json, re, time
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin

JSON    = Path("src/data/gocmaksan.json")
PDF_DIR = Path("public/catalogs/gocmaksan")
PDF_DIR.mkdir(parents=True, exist_ok=True)

BASE = "https://www.gocmaksan.com"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 Chrome/124',
    'Referer': BASE,
})
session.get(f"{BASE}/eng", timeout=15)

with open(JSON) as f:
    data = json.load(f)

updated = 0
for i, m in enumerate(data):
    en = m.get("diller", {}).get("en", {})
    slug = m["slug"]
    
    # Zaten var mı?
    if en.get("catalog", "").startswith("/catalogs/"):
        print(f"[{slug}] zaten lokal, atla")
        continue
    
    # Makine sayfasını bul — gocmaksan.json'da orijinal URL var mı?
    # Varsa oradan al, yoksa slug'dan tahmin et
    page_url = en.get("source_url") or f"{BASE}/eng/{slug}"
    
    print(f"[{i+1}/{len(data)}] {slug}")
    time.sleep(1.5)
    
    r = session.get(page_url, timeout=30)
    if r.status_code != 200:
        print(f"  SKIP: HTTP {r.status_code}")
        continue
    
    soup = BeautifulSoup(r.content, 'html.parser')
    
    # PDF linkini bul
    pdf_url = None
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '.pdf' in href.lower():
            pdf_url = href if href.startswith('http') else urljoin(BASE, href)
            break
    
    if not pdf_url:
        print(f"  PDF bulunamadi")
        continue
    
    # İndir
    time.sleep(0.5)
    try:
        pr = session.get(pdf_url, timeout=30)
        if pr.status_code == 200 and len(pr.content) > 1000:
            filename = f"{slug}.pdf"
            (PDF_DIR / filename).write_bytes(pr.content)
            en["catalog"] = f"/catalogs/gocmaksan/{filename}"
            updated += 1
            print(f"  OK: {len(pr.content)//1024}KB → {filename}")
    except Exception as e:
        print(f"  HATA: {e}")

with open(JSON, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nTamamlandi: {updated} PDF lokal'e alindi")
```

Çalıştır:
```bash
python scripts/gocmaksan_pdf_enrich.py
```

---

## SORUN 3 — Göçmaksan makine verisi eksik (SLS 12 örneği)

### Sorun
SLS 12 sayfamızda sadece: isim + açıklama + 1 resim
Göçmaksan sitesinde: teknik tablo + özellik listesi + video + daha fazla resim

### Sebep
gocmaksan_guncelleyici.py parse_product() fonksiyonu:
- Webflow'un lazy-load JS render ettiği içeriği alamıyor
- Teknik tablo `<table>` DOM'da ama JS çalışmadan görünmüyor

### Çözüm: Göçmaksan için enrich scripti

scripts/gocmaksan_enrich.py — eksik verileri doldur

```python
# Her Göçmaksan makinesini ziyaret et, şunları çek:
# 1. Teknik tablo: soup.find('table') veya .technical-data div
# 2. Özellikler: bullet list'ler (h3+ul kombinasyonu)
# 3. Video: YouTube iframe src
# 4. Ek resimler: sayfa içindeki tüm makine görselleri

# Teknik tablo parse stratejisi:
# <table> → satır bazlı key:value
# Webflow widget → .cms-item içindeki span çiftleri
# Piktogram kutuları → .spec-icon + .spec-value kombinasyonu

# Features parse:
# h3 veya strong tag + ardından ul
# .feature-title + .feature-text kombinasyonu

# Video:
# iframe[src*="youtube"] veya a[href*="youtu.be"]
```

### Önemli not: Claude in Chrome daha iyi sonuç verir
Göçmaksan sitesi Webflow + JavaScript heavy
Python scraper statik HTML alıyor, JS render görmüyor
Claude in Chrome extension ile tarayıcıdan çekmek çok daha doğru

---

## ÇALIŞTIRILACAK SIRALAMA

```bash
cd C:\Users\Kenan\Desktop\AI\Jaguar-ltd

# 1. Yılmaz PDF'leri indir (önce)
python scripts/pdf_indir.py

# 2. Göçmaksan PDF'leri indir
python scripts/gocmaksan_pdf_enrich.py

# 3. Sonucu kontrol et
python -c "
import json
m = json.load(open('src/data/machines.json'))
g = json.load(open('src/data/gocmaksan.json'))
ym_pdf = sum(1 for x in m if x.get('diller',{}).get('en',{}).get('catalog','').startswith('/'))
gm_pdf = sum(1 for x in g if x.get('diller',{}).get('en',{}).get('catalog','').startswith('/'))
print(f'Yilmaz lokal PDF: {ym_pdf}/{len(m)}')
print(f'Gocmaksan lokal PDF: {gm_pdf}/{len(g)}')
"

# 4. Astro build test
npx astro build

# 5. Dev server
npx astro dev
```

---

## GELECEK SESSION İÇİN NOT

Göçmaksan teknik tablo ve detay verisi için:
Claude in Chrome browser agent kullan:
1. Her makine URL'sini aç (gocmaksan.com/eng/[slug])
2. Sayfanın tam render edilmiş DOM'unu oku
3. Teknik tablo, özellikler ve videoyu çek
4. gocmaksan.json'ı güncelle

Bu işlem otomatik script yerine browser agent ile çok daha güvenilir.
