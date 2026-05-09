# JAGUAR LTD — TEKNİK TABLO + PDF KATALOG FIX
# Claude Code'a ver: "Bu dosyayı oku ve uygula"

## SORUN
machines.json'da iki eksiklik:
1. Teknik spesifikasyon tablosu (boyut, voltaj, motor, ağırlık) — hiç çekilmemiş
2. PDF katalog linki — hiç çekilmemiş

Yılmaz ürün sayfasında bunlar var:
- Teknik tablo: sayfa alt kısmındaki ikonlu kutular
- PDF: "Katalog Sayfası" butonu

## ADIM 1 — Scraper'ı güncelle

Dosya: scripts/yilmaz_guncelleyici.py
Fonksiyon: parse_page() içine şunları ekle

### 1a. Teknik tablo parse (yilmaz_guncelleyici.py > parse_page):

```python
# TEKNİK TABLO - sayfa alt kismindaki specs tablosu
teknik_tablo = {}

# Yontem 1: <table> tag icinde
for table in soup.find_all('table'):
    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all(['td', 'th'])
        if len(cells) >= 2:
            key = cells[0].get_text(strip=True)
            val = cells[1].get_text(strip=True)
            if key and val and len(key) < 50:
                teknik_tablo[key] = val

# Yontem 2: .technical-data veya benzeri div'ler
for div in soup.find_all('div', class_=re.compile(r'technical|spec|data|table', re.I)):
    items = div.find_all(['dt', 'dd', 'li', 'span'])
    for i in range(0, len(items)-1, 2):
        key = items[i].get_text(strip=True)
        val = items[i+1].get_text(strip=True) if i+1 < len(items) else ''
        if key and val and len(key) < 50 and len(val) < 100:
            teknik_tablo[key] = val

# Yontem 3: Ikon + deger kombinasyonlari (Yilmaz sitesi ozel)
# <div class="..."> <img/> <span>deger</span> <p>birim</p> </div>
for container in soup.find_all('div'):
    img = container.find('img')
    spans = container.find_all(['span', 'p', 'div'], recursive=False)
    if img and len(spans) >= 2:
        deger = spans[0].get_text(strip=True) if spans else ''
        birim = spans[1].get_text(strip=True) if len(spans) > 1 else ''
        alt = img.get('alt', '') or img.get('title', '') or img.get('src', '').split('/')[-1].split('.')[0]
        if deger and alt and len(deger) < 30:
            teknik_tablo[alt] = f"{deger} {birim}".strip()
```

### 1b. PDF katalog link parse:

```python
# PDF KATALOG
katalog_url = None

# Yontem 1: "katalog" veya "catalog" iceren a[href] PDF
for a in soup.find_all('a', href=True):
    href = a['href']
    text = a.get_text(strip=True).lower()
    if href.endswith('.pdf') or 'katalog' in text.lower() or 'catalog' in text.lower():
        katalog_url = urljoin(BASE, href) if href.startswith('/') else href
        break

# Yontem 2: PDF butonu
for a in soup.find_all('a', href=True):
    href = a['href']
    if '.pdf' in href.lower():
        katalog_url = urljoin(BASE, href) if href.startswith('/') else href
        break
```

### 1c. Return dict'e ekle:

```python
return {
    "slug": en_slug,
    "brand": "yilmaz",
    "categories": kategoriler,
    "subcategory": alt_kategoriler[0] if alt_kategoriler else "Other",
    "diller": {
        "en": {
            "name": isim,
            "description": aciklama,
            "images": resimler,
            "specs": ozellik_gruplari,
            "technical_data": teknik_tablo,  # YENİ
            "catalog": katalog_url,           # YENİ
        }
    }
}
```

## ADIM 2 — Sadece eksik verileri geri doldur (--enrich modu)

Mevcut machines.json'daki her makine için Yılmaz sayfasını aç,
sadece teknik tablo ve PDF linkini çek, ekle.

