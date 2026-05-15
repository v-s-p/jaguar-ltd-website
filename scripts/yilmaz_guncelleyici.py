#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YILMAZ MAKINE - JAGUAR LTD ENVANTER GUNCELLEYICI v4.2
Type-sayfasi tabanli, EN slug bazli + BLACKLIST (Hafizada Temizlik)
"""

import sys, io, hashlib
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

import requests
from bs4 import BeautifulSoup
import json, re, time, shutil
from pathlib import Path
from urllib.parse import urlparse, urljoin
from datetime import datetime

# ===================================================
# KONFIG & YOLLAR
# ===================================================
BASE     = "https://www.yilmazmachine.com.tr"

SCRIPT_DIR    = Path(__file__).parent
PROJECT_ROOT  = SCRIPT_DIR.parent
JSON_OUTPUT   = PROJECT_ROOT / "src" / "data" / "yilmaz.json"
JSON_BACKUP   = PROJECT_ROOT / "src" / "data" / f"machines_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
ERROR_OUTPUT  = PROJECT_ROOT / "src" / "data" / "machines_errors.txt"
IMG_DIR       = PROJECT_ROOT / "public" / "images" / "machines"
BLACKLIST_DIR = SCRIPT_DIR / "blacklist"

DELAY     = 1.5
MAX_RETRY = 3
BAD_HASHES = set()

SKIP_URLS = [
    "https://www.yilmazmachine.com.tr/en/product-category/vacuum-swarf-extractor-en-2/",
]

KATEGORI_AGACI = {
    "Aluminium": {
        "Processing Centers": [
            ("Profile Machining and Cutting Center", "https://www.yilmazmachine.com.tr/en/product-category/profile-machining-and-cutting-center/"),
            ("Sheet Plate Machining Center", "https://www.yilmazmachine.com.tr/en/product-category/sheet-plate-machining-center/"),
        ],
        "Saw Cutting": [
            ("Double Head Cutting", "https://www.yilmazmachine.com.tr/en/product-category/double-head-cutting/"),
            ("Radial Cutting", "https://www.yilmazmachine.com.tr/en/product-category/radial-cutting-2/"),
            ("Single Head Cutting", "https://www.yilmazmachine.com.tr/en/product-category/single-head-cutting/"),
            ("Slicing Machine", "https://www.yilmazmachine.com.tr/en/product-category/slicing-machine/"),
            ("V Cutting", "https://www.yilmazmachine.com.tr/en/product-category/v-cutting/"),
            ("Portable Cutting", "https://www.yilmazmachine.com.tr/en/product-category/portable-cutting/"),
        ],
        "Milling": [
            ("Numerical Controlled NC Router", "https://www.yilmazmachine.com.tr/en/product-category/numerical-controlled-nc-router/"),
            ("Portable Copy Router", "https://www.yilmazmachine.com.tr/en/product-category/portable-copy-router-en-2/"),
            ("Template Copy Router", "https://www.yilmazmachine.com.tr/en/product-category/template-copy-router/"),
        ],
        "Corner Crimping": [
            ("CNC Automatic Corner Crimping", "https://www.yilmazmachine.com.tr/en/product-category/cnc-automatic-corner-crimping/"),
            ("Hydraulic Corner Crimping", "https://www.yilmazmachine.com.tr/en/product-category/hydrolic-corner-crimping/"),
            ("Pneumatic Corner Crimping", "https://www.yilmazmachine.com.tr/en/product-category/pneumatic-corner-crimping/"),
        ],
        "End Milling": [
            ("Semi Automatic End Milling", "https://www.yilmazmachine.com.tr/en/product-category/semi-automatic-end-milling/"),
            ("Portable End Milling", "https://www.yilmazmachine.com.tr/en/product-category/portable-end-milling/"),
            ("Facade Notching Saw", "https://www.yilmazmachine.com.tr/en/product-category/facade-notching-saw/"),
        ],
        "Pressing": [
            ("Manual Punch Press", "https://www.yilmazmachine.com.tr/en/product-category/manual-punch-press/"),
        ],
        "Transferring": [
            ("Trolley", "https://www.yilmazmachine.com.tr/en/product-category/trolley/"),
        ],
        "Conveying": [
            ("Conveyors", "https://www.yilmazmachine.com.tr/en/product-category/conveyors/"),
        ],
        "Swarf Extraction": [
            ("Vacuum Swarf Extractor", "https://www.yilmazmachine.com.tr/en/product-category/vacuum-swarf-extractor-en/"),
        ],
        "Assembling": [
            ("Sash Assembly Station", "https://www.yilmazmachine.com.tr/en/product-category/sash-assembly-station/"),
            ("Work Bench", "https://www.yilmazmachine.com.tr/en/product-category/work-beanch/"),
        ],
    },
    "PVC": {
        "Processing Center": [
            ("Four Head Corner Welding & Cleaning Line", "https://www.yilmazmachine.com.tr/en/product-category/four-head-corner-welding-cleaning-line/"),
            ("Profile Cutting & Machining Center", "https://www.yilmazmachine.com.tr/en/product-category/profile-cutting-machining-center/"),
        ],
        "Cleaning": [
            ("CNC Corner Cleaning Machine", "https://www.yilmazmachine.com.tr/en/product-category/cnc-corner-cleaning-machine/"),
            ("Manual Corner Cleaning Machine", "https://www.yilmazmachine.com.tr/en/product-category/manual-corner-cleaning-machine/"),
            ("Window Gasket Milling Machine", "https://www.yilmazmachine.com.tr/en/product-category/window-gasket-milling-machine/"),
        ],
        "Cutting": [
            ("Double Head Cutting", "https://www.yilmazmachine.com.tr/en/product-category/double-head-cutting-2/"),
            ("Glazing Bead Cutting", "https://www.yilmazmachine.com.tr/en/product-category/glazing-bead-cutting/"),
            ("Reinforcement Sheet Band Saw", "https://www.yilmazmachine.com.tr/en/product-category/reinforcement-sheet-band-saw/"),
            ("Reinforcement Sheet Circular Saw", "https://www.yilmazmachine.com.tr/en/product-category/reinforcement-sheet-circular-saw/"),
            ("Single Head Cutting", "https://www.yilmazmachine.com.tr/en/product-category/single-head-cutting-2/"),
            ("Portable Cutting", "https://www.yilmazmachine.com.tr/en/product-category/portable-cutting-2/"),
        ],
        "Milling": [
            ("Template Copy Router", "https://www.yilmazmachine.com.tr/en/product-category/template-copy-router-machine/"),
            ("Portable Copy Router", "https://www.yilmazmachine.com.tr/en/product-category/portable-copy-router-en/"),
        ],
        "End Milling": [
            ("End Milling Machine", "https://www.yilmazmachine.com.tr/en/product-category/end-milling-machine-2/"),
            ("Portable End Milling", "https://www.yilmazmachine.com.tr/en/product-category/portable-end-milling-en/"),
        ],
        "Screwdriving": [
            ("Double Head Reinforcement Steel Screwdriver", "https://www.yilmazmachine.com.tr/en/product-category/double-head-reinforcement-stell-screwdriver-en/"),
            ("Single Head Reinforcement Steel Screwdriver", "https://www.yilmazmachine.com.tr/en/product-category/single-head-reinforcement-stell-screwdriver-en/"),
            ("Automatic Mullion Connector Assembly Machine", "https://www.yilmazmachine.com.tr/en/product-category/automatic-mullion-connector-assembly-machine/"),
        ],
        "Welding": [
            ("Double Corner Welding", "https://www.yilmazmachine.com.tr/en/product-category/double-corner-welding/"),
            ("Four Corner Welding", "https://www.yilmazmachine.com.tr/en/product-category/four-corner-welding/"),
            ("Single Corner Welding", "https://www.yilmazmachine.com.tr/en/product-category/single-corner-welding/"),
        ],
        "Transferring": [
            ("Trolley", "https://www.yilmazmachine.com.tr/en/product-category/trolley-en/"),
        ],
        "Swarf Extraction": [
            ("Vacuum Swarf Extractor", "https://www.yilmazmachine.com.tr/en/product-category/vacuum-swarf-extractor-en-2/"),
        ],
        "Conveying": [
            ("Conveyors", "https://www.yilmazmachine.com.tr/en/product-category/conveyors-en/"),
        ],
        "Assembling": [
            ("Sash Assembly Station", "https://www.yilmazmachine.com.tr/en/product-category/sash-assembly-station-en/"),
        ],
    }
}

# ===================================================
# KATEGORI HARITASI
# ===================================================
MODEL_KAT = {
    "AIM": ("Aluminyum", "ISLEME MERKEZLERI"), "ALM": ("Aluminyum", "ISLEME MERKEZLERI"), "CPM": ("Aluminyum", "ISLEME MERKEZLERI"),
    "KD":  ("Aluminyum", "KESIM"), "DC":  ("Aluminyum", "KESIM"), "ACK": ("Aluminyum", "KESIM"), "SK":  ("Aluminyum", "KESIM"),
    "MK":  ("Aluminyum", "KESIM"), "RYK": ("Aluminyum", "KESIM"), "KY":  ("Aluminyum", "KESIM"), "VK":  ("Aluminyum", "KESIM"),
    "SCM": ("Aluminyum", "KESIM"), "CDC": ("Aluminyum", "KESIM"), "SDT": ("Aluminyum", "KESIM"), "FR":  ("Aluminyum", "FREZE"),
    "NCR": ("Aluminyum", "FREZE"), "CRM": ("Aluminyum", "FREZE"), "KP":  ("Aluminyum", "KOSE PRES"), "MEM": ("Aluminyum", "KERTME"),
    "KM":  ("Aluminyum", "KERTME"), "SNM": ("Aluminyum", "KERTME"), "PYE": ("Aluminyum", "PRES"), "PT":  ("Aluminyum", "TASIMA"),
    "HP":  ("Aluminyum", "TASIMA"), "VP":  ("Aluminyum", "TASIMA"), "GPT": ("Aluminyum", "TASIMA"), "GT":  ("Aluminyum", "TASIMA"),
    "PC":  ("Aluminyum", "TASIMA"), "DKN": ("Aluminyum", "AKTARMA"), "SKN": ("Aluminyum", "AKTARMA"), "MKN": ("Aluminyum", "AKTARMA"),
    "HDL": ("Aluminyum", "AKTARMA"), "VCE": ("Aluminyum", "TALAS TOPLAMA"), "GAS": ("Aluminyum", "TALAS TOPLAMA"),
    "WAS": ("Aluminyum", "MONTAJ"), "WB":  ("Aluminyum", "MONTAJ"), "PWB": ("Aluminyum", "MONTAJ"), "RT":  ("Aluminyum", "MONTAJ"),
    "RS":  ("Aluminyum", "MONTAJ"), "NSM": ("Aluminyum", "MONTAJ"), "PIM": ("PVC", "ISLEME MERKEZI"), "CCL": ("PVC", "ISLEME MERKEZI"),
    "PCC": ("PVC", "ISLEME MERKEZI"), "CNC": ("PVC", "ISLEME MERKEZI"), "TK":  ("PVC", "KAYNAK"), "DK":  ("PVC", "KAYNAK"),
    "CA":  ("PVC", "CAPAK ALMA"), "MCA": ("PVC", "CAPAK ALMA"), "WGM": ("PVC", "CAPAK ALMA"), "SM":  ("PVC", "VIDALAMA"),
    "CK":  ("PVC", "KESIM"), "ST":  ("PVC", "FREZE"),
}

KAT_EN = {"Aluminyum": "Aluminium", "Alüminyum": "Aluminium", "PVC": "PVC"}
ALT_EN = {
    "KESIM": "Cutting", "ISLEME MERKEZLERI": "Machining Centers",
    "ISLEME MERKEZI": "Machining Centers", "FREZE": "Routing & Milling",
    "KOSE PRES": "Corner Crimping", "KERTME": "End Milling", "PRES": "Punch Press",
    "TASIMA": "Transport & Storage", "AKTARMA": "Conveyors",
    "TALAS TOPLAMA": "Swarf Extraction", "MONTAJ": "Assembly", "KAYNAK": "Welding",
    "CAPAK ALMA": "Corner Cleaning", "VIDALAMA": "Screwdriving", "DIGER": "Other",
}

CIFT_KAT = {
    "KD","DC","ACK","MK","RYK","KY","VK","CDC","SCM","SK","SDT","FR","CRM","NCR","KM",
    "MEM","PT","HP","VP","GPT","GT","PC","DKN","SKN","MKN","HDL","VCE","GAS","WAS",
    "WB","PWB","RT","RS","NSM",
}

OZEL_KAT = {
    "vce-1570":    (["PVC"], "TALAS TOPLAMA"),
    "gas-301":     (["PVC"], "TALAS TOPLAMA"),
    "cnc-609":     (["PVC"], "ISLEME MERKEZI"),
    "cnc-611":     (["PVC"], "ISLEME MERKEZI"),
    "pim-6508-se": (["PVC"], "ISLEME MERKEZI"),
    "cpm-4150-s":  (["Aluminyum"], "ISLEME MERKEZLERI"),
}

# ===================================================
# YARDIMCI
# ===================================================
VERBOSE = "--verbose" in sys.argv or "-v" in sys.argv

def log(msg, lvl="INFO"):
    icons = {"INFO": "[i]","OK": "[+]","WARN": "[!]","ERR": "[X]","SCAN": "[~]"}
    print(f"  {icons.get(lvl,'   ')} {msg}")

def vlog(msg):
    if VERBOSE: log(msg, "SCAN")

def model_prefix(slug):
    m = re.match(r'^([a-zA-Z]+)', slug)
    return m.group(1).upper() if m else ""

def kategori_belirle(slug):
    slug_l = slug.lower()
    for k, (cats, alt) in OZEL_KAT.items():
        if slug_l.startswith(k): return cats, [alt]
    prefix = model_prefix(slug)
    if prefix in MODEL_KAT:
        ana, alt = MODEL_KAT[prefix]
        if prefix in CIFT_KAT: return ["Aluminyum", "PVC"], [alt]
        return [ana], [alt]
    if 'pvc' in slug_l: return ["PVC"], ["DIGER"]
    return ["Aluminyum"], ["DIGER"]

def slug_to_title(slug):
    return slug.replace('-', ' ').strip().title()

def breadcrumb_subcategory_bul(soup):
    breadcrumb_seciciler = [
        attrs for attrs in (
            {"class": re.compile(r'breadcrumb', re.I)},
            {"id": re.compile(r'breadcrumb', re.I)},
            {"aria-label": re.compile(r'breadcrumb', re.I)},
        )
    ]
    alanlar = []
    for secici in breadcrumb_seciciler:
        alanlar.extend(soup.find_all(['nav', 'div', 'ul', 'ol'], secici))

    aday_sluglar = []
    if alanlar:
        for alan in alanlar:
            for a in alan.find_all('a', href=True):
                eslesme = re.search(r'/en/product-category/([^/]+)/?$', a['href'])
                if eslesme:
                    aday_sluglar.append(eslesme.group(1))
    else:
        for a in soup.find_all('a', href=True):
            eslesme = re.search(r'/en/product-category/([^/]+)/?$', a['href'])
            if eslesme:
                aday_sluglar.append(eslesme.group(1))

    if not aday_sluglar:
        return None
    return slug_to_title(aday_sluglar[-1])

def load_blacklist():
    if not BLACKLIST_DIR.exists(): return
    for f in BLACKLIST_DIR.iterdir():
        if f.is_file():
            with open(f, 'rb') as file:
                BAD_HASHES.add(hashlib.md5(file.read()).hexdigest())
    if BAD_HASHES:
        log(f"Blacklist yuklendi: {len(BAD_HASHES)} parmak izi korumasi aktif.", "OK")

# ===================================================
# SESSION
# ===================================================
def build_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    })
    try: s.get(f"{BASE}/en/", timeout=15, allow_redirects=True)
    except Exception: pass
    return s

def safe_get(session, url, retries=MAX_RETRY):
    session.headers["Referer"] = f"{BASE}/en/products/"
    for attempt in range(retries):
        try:
            r = session.get(url, timeout=30, allow_redirects=True)
            if r.status_code == 200: return r
            elif r.status_code == 403: time.sleep(2 * (attempt + 1))
            else: return None
        except requests.RequestException:
            time.sleep(2)
    return None

# ===================================================
# TYPE SAYFALARI - URL KESFI
# ===================================================
def urun_slug_bul(href):
    if not href:
        return None
    full_url = urljoin(BASE, href)
    path = urlparse(full_url).path.rstrip("/")
    m = re.match(r"^/en/products/([^/]+)$", path)
    return m.group(1) if m else None

def type_sayfasindan_sluglari_cek(session, page_url):
    resp = safe_get(session, page_url)
    if resp is None:
        return None
    soup = BeautifulSoup(resp.content, "html.parser")
    sluglar = []
    gorulen = set()
    for a in soup.find_all("a", href=True):
        slug = urun_slug_bul(a["href"])
        if slug and slug not in gorulen:
            gorulen.add(slug)
            sluglar.append(slug)
    return sluglar

def skip_sluglarini_topla(session):
    skip_sluglar = set()
    hata_satirlari = []
    for skip_url in SKIP_URLS:
        sluglar = type_sayfasindan_sluglari_cek(session, skip_url)
        if sluglar is None:
            hata_satirlari.append(f"SKIP_PAGE_FETCH_ERROR\t{skip_url}")
            continue
        for slug in sluglar:
            skip_sluglar.add(slug)
            hata_satirlari.append(f"SKIP_URL_MATCH\t{slug}\t{skip_url}")
    return skip_sluglar, hata_satirlari

def type_agacini_tara(session):
    skip_sluglar, hata_satirlari = skip_sluglarini_topla(session)
    slug_haritasi = {}
    type_istatistikleri = []

    for category, subcats in KATEGORI_AGACI.items():
        for subcategory, type_list in subcats.items():
            for type_name, type_url in type_list:
                time.sleep(0.3)
                sluglar = type_sayfasindan_sluglari_cek(session, type_url)
                if sluglar is None:
                    hata_satirlari.append(f"TYPE_PAGE_FETCH_ERROR\t{type_url}")
                    type_istatistikleri.append({
                        "category": category,
                        "subcategory": subcategory,
                        "type": type_name,
                        "url": type_url,
                        "count": 0,
                    })
                    continue

                kalan_sayisi = 0
                for slug in sluglar:
                    if slug in skip_sluglar:
                        continue
                    kalan_sayisi += 1
                    kayit = slug_haritasi.get(slug)
                    if kayit is None:
                        slug_haritasi[slug] = {
                            "en_url": f"{BASE}/en/products/{slug}/",
                            "tr_url": "",
                            "category": category,
                            "categories": [category],
                            "subcategory": subcategory,
                            "type": type_name,
                            "type_url": type_url,
                        }
                        continue

                    if category not in kayit["categories"]:
                        kayit["categories"].append(category)
                    kayit["category"] = category
                    kayit["subcategory"] = subcategory
                    kayit["type"] = type_name
                    kayit["type_url"] = type_url

                type_istatistikleri.append({
                    "category": category,
                    "subcategory": subcategory,
                    "type": type_name,
                    "url": type_url,
                    "count": kalan_sayisi,
                })

    return slug_haritasi, type_istatistikleri, hata_satirlari

# ===================================================
# RESIM INDIRME (HAFIZADA TEMIZLIK)
# ===================================================
def download_image(session, img_url, en_slug, index):
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    ext = Path(urlparse(img_url).path).suffix.lower()
    if ext not in ('.jpg', '.jpeg', '.png', '.webp', '.gif'): ext = '.jpg'
    filename  = f"{en_slug}-{index}{ext}"
    save_path = IMG_DIR / filename
    web_path  = f"/images/yilmaz/{filename}"

    if save_path.exists() and save_path.stat().st_size > 1000:
        vlog(f"    Zaten mevcut: {filename}")
        return web_path

    original_url = re.sub(r'-\d+x\d+\.', '.', img_url)

    for try_url in [original_url, img_url]:
        r = safe_get(session, try_url)
        if r and len(r.content) > 1000:
            # === YENI: Hafizada Blacklist Kontrolu ===
            if BAD_HASHES:
                img_hash = hashlib.md5(r.content).hexdigest()
                if img_hash in BAD_HASHES:
                    vlog(f"    [X] Çöp resim reddedildi: {img_url[-30:]}")
                    return None # Kaydetmeden reddet

            save_path.write_bytes(r.content)
            vlog(f"    Indirildi: {filename} ({len(r.content)//1024}KB)")
            return web_path
    return img_url

# ===================================================
# SAYFA PARSE
# ===================================================
def parse_page(session, en_slug, urls, download_images):
    en_url = urls["en_url"]
    tr_url = urls.get("tr_url", "")
    resp = safe_get(session, en_url)
    if resp is None and tr_url: resp = safe_get(session, tr_url)
    if resp is None: return None

    soup = BeautifulSoup(resp.content, 'html.parser')

    isim = ""
    title_tag = soup.find('title')
    if title_tag:
        t = title_tag.get_text(strip=True)
        isim = re.split(r'\s*[-|]\s*YILMAZ', t, flags=re.IGNORECASE)[0].strip()
    if not isim:
        h1 = soup.find('h1')
        if h1: isim = h1.get_text(strip=True)
    if not isim or isim.lower() in ('products', 'urunler', ''):
        parts = en_slug.split('-')
        code = []
        for p in parts:
            code.append(p)
            if any(c.isdigit() for c in p): break
        isim = " ".join(code).upper()

    aciklama = ""
    skip_words = ['consent', 'cookie', 'loading', 'required field', 'zorunlu', 'subscribe', 'newsletter', 'javascript']
    for p in soup.find_all('p'):
        t = p.get_text(strip=True)
        if len(t) > 60 and not any(x in t.lower() for x in skip_words):
            aciklama = t
            break

    cdn_resimler = set()
    bad_keywords = ['logo', 'toolquaz', 'uvaga', 'banner']
    
    # "Sadece ana ürün galerisi div'i" yaklaşımı veya genel tarama ama katı blacklist
    for img in soup.find_all('img'):
        for attr in ('src', 'data-src', 'data-lazy-src', 'data-original', 'data-img'):
            val = img.get(attr, '') or ''
            if 'cloudfront.net' in val and not any(bad in val.lower() for bad in bad_keywords):
                cdn_resimler.add(re.sub(r'-\d+x\d+\.', '.', val))

    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'cloudfront.net' in href and any(href.endswith(e) for e in ('.jpg','.jpeg','.png','.webp')):
            if not any(bad in href.lower() for bad in bad_keywords):
                cdn_resimler.add(re.sub(r'-\d+x\d+\.', '.', href))

    for m_obj in re.finditer(r'https://[^\s"\'<>]+cloudfront\.net[^\s"\'<>]+\.(?:jpg|jpeg|png|webp)', resp.text):
        url = re.sub(r'-\d+x\d+\.', '.', m_obj.group())
        if not any(bad in url.lower() for bad in bad_keywords):
            cdn_resimler.add(url)

    cdn_resimler = sorted(cdn_resimler)

    # `--images` yoksa klasore dokunmadan mevcut yerel gorselleri kullan.
    yerel_resimler = _mevcut_resim_bul(en_slug)

    # === YENI: Dinamik Indeksleme (Copleri atla, sayiyi koru) ===
    resimler = []
    if download_images and cdn_resimler:
        gecerli_index = 1
        for img_url in cdn_resimler:
            lokal = download_image(session, img_url, en_slug, gecerli_index)
            if lokal: # Eger None degilse (yani cop degilse) ekle
                resimler.append(lokal)
                gecerli_index += 1 # Sadece gercek resimlerde indexi artir
            time.sleep(0.2)
    elif yerel_resimler:
        resimler = yerel_resimler
    elif cdn_resimler:
        resimler = list(cdn_resimler)

    specs = {
        "STANDARD ACCESSORIES": [],
        "OPTIONAL ACCESSORIES": [],
        "GENERAL FEATURES": [],
    }
    kw_map = {
        "STANDART": "STANDARD ACCESSORIES", "STANDARD": "STANDARD ACCESSORIES",
        "OPTIONAL": "OPTIONAL ACCESSORIES", "OPSIYONEL": "OPTIONAL ACCESSORIES",
        "GENERAL": "GENERAL FEATURES", "GENEL": "GENERAL FEATURES",
        "TECHNICAL": "GENERAL FEATURES", "TEKNIK": "GENERAL FEATURES",
        "FEATURES": "GENERAL FEATURES", "SPECIFICATIONS": "GENERAL FEATURES",
    }
    for hx in soup.find_all(['h2','h3','h4']):
        baslik = hx.get_text(strip=True).upper()
        grup = next((v for k, v in kw_map.items() if k in baslik), None)
        if not grup: continue
        ul = hx.find_next_sibling('ul')
        if ul:
            items = [li.get_text(strip=True) for li in ul.find_all('li') if li.get_text(strip=True)]
            specs[grup].extend(items)

    # TEKNİK TABLO
    teknik_tablo = {}
    for table in soup.find_all('table'):
        for row in table.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                val = cells[1].get_text(strip=True)
                if key and val and len(key) < 50:
                    teknik_tablo[key] = val
    for div in soup.find_all('div', class_=re.compile(r'technical|spec|data|table', re.I)):
        items_d = div.find_all(['dt', 'dd', 'li', 'span'])
        for i in range(0, len(items_d)-1, 2):
            key = items_d[i].get_text(strip=True)
            val = items_d[i+1].get_text(strip=True) if i+1 < len(items_d) else ''
            if key and val and len(key) < 50 and len(val) < 100:
                teknik_tablo[key] = val
    for container in soup.find_all('div'):
        img_t = container.find('img')
        spans = container.find_all(['span', 'p', 'div'], recursive=False)
        if img_t and len(spans) >= 2:
            deger = spans[0].get_text(strip=True)
            birim = spans[1].get_text(strip=True) if len(spans) > 1 else ''
            alt = img_t.get('alt','') or img_t.get('title','') or img_t.get('src','').split('/')[-1].split('.')[0]
            if deger and alt and len(deger) < 30:
                teknik_tablo[alt] = f"{deger} {birim}".strip()

    # PDF KATALOG
    katalog_url = None
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True).lower()
        if href.lower().endswith('.pdf') or 'katalog' in text or 'catalog' in text:
            katalog_url = urljoin(BASE, href) if href.startswith('/') else href
            break
    if not katalog_url:
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '.pdf' in href.lower():
                katalog_url = urljoin(BASE, href) if href.startswith('/') else href
                break

    breadcrumb_alt_en = breadcrumb_subcategory_bul(soup)
    kategoriler_tr, alt_kategoriler_tr = kategori_belirle(en_slug)
    kategoriler_en = [KAT_EN.get(k, k) for k in kategoriler_tr]
    alt_en = breadcrumb_alt_en or (ALT_EN.get(alt_kategoriler_tr[0], alt_kategoriler_tr[0]) if alt_kategoriler_tr else "Other")

    return {
        "slug": en_slug,
        "brand": "yilmaz",
        "categories": kategoriler_en,
        "subcategory": alt_en,
        "diller": {
            "en": {
                "name": isim,
                "description": aciklama,
                "images": resimler,
                "specs": specs,
                "technical_data": teknik_tablo,
                "catalog": katalog_url,
            }
        },
    }

def _mevcut_resim_bul(en_slug):
    if not IMG_DIR.exists(): return []
    parts = en_slug.split('-')
    kod = []
    for i, p in enumerate(parts):
        kod.append(p)
        if any(c.isdigit() for c in p):
            if i+1 < len(parts) and len(parts[i+1]) <= 2 and parts[i+1].isalpha():
                if parts[i+1].lower() != kod[0].lower(): kod.append(parts[i+1])
            break
    model_k = "-".join(kod).lower()
    return [f"/images/yilmaz/{f.name}" for f in sorted(IMG_DIR.iterdir()) 
            if f.is_file() and f.stat().st_size > 1000 and (f.name.lower().startswith(model_k + "-") or f.name.lower().startswith(model_k + "."))]

# ===================================================
# ANA AKIS
# ===================================================
def main():
    print("\n" + "=" * 64)
    print("  YILMAZ MAKINE GUNCELLEYICI v4.2")
    print("  Type sayfalari | EN resim isimleri | BLACKLIST KORUMASI")
    print("=" * 64 + "\n")

    load_blacklist() # === YENI: Baslarken karalisteyi yukle ===

    test_mode = "--test" in sys.argv
    download_images = "--images" in sys.argv

    session = build_session()
    tum_urls, type_istatistikleri, hata_satirlari = type_agacini_tara(session)

    if not tum_urls:
        log("Hic urun bulunamadi!", "ERR")
        sys.exit(1)

    items = list(tum_urls.items())
    if test_mode: items = items[:5]

    log(f"=== {len(items)} MAKINE ISLENIYOR ===", "SCAN")
    makineler, hatali = [], 0
    standart_dolu = 0

    for i, (en_slug, urls) in enumerate(items, 1):
        log(f"[{i}/{len(items)}] {en_slug}")
        time.sleep(DELAY)
        m = parse_page(session, en_slug, urls, download_images)
        if m:
            m["category"] = urls["category"]
            m["categories"] = urls["categories"]
            m["subcategory"] = urls["subcategory"]
            m["type"] = urls["type"]
            m["diller"]["en"].pop("catalog", None)
            if m["diller"]["en"]["specs"]["STANDARD ACCESSORIES"]:
                standart_dolu += 1
            makineler.append(m)
        else:
            hatali += 1
            hata_satirlari.append(f"DETAIL_PARSE_ERROR\t{en_slug}\t{urls['en_url']}")

    makineler.sort(key=lambda m: m["slug"])

    if JSON_OUTPUT.exists(): shutil.copy2(JSON_OUTPUT, JSON_BACKUP)

    JSON_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(ERROR_OUTPUT, 'w', encoding='utf-8') as f:
        if hata_satirlari:
            f.write("\n".join(hata_satirlari) + "\n")
        else:
            f.write("OK\n")

    JSON_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(makineler, f, ensure_ascii=False, indent=2)

    print(f"\n  TAMAMLANDI. Toplam: {len(makineler)} | Hatali: {hatali}")
    print(f"  STANDARD ACCESSORIES dolu: {standart_dolu}\n")
    print("  TYPE URL OZETI:")
    for row in type_istatistikleri:
        print(f"    - {row['category']} | {row['subcategory']} | {row['type']} | {row['count']} | {row['url']}")
    if hata_satirlari:
        print("  HATA / ATLANAN KAYITLAR:")
        for line in hata_satirlari:
            print(f"    - {line}")
    else:
        print("  HATA / ATLANAN KAYITLAR: yok\n")

if __name__ == "__main__":
    main()
