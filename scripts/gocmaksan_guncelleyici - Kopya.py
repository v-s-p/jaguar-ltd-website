#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JAGUAR LTD - GOCMAKSAN GUNCELLEYICI v1.0
https://www.gocmaksan.com/eng -> gocmaksan.json

Format: machines.json ile ayni (brand: "gocmaksan")

Kullanim:
  python gocmaksan_guncelleyici.py          # Tum veriyi cek
  python gocmaksan_guncelleyici.py --images # Resimleri de indir
  python gocmaksan_guncelleyici.py --test   # Ilk 3 makine
"""
import sys, io, re, json, time, shutil, gzip
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime
import requests
from bs4 import BeautifulSoup

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE = "https://www.gocmaksan.com"

SCRIPT_DIR   = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
JSON_OUTPUT  = PROJECT_ROOT / "src" / "data" / "gocmaksan.json"
JSON_BACKUP  = PROJECT_ROOT / "src" / "data" / f"gocmaksan_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
IMG_DIR      = PROJECT_ROOT / "public" / "images" / "gocmaksan"

DELAY     = 1.5
MAX_RETRY = 3

# Kategori URL'leri -> (category, subcategory)
KATEGORI_MAP = {
    "/eng/bukme-makinalari":                                    ("Bending Machines", "Standard"),
    "/eng/portatif-bukme-makinalari":                           ("Bending Machines", "Portable"),
    "/eng/etriye-bukme-makinalari":                             ("Bending Machines", "Stirrup"),
    "/eng/spiral-bukme-makinalari":                             ("Bending Machines", "Spiral"),
    "/eng/filiz-demir-bukme-makinalari":                        ("Bending Machines", "Dowel Bar"),
    "/eng/kesme-makinalari":                                    ("Cutting Machines", "Standard"),
    "/eng/portatif-kesme-makinalari":                           ("Cutting Machines", "Portable"),
    "/eng/insaat-demiri-kesme-ve-bukme-kombine-makinalari":     ("Combined Machines", "Combined"),
    "/eng/hafif-insaat-makinalari":                             ("Light Construction", "Light Construction"),
    "/eng/demir-tesisi-cozumleri":                              ("Steel Factory Solutions", "Steel Factory"),
    "/eng/insaatci-el-aletleri":                                ("Hand Tools", "Hand Tools"),
}

VERBOSE = "--verbose" in sys.argv or "-v" in sys.argv

def log(msg, lvl="INFO"):
    icons = {"INFO":"[i]","OK":"[+]","WARN":"[!]","ERR":"[X]","SCAN":"[~]"}
    print(f"  {icons.get(lvl,'   ')} {msg}")

def vlog(msg):
    if VERBOSE: log(msg, "SCAN")

def build_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "identity",
        "Connection": "keep-alive",
    })
    try:
        vlog("Ana sayfa cookie aliniyor...")
        s.get(f"{BASE}/eng", timeout=15)
        time.sleep(0.5)
    except Exception:
        pass
    return s

def safe_get(session, url, retries=MAX_RETRY):
    session.headers["Referer"] = f"{BASE}/eng"
    for attempt in range(retries):
        try:
            r = session.get(url, timeout=30, allow_redirects=True)
            if r.status_code == 200:
                return r
            vlog(f"HTTP {r.status_code}: {url}")
            time.sleep(2 * (attempt + 1))
        except requests.RequestException as e:
            vlog(f"Hata: {e}")
            time.sleep(2)
    return None

def get_product_links(session, cat_url):
    """Kategori sayfasindan urun linklerini cek."""
    full_url = BASE + cat_url
    r = safe_get(session, full_url)
    if not r:
        log(f"Kategori alinamadi: {cat_url}", "WARN")
        return []

    soup = BeautifulSoup(r.content, 'html.parser')
    links = set()

    # Webflow - urun linkleri genellikle .w-dyn-item icinde
    for a in soup.find_all('a', href=True):
        href = a['href']
        # Urun linkleri: /eng/... formatinda ve kategori URL degil
        if href.startswith('/eng/') and href not in KATEGORI_MAP:
            # Kategori URL'lerini atla
            skip = any(href.startswith(k) for k in KATEGORI_MAP.keys())
            if not skip and len(href.split('/')) >= 3:
                links.add(href)

    vlog(f"  {cat_url}: {len(links)} link")
    return list(links)

def download_image(session, img_url, slug, index):
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    ext = Path(urlparse(img_url).path).suffix.lower()
    if ext not in ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg'):
        ext = '.jpg'
    if ext == '.svg':
        ext = '.png'

    filename  = f"{slug}-{index}{ext}"
    save_path = IMG_DIR / filename
    web_path  = f"/images/gocmaksan/{filename}"

    if save_path.exists() and save_path.stat().st_size > 1000:
        vlog(f"    Zaten mevcut: {filename}")
        return web_path

    r = safe_get(session, img_url)
    if r and len(r.content) > 500:
        save_path.write_bytes(r.content)
        vlog(f"    Indirildi: {filename} ({len(r.content)//1024}KB)")
        return web_path

    return img_url

def parse_product(session, href, category, subcategory, download_images):
    """Urun sayfasindan veri cek."""
    full_url = BASE + href
    slug = href.rstrip('/').split('/')[-1]

    r = safe_get(session, full_url)
    if not r:
        return None

    soup = BeautifulSoup(r.content, 'html.parser')

    # ISIM
    name = ""
    title_tag = soup.find('title')
    if title_tag:
        t = title_tag.get_text(strip=True)
        name = re.split(r'\s*[|\-]\s*(GMS|Gocmaksan|GOCMAKSAN)', t, flags=re.IGNORECASE)[0].strip()

    if not name:
        for h in ['h1', 'h2']:
            tag = soup.find(h)
            if tag:
                name = tag.get_text(strip=True)
                break

    if not name:
        name = slug.upper().replace('-', ' ')

    # ACIKLAMA
    description = ""
    skip_words = ['cookie', 'consent', 'subscribe', 'newsletter', 'javascript', 'loading']
    for p in soup.find_all('p'):
        t = p.get_text(strip=True)
        if len(t) > 50 and not any(x in t.lower() for x in skip_words):
            description = t
            break

    # RESIMLER
    images_raw = set()

    # Webflow CDN
    for img in soup.find_all('img'):
        for attr in ('src', 'data-src', 'srcset'):
            val = img.get(attr, '') or ''
            # Webflow assets
            if ('assets.website-files.com' in val or
                'uploads-ssl.webflow.com' in val or
                'cdn.prod.website-files.com' in val):
                if 'logo' not in val.lower() and 'icon' not in val.lower():
                    # srcset'ten ilk URL'yi al
                    url = val.split(',')[0].split(' ')[0].strip()
                    if url:
                        images_raw.add(url)

    # Ham HTML'de de ara
    for m_obj in re.finditer(
            r'https://[^\s"\'<>]+(?:website-files\.com|webflow\.com)[^\s"\'<>]+\.(?:jpg|jpeg|png|webp)',
            r.text):
        url = m_obj.group()
        if 'logo' not in url.lower() and 'icon' not in url.lower():
            images_raw.add(url)

    images_raw = sorted(images_raw)

    if download_images and images_raw:
        images = []
        for idx, img_url in enumerate(images_raw, 1):
            lokal = download_image(session, img_url, slug, idx)
            images.append(lokal)
            time.sleep(0.2)
    else:
        images = list(images_raw)

    # TEKNIK OZELLIKLER
    specs = {
        "STANDARD FEATURES": [],
        "OPTIONAL FEATURES": [],
        "TECHNICAL SPECS": [],
    }

    kw_map = {
        "STANDARD": "STANDARD FEATURES",
        "OPTIONAL":  "OPTIONAL FEATURES",
        "TECHNICAL": "TECHNICAL SPECS",
        "SPECS":     "TECHNICAL SPECS",
        "FEATURES":  "STANDARD FEATURES",
    }

    for hx in soup.find_all(['h2','h3','h4']):
        baslik = hx.get_text(strip=True).upper()
        grup = next((v for k, v in kw_map.items() if k in baslik), None)
        if not grup:
            continue
        ul = hx.find_next_sibling('ul')
        if ul:
            items = [li.get_text(strip=True) for li in ul.find_all('li') if li.get_text(strip=True)]
            specs[grup].extend(items)

    return {
        "slug":        slug,
        "brand":       "gocmaksan",
        "category":    category,
        "subcategory": subcategory,
        "diller": {
            "en": {
                "name":        name,
                "description": description,
                "images":      images,
                "specs":       specs,
            }
        }
    }

def main():
    print()
    print("=" * 64)
    print("  GOCMAKSAN GUNCELLEYICI v1.0")
    print("  gocmaksan.com/eng -> gocmaksan.json")
    print("=" * 64)
    print()

    test_mode       = "--test"   in sys.argv
    download_images = "--images" in sys.argv

    if test_mode:       log("TEST MODU - Ilk 3 urun", "WARN")
    if download_images: log("Resimler indirilecek", "WARN")

    session = build_session()
    log("Session hazir", "OK")

    # Tum urun linklerini topla
    log("=== KATEGORI TARAMASI ===", "SCAN")
    tum_urunler = {}  # href -> (category, subcategory)

    for cat_path, (category, subcategory) in KATEGORI_MAP.items():
        time.sleep(DELAY * 0.5)
        links = get_product_links(session, cat_path)
        for link in links:
            if link not in tum_urunler:
                tum_urunler[link] = (category, subcategory)

    log(f"Toplam {len(tum_urunler)} benzersiz urun", "OK")

    if not tum_urunler:
        log("Hic urun bulunamadi!", "ERR")
        sys.exit(1)

    items = list(tum_urunler.items())
    if test_mode:
        items = items[:3]

    # Parse
    log(f"=== {len(items)} URUN ISLENIYOR ===", "SCAN")
    makineler = []
    hatali = 0

    for i, (href, (category, subcategory)) in enumerate(items, 1):
        slug = href.rstrip('/').split('/')[-1]
        log(f"[{i}/{len(items)}] {slug}")
        time.sleep(DELAY)

        m = parse_product(session, href, category, subcategory, download_images)
        if m:
            makineler.append(m)
            r_sayi = len(m['diller']['en']['images'])
            vlog(f"  -> {m['diller']['en']['name']} | {r_sayi} resim | {m['category']}")
        else:
            hatali += 1

    makineler.sort(key=lambda m: m['slug'])

    if JSON_OUTPUT.exists():
        shutil.copy2(JSON_OUTPUT, JSON_BACKUP)
        log(f"Yedeklendi -> {JSON_BACKUP.name}", "OK")

    JSON_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(makineler, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 64)
    print(f"  TAMAMLANDI")
    print(f"  Toplam : {len(makineler)}")
    print(f"  Hatali : {hatali}")
    print("=" * 64)

    from collections import Counter
    kat_sayac = Counter(f"{m['category']} / {m['subcategory']}" for m in makineler)
    print("\n  Kategori dagilimi:")
    for k, v in sorted(kat_sayac.items(), key=lambda x: -x[1]):
        print(f"    {k:<40} {v:>3}")

    print(f"\n  Sonraki: Astro sayfalarini guncelle")
    print()

if __name__ == "__main__":
    main()