```python
# scripts/enrich_machines.py - yeni script yaz

import requests, json, re, time
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin

BASE = "https://www.yilmazmachine.com.tr"
JSON = Path("src/data/machines.json")

def fetch_page(session, slug):
    url = f"{BASE}/en/products/{slug}/"
    r = session.get(url, timeout=30)
    return r if r.status_code == 200 else None

def extract_technical_data(soup):
    """Teknik tablo verilerini cek."""
    data = {}
    # ... (yukarıdaki yöntemler)
    return data

def extract_catalog(soup, base_url):
    """PDF katalog linkini bul."""
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True).lower()
        if '.pdf' in href.lower() or 'katalog' in text:
            return urljoin(base_url, href)
    return None

def main():
    session = requests.Session()
    session.headers['User-Agent'] = 'Mozilla/5.0 Chrome/124'
    
    # Ana sayfadan cookie al
    session.get(f"{BASE}/en/", timeout=15)
    
    with open(JSON) as f:
        machines = json.load(f)
    
    updated = 0
    for i, m in enumerate(machines):
        en = m.get("diller", {}).get("en", {})
        
        # Zaten var mi?
        if en.get("technical_data") and en.get("catalog"):
            continue
        
        print(f"[{i+1}/{len(machines)}] {m['slug']}")
        time.sleep(1.5)
        
        r = fetch_page(session, m['slug'])
        if not r:
            print(f"  SKIP: 403/timeout")
            continue
        
        soup = BeautifulSoup(r.content, 'html.parser')
        
        if not en.get("technical_data"):
            tech = extract_technical_data(soup)
            if tech:
                m["diller"]["en"]["technical_data"] = tech
                updated += 1
                print(f"  + teknik tablo: {len(tech)} alan")
        
        if not en.get("catalog"):
            cat = extract_catalog(soup, f"{BASE}/en/products/{m['slug']}/")
            if cat:
                m["diller"]["en"]["catalog"] = cat
                updated += 1
                print(f"  + katalog: {cat[-50:]}")
    
    with open(JSON, 'w') as f:
        json.dump(machines, f, ensure_ascii=False, indent=2)
    
    print(f"\nGuncellendi: {updated} alan")

if __name__ == "__main__":
    main()
```

## ADIM 3 — MachinePage.astro'da göster

Dosya: src/components/pages/MachinePage.astro

### 3a. Teknik tablo gösterimi ekle (specs bölümünden önce):

```astro
{/* TEKNİK VERİ TABLOSU */}
{Object.keys(teknikTablo).length > 0 && (
  <div class="mt-12 bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
    <h3 class="text-2xl font-extrabold text-gray-900 mb-6">
      {t('machine.technical_data') || 'Технически данни'}
    </h3>
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
      {Object.entries(teknikTablo).map(([key, val]) => (
        <div class="bg-gray-50 border border-gray-200 rounded-xl p-4 text-center">
          <div class="text-lg font-extrabold text-gray-900">{val}</div>
          <div class="text-xs text-gray-400 font-bold uppercase tracking-wider mt-1">
            {key.replace(/_/g, ' ')}
          </div>
        </div>
      ))}
    </div>
  </div>
)}
```

### 3b. teknikTablo değişkenini frontmatter'a ekle:
```typescript
const teknikTablo = activeLang.technical_data || {};
```

### 3c. PDF katalog butonu — mevcut katalog bölümüne zaten var, catalog field'ı doldurulunca otomatik çıkacak.

## ADIM 4 — Test

```bash
# 1. Enrich scripti çalıştır
cd scripts
python enrich_machines.py

# 2. Sonucu kontrol et
python -c "
import json
m = json.load(open('../src/data/machines.json'))
has_tech = sum(1 for x in m if x.get('diller',{}).get('en',{}).get('technical_data'))
has_cat = sum(1 for x in m if x.get('diller',{}).get('en',{}).get('catalog'))
print(f'Teknik tablo: {has_tech}/{len(m)}')
print(f'Katalog: {has_cat}/{len(m)}')
"

# 3. Dev server test
npx astro dev
# http://localhost:4321/tr/machines/cdc-600-compound-angle-double-head-saw-cutting-machine
# → Teknik tablo kutuları görünüyor mu?
# → PDF butonu var mı?
```

## NOT
- Yılmaz sitesi Python'u 403 ile blokluyor olabilir
- Eğer enrich_machines.py 403 alıyorsa, Claude in Chrome browser agent kullan
- Göçmaksan için teknik tablo zaten ayrı format (HTML table), o ayrı bir görev

## ÖNCE TEMELİ DÜZELT
Bu görevden önce CLAUDE_MASTER.md'deki Adım 1-4'ü (migrate + page fix) tamamla!
Temel düzgün çalışmadan bu ekleme yapma.
