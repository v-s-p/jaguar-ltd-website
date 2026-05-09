#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JAGUAR LTD - GOCMAKSAN GUNCELLEYICI v7.0 (ULTIMATE SURUM)
Tam Kategori Zekası | Kusursuz İsimler | Esnek Sniper | PDF Çekici | Kardeş Makineler
"""
import sys, io, re, json, time, shutil
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime
import requests
from bs4 import BeautifulSoup

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

BASE = "https://www.gocmaksan.com"

SCRIPT_DIR   = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
JSON_OUTPUT  = PROJECT_ROOT / "src" / "data" / "gocmaksan.json"
JSON_BACKUP  = PROJECT_ROOT / "src" / "data" / f"gocmaksan_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
IMG_DIR      = PROJECT_ROOT / "public" / "images" / "gocmaksan"
CATALOG_DIR  = PROJECT_ROOT / "public" / "catalogs" / "gocmaksan"

DELAY     = 1.5
MAX_RETRY = 3

KATEGORI_MAP = {
    "/eng/bukme-makinalari":                                    ("Bending Machines", "Standard"),
    "/eng/portatif-bukme-makinalari":                           ("Bending Machines", "Portable"),
    "/eng/etriye-bukme-makinalari":                             ("Bending Machines", "Stirrup"),
    "/eng/spiral-bukme-makinalari":                             ("Bending Machines", "Spiral"),
    "/eng/filiz-demir-bukme-makinalari":                        ("Bending Machines", "Dowel Bar"),
    "/eng/kesme-makinalari":                                    ("Cutting Machines", "Standard"),
    "/eng/portatif-kesme-makinalari":                           ("Cutting Machines", "Portable"),
    "/eng/kombine-demir-kesme-bukme-makinalari":                ("Combined Machines", "Combined"),
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Connection": "keep-alive",
    })
    try: s.get(f"{BASE}/eng", timeout=15)
    except: pass
    return s

def safe_get(session, url, retries=MAX_RETRY):
    session.headers["Referer"] = f"{BASE}/eng"
    for attempt in range(retries):
        try:
            r = session.get(url, timeout=30, allow_redirects=True)
            if r.status_code == 200: return r
            time.sleep(2 * (attempt + 1))
        except requests.RequestException:
            time.sleep(2)
    return None

def get_product_links(session, cat_url):
    full_url = BASE + cat_url
    r = safe_get(session, full_url)
    if not r: return []
    soup = BeautifulSoup(r.content, 'html.parser')
    links = set()

    for a in soup.find_all('a', href=True):
        href = a['href']
        parts = [p for p in href.split('/') if p]
        if len(parts) >= 3 and parts[0] == 'eng':
            cat_part = f"/eng/{parts[1]}"
            if cat_part in KATEGORI_MAP:
                links.add(href)
            
    return list(links)

def get_smart_categories(href, raw_name):
    parts = [p for p in href.split('/') if p]
    cat_part = f"/eng/{parts[1]}" if len(parts) > 1 else ""
    base_cat = KATEGORI_MAP.get(cat_part)
    
    name_upper = raw_name.upper()
    slug_upper = parts[-1].upper() if parts else ""
    
    cats, subcats = set(), set()
    
    if base_cat:
        cats.add(base_cat[0])
        subcats.add(base_cat[1])

    if "KOMBINE" in slug_upper or "COMBINED" in name_upper or "KOMBINE" in cat_part.upper():
        cats.update(["Combined Machines", "Bending Machines", "Cutting Machines"])
        subcats.add("Combined")
    else:
        if "BENDING" in cat_part.upper() or "BUKME" in slug_upper:
            cats.add("Bending Machines")
            if "SX" in name_upper or "SX" in slug_upper or "SPIRAL" in slug_upper: subcats.add("Spiral")
            elif "SL" in name_upper or "SL" in slug_upper or "ETRIYE" in slug_upper or "STIRRUP" in name_upper: subcats.add("Stirrup")
            elif "MG" in name_upper or "BT" in name_upper or "PORTATIF" in slug_upper or "PORTABLE" in name_upper: subcats.add("Portable")
            elif "FILIZ" in slug_upper or "DOWEL" in name_upper: subcats.add("Dowel Bar")
            else: subcats.add("Standard")

        if "CUTTING" in cat_part.upper() or "KESME" in slug_upper:
            cats.add("Cutting Machines")
            if "PORTATIF" in slug_upper or "PORTABLE" in name_upper: subcats.add("Portable")
            else: subcats.add("Standard")

    if "EL-ALETLERI" in slug_upper or "HAND TOOLS" in cat_part.upper() or "KALIP" in slug_upper:
        cats.add("Hand Tools")
        subcats.add("Hand Tools")

    if "HAFIF" in slug_upper or "LIGHT" in cat_part.upper():
        cats.add("Light Construction")
        subcats.add("Light Construction")

    if "TESIS" in slug_upper or "STEEL FACTORY" in cat_part.upper() or "TESIS" in cat_part.upper():
        cats.add("Steel Factory Solutions")
        subcats.add("Steel Factory")

    if not cats:
        cats.add("Other")
        subcats.add("Other")

    return list(cats), list(subcats)

def clean_machine_name(raw_name, slug):
    name = raw_name
    silinecekler = [
        r'(?i)G[öo]çmaksan', r'(?i)GMS', r'(?i)İnşaat\s+Demiri', r'(?i)İnşaat', r'(?i)Demiri', 
        r'(?i)Kesme\s+Makinası', r'(?i)Bükme\s+Makinası', r'(?i)Kesme\s+ve\s+Bükme',
        r'(?i)Makinası', r'(?i)Makinaları', r'(?i)Machine\w*', r'(?i)Rebar', 
        r'(?i)Bending', r'(?i)Cutting', r'(?i)Combined', r'(?i)Portable', 
        r'(?i)Spiral', r'(?i)Stirrup', r'(?i)Dowel\s+Bar'
    ]
    for kelime in silinecekler: 
        name = re.sub(kelime, '', name)
    
    name = name.strip(' -|/:,')
    if not name or len(name) < 2: 
        slug_clean = re.sub(r'(?i)(gocmaksan|gms|makinasi|makinalari|insaat|demiri|kesme|bukme)', '', slug)
        name = slug_clean.replace('-', ' ').strip().upper() if slug_clean else slug.upper()
        
    return re.sub(r'\s+', ' ', name).strip()

def download_image(session, img_url, slug, index):
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    ext = Path(urlparse(img_url).path).suffix.lower()
    if ext not in ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.avif'): ext = '.jpg'

    filename  = f"{slug}-{index}{ext}"
    save_path = IMG_DIR / filename
    web_path  = f"/images/gocmaksan/{filename}"

    if save_path.exists() and save_path.stat().st_size > 1000:
        return web_path

    r = safe_get(session, img_url)
    if r and len(r.content) > 500:
        save_path.write_bytes(r.content)
        return web_path
    return img_url

def download_pdf(session, pdf_url, slug):
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{slug}.pdf"
    save_path = CATALOG_DIR / filename
    web_path = f"/catalogs/gocmaksan/{filename}"

    if save_path.exists() and save_path.stat().st_size > 1000:
        vlog(f"    PDF Zaten mevcut: {filename}")
        return web_path

    r = safe_get(session, pdf_url)
    if r and len(r.content) > 1000:
        save_path.write_bytes(r.content)
        vlog(f"    PDF Indirildi: {filename} ({len(r.content)//1024}KB)")
        return web_path
    return pdf_url 

def parse_product(session, href, download_images):
    full_url = BASE + href
    slug = href.rstrip('/').split('/')[-1]

    r = safe_get(session, full_url)
    if not r: return None

    soup = BeautifulSoup(r.content, 'html.parser')

    # BASLIK & KATEGORI
    raw_name = slug.upper().replace('-', ' ')
    h1 = soup.find('h1')
    if h1: raw_name = h1.get_text(strip=True)
    clean_name = clean_machine_name(raw_name, slug)
    cats, subcats = get_smart_categories(href, clean_name)

    # ACIKLAMA
    description = ""
    for p in soup.find_all('p'):
        t = p.get_text(strip=True)
        if len(t) > 60 and "cookie" not in t.lower():
            description = t
            break

    # ==========================================
    # PDF YAKALAMA (Çifte Güvenlikli Sniper)
    # ==========================================
    pdf_link = ""
    pdf_baslik = soup.find(lambda tag: tag.name in ['h3', 'h4', 'h2'] and 'PDF' in tag.get_text(strip=True).upper())
    
    if pdf_baslik:
        a_tag = pdf_baslik.find_next('a', href=True)
        if a_tag and '.pdf' in a_tag['href'].lower():
            raw_pdf_url = a_tag['href']
            if raw_pdf_url.startswith('/'): raw_pdf_url = BASE + raw_pdf_url
            pdf_link = download_pdf(session, raw_pdf_url, slug) if download_images else raw_pdf_url
            
    # B Planı: Eğer başlık yoksa sayfadaki ilk pdf'i bul
    if not pdf_link:
        for a in soup.find_all('a', href=True):
            if '.pdf' in a['href'].lower() and 'website-files.com' in a['href']:
                raw_pdf_url = a['href']
                if raw_pdf_url.startswith('/'): raw_pdf_url = BASE + raw_pdf_url
                pdf_link = download_pdf(session, raw_pdf_url, slug) if download_images else raw_pdf_url
                break

    # ==========================================
    # YENI: SERI KARDESLERI (RELATED PRODUCTS)
    # ==========================================
    related_products = []
    diger_urunler_kasasi = soup.find('div', class_=re.compile(r'di-er-r-nler'))
    
    if diger_urunler_kasasi:
        for a_link in diger_urunler_kasasi.find_all('a', class_=re.compile(r'-link-blok')):
            isim_tag = a_link.find(['h4', 'h3', 'span'])
            if isim_tag:
                kardes_isim = isim_tag.get_text(strip=True)
                if kardes_isim:
                    related_products.append(kardes_isim)

    # ==========================================
    # RESIM SNIPER
    # ==========================================
    images_raw = []
    for img in soup.find_all('img', class_=re.compile(r'urun-image')):
        src = img.get('src') or img.get('data-src') or ''
        srcset = img.get('srcset', '')
        if srcset:
            try: src = srcset.split(',')[-1].strip().split(' ')[0]
            except: pass
        if src and src not in images_raw:
            images_raw.append(src)

    if download_images and images_raw:
        images = []
        for idx, img_url in enumerate(images_raw, 1):
            lokal = download_image(session, img_url, slug, idx)
            images.append(lokal)
            time.sleep(0.2)
    else:
        images = images_raw

    # ==========================================
    # OZELLIKLER (TABLO) SNIPER
    # ==========================================
    raw_specs = { "Featured Features": [], "Technical Data": [], "Capacities": [] }
    
    feat_div = soup.find('div', class_='ne-kan-zellikler')
    if feat_div: raw_specs["Featured Features"] = [li.get_text(strip=True) for li in feat_div.find_all('li')]

    tech_div = soup.find('div', class_='teknik-veriler-wrapper')
    if tech_div:
        for item in tech_div.find_all('div', class_='teknik-veri-div'):
            val = item.find('div', class_='teknik-veri-metin')
            key = item.find(['h4', 'h5', 'h3'], class_='teknik-veri-ba-l-k')
            if val and key:
                v_text = val.get_text(strip=True)
                k_text = key.get_text(separator=" ", strip=True).replace('\n', ' ')
                raw_specs["Technical Data"].append(f"{k_text}: {v_text}")

    cap_div = soup.find('div', class_='kapasite-wrapper')
    if cap_div:
        for item in cap_div.find_all('div', class_='kapasite-h-cre'):
            baslik = item.find('h4', class_='kapasite-baslik')
            rich_text = item.find('div', class_='kapasite-rich-text')
            if baslik and rich_text:
                k_text = baslik.get_text(separator=" ", strip=True).replace('\n', ' ')
                v_texts = [p.get_text(strip=True) for p in rich_text.find_all('p')]
                for v in v_texts: raw_specs["Capacities"].append(f"{k_text} -> {v}")

    # ==========================================
    # B PLANI: YENI TASARIM / WEBFLOW BLOKLARI (HB 12x3, Steel Factory)
    # ==========================================
    if not raw_specs["Featured Features"] and not raw_specs["Technical Data"]:
        # Ozel tasarimli sayfalarda layout bloklari arasi gizli text
        for flex_div in soup.find_all('div', class_=re.compile(r'flex-block-\d+')):
            text_div = flex_div.find('div', class_=re.compile(r'text-block-\d+'))
            if text_div:
                t = text_div.get_text(strip=True)
                if 3 < len(t) < 80 and t not in raw_specs["Featured Features"] and not t.lower().startswith("cookie"):
                    raw_specs["Featured Features"].append(t)

    specs = {
        "STANDART AKSESUARLAR": [],
        "OPSIYONEL AKSESUARLAR": [],
        "GENEL OZELLIKLER": raw_specs["Featured Features"],
        "TEKNIK_TABLO": {}
    }
    
    for item in raw_specs["Technical Data"]:
        parts = item.split(':', 1)
        if len(parts) == 2:
            specs["TEKNIK_TABLO"][parts[0].strip()] = parts[1].strip()
        else:
            specs["TEKNIK_TABLO"][item] = "Yes"
            
    for item in raw_specs["Capacities"]:
        parts = item.split('->', 1)
        if len(parts) == 2:
            specs["TEKNIK_TABLO"][parts[0].strip()] = parts[1].strip()
        else:
            specs["TEKNIK_TABLO"][item] = "Yes"

    return {
        "slug":        slug,
        "brand":       "gocmaksan",
        "categories":  cats,
        "subcategory": subcats,
        "pdf_catalog": pdf_link,
        "related_products": related_products,
        "specs":       specs,
        "diller": {
            "en": {
                "name":        clean_name,
                "description": description,
                "images":      images,
            }
        }
    }

def main():
    print("\n" + "=" * 64)
    print("  GOCMAKSAN GUNCELLEYICI v7.0 (ULTIMATE SURUM)")
    print("  Akıllı Kategori | Çift Güvenlikli PDF | Kardeş Makineler")
    print("=" * 64 + "\n")

    test_mode       = "--test"   in sys.argv
    download_images = "--images" in sys.argv

    if test_mode:       log("TEST MODU AÇIK", "WARN")
    if download_images: log("Resimler ve PDF'ler indirilecek", "WARN")

    session = build_session()
    tum_urun_linkleri = set([
        "/eng/kombine-demir-kesme-bukme-makinalari/gms-max-40-gocmaksan-insaat-demiri-kesme-bukme-makinasi"
    ])

    for cat_path in KATEGORI_MAP.keys():
        links = get_product_links(session, cat_path)
        tum_urun_linkleri.update(links)

    log(f"Toplam {len(tum_urun_linkleri)} benzersiz ÜRÜN linki bulundu", "OK")

    items = list(tum_urun_linkleri)
    if test_mode: items = items[:3]

    makineler, hatali = [], 0

    for i, href in enumerate(items, 1):
        slug = href.rstrip('/').split('/')[-1]
        log(f"[{i}/{len(items)}] {slug}")
        time.sleep(DELAY)
        
        m = parse_product(session, href, download_images)
        if m:
            makineler.append(m)
            vlog(f"  -> {m['diller']['en']['name']} | {m['subcategory']} | Resim: {len(m['diller']['en']['images'])} | PDF: {'Var' if m['pdf_catalog'] else 'Yok'}")
        else: hatali += 1

    makineler.sort(key=lambda m: m['slug'])
    if JSON_OUTPUT.exists(): shutil.copy2(JSON_OUTPUT, JSON_BACKUP)
    JSON_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f: json.dump(makineler, f, ensure_ascii=False, indent=2)

    print(f"\n  TAMAMLANDI. Toplam Ürün: {len(makineler)} | Hatalı: {hatali}\n")

if __name__ == "__main__":
    main()