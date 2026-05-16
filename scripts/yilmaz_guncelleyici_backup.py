#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YILMAZ MAKINE - JAGUAR LTD ENVANTER GUNCELLEYICI v4.1
Sitemap-tabanli, resim indirmeli, EN slug bazli

Kullanim:
  python yilmaz_guncelleyici.py              # Tum veriyi cek, CDN URL'leri sakla
  python yilmaz_guncelleyici.py --images     # Resimleri de indir (EN isimli)
  python yilmaz_guncelleyici.py --test       # 3 makine test
  python yilmaz_guncelleyici.py --skip       # Mevcut JSON'dakileri atla
  python yilmaz_guncelleyici.py --verbose    # Detayli log

Gereksinimler:
  pip install requests beautifulsoup4
"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import json, re, time, shutil, gzip
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime

# ===================================================
# KONFIG
# ===================================================
BASE     = "https://www.yilmazmachine.com.tr"
SITEMAPS = [f"{BASE}/urunler-sitemap{i}.xml" for i in range(1, 6)]

SCRIPT_DIR   = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
JSON_OUTPUT  = PROJECT_ROOT / "src" / "data" / "yilmaz.json"
JSON_BACKUP  = PROJECT_ROOT / "src" / "data" / f"machines_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
IMG_DIR      = PROJECT_ROOT / "public" / "images" / "machines"

DELAY     = 1.5
MAX_RETRY = 3

# ===================================================
# KATEGORI HARITASI
# ===================================================
MODEL_KAT = {
    "AIM": ("Aluminyum", "ISLEME MERKEZLERI"),
    "ALM": ("Aluminyum", "ISLEME MERKEZLERI"),
    "CPM": ("Aluminyum", "ISLEME MERKEZLERI"),
    "KD":  ("Aluminyum", "KESIM"),
    "DC":  ("Aluminyum", "KESIM"),
    "ACK": ("Aluminyum", "KESIM"),
    "SK":  ("Aluminyum", "KESIM"),
    "MK":  ("Aluminyum", "KESIM"),
    "RYK": ("Aluminyum", "KESIM"),
    "KY":  ("Aluminyum", "KESIM"),
    "VK":  ("Aluminyum", "KESIM"),
    "SCM": ("Aluminyum", "KESIM"),
    "CDC": ("Aluminyum", "KESIM"),
    "SDT": ("Aluminyum", "KESIM"),
    "FR":  ("Aluminyum", "FREZE"),
    "NCR": ("Aluminyum", "FREZE"),
    "CRM": ("Aluminyum", "FREZE"),
    "KP":  ("Aluminyum", "KOSE PRES"),
    "MEM": ("Aluminyum", "KERTME"),
    "KM":  ("Aluminyum", "KERTME"),
    "SNM": ("Aluminyum", "KERTME"),
    "PYE": ("Aluminyum", "PRES"),
    "PT":  ("Aluminyum", "TASIMA"),
    "HP":  ("Aluminyum", "TASIMA"),
    "VP":  ("Aluminyum", "TASIMA"),
    "GPT": ("Aluminyum", "TASIMA"),
    "GT":  ("Aluminyum", "TASIMA"),
    "PC":  ("Aluminyum", "TASIMA"),
    "DKN": ("Aluminyum", "AKTARMA"),
    "SKN": ("Aluminyum", "AKTARMA"),
    "MKN": ("Aluminyum", "AKTARMA"),
    "HDL": ("Aluminyum", "AKTARMA"),
    "VCE": ("Aluminyum", "TALAS TOPLAMA"),
    "GAS": ("Aluminyum", "TALAS TOPLAMA"),
    "WAS": ("Aluminyum", "MONTAJ"),
    "WB":  ("Aluminyum", "MONTAJ"),
    "PWB": ("Aluminyum", "MONTAJ"),
    "RT":  ("Aluminyum", "MONTAJ"),
    "RS":  ("Aluminyum", "MONTAJ"),
    "NSM": ("Aluminyum", "MONTAJ"),
    "PIM": ("PVC", "ISLEME MERKEZI"),
    "CCL": ("PVC", "ISLEME MERKEZI"),
    "PCC": ("PVC", "ISLEME MERKEZI"),
    "CNC": ("PVC", "ISLEME MERKEZI"),
    "TK":  ("PVC", "KAYNAK"),
    "DK":  ("PVC", "KAYNAK"),
    "CA":  ("PVC", "CAPAK ALMA"),
    "MCA": ("PVC", "CAPAK ALMA"),
    "WGM": ("PVC", "CAPAK ALMA"),
    "SM":  ("PVC", "VIDALAMA"),
    "CK":  ("PVC", "KESIM"),
    "ST":  ("PVC", "FREZE"),
}

CIFT_KAT = {
    "KD","DC","ACK","MK","RYK","KY","VK","CDC","SCM","SK",
    "SDT","FR","CRM","NCR","KM","MEM","PT","HP","VP","GPT",
    "GT","PC","DKN","SKN","MKN","HDL","VCE","GAS","WAS","WB",
    "PWB","RT","RS","NSM",
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
        if slug_l.startswith(k):
            return cats, [alt]
    prefix = model_prefix(slug)
    if prefix in MODEL_KAT:
        ana, alt = MODEL_KAT[prefix]
        if prefix in CIFT_KAT:
            return ["Aluminyum", "PVC"], [alt]
        return [ana], [alt]
    if 'pvc' in slug_l:
        return ["PVC"], ["DIGER"]
    return ["Aluminyum"], ["DIGER"]

def parse_xml_safe(content_bytes):
    """
    Gzip, BOM ve encoding sorunlarini atlayarak XML parse eder.
    """
    # 1. Gzip mi?
    if content_bytes[:2] == b'\x1f\x8b':
        try:
            content_bytes = gzip.decompress(content_bytes)
        except Exception:
            pass

    # 2. UTF-8 BOM kaldir
    content_bytes = content_bytes.lstrip(b'\xef\xbb\xbf')

    # 3. Deneme 1: direkt parse
    try:
        return ET.fromstring(content_bytes)
    except ET.ParseError:
        pass

    # 4. Deneme 2: text olarak decode et ve yeniden encode
    try:
        text = content_bytes.decode('utf-8', errors='replace')
        text = text.lstrip('\ufeff')  # unicode BOM
        return ET.fromstring(text.encode('utf-8'))
    except ET.ParseError:
        pass

    # 5. Deneme 3: latin-1 ile
    try:
        text = content_bytes.decode('latin-1', errors='replace')
        return ET.fromstring(text.encode('utf-8'))
    except ET.ParseError as e:
        raise e

# ===================================================
# SESSION
# ===================================================
def build_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "identity",  # Gzip'i biz halledelim
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    })
    try:
        vlog("Ana sayfa ziyaret ediliyor...")
        s.get(f"{BASE}/en/", timeout=15, allow_redirects=True)
        time.sleep(0.5)
    except Exception:
        pass
    return s

def safe_get(session, url, retries=MAX_RETRY):
    session.headers["Referer"] = f"{BASE}/en/products/"
    for attempt in range(retries):
        try:
            r = session.get(url, timeout=30, allow_redirects=True)
            if r.status_code == 200:
                return r
            elif r.status_code == 403:
                vlog(f"403 - {url} (deneme {attempt+1})")
                time.sleep(2 * (attempt + 1))
            else:
                vlog(f"HTTP {r.status_code} - {url}")
                return None
        except requests.RequestException as e:
            vlog(f"Hata: {e} (deneme {attempt+1})")
            time.sleep(2)
    return None

# ===================================================
# SITEMAP - URL KESFI
# ===================================================
NS_URL  = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
NS_HTML = "{http://www.w3.org/1999/xhtml}"

def sitemap_urls(session):
    log("=== SITEMAP KESFI ===", "SCAN")
    makineler = {}

    for sitemap_url in SITEMAPS:
        time.sleep(0.3)
        r = safe_get(session, sitemap_url)
        if not r:
            log(f"Sitemap alinamadi: {sitemap_url}", "WARN")
            continue

        vlog(f"Sitemap {sitemap_url[-20:]} - {len(r.content)} byte, "
             f"encoding={r.headers.get('Content-Encoding','?')}, "
             f"ilk4={r.content[:4].hex()}")

        try:
            root = parse_xml_safe(r.content)
        except Exception as e:
            log(f"XML parse hatasi ({sitemap_url[-25:]}): {e}", "WARN")
            continue

        sayac = 0
        for url_elem in root.findall(f"{NS_URL}url"):
            loc_elem = url_elem.find(f"{NS_URL}loc")
            if loc_elem is None:
                continue
            loc = loc_elem.text or ""

            if "/en/products/" not in loc:
                continue

            en_slug = loc.rstrip("/").split("/")[-1]
            if not en_slug or en_slug == "products":
                continue

            tr_url = ""
            for link in url_elem.findall(f"{NS_HTML}link"):
                if link.get("hreflang") == "tr":
                    tr_url = link.get("href", "")
                    break

            if en_slug not in makineler:
                makineler[en_slug] = {"en_url": loc, "tr_url": tr_url}
                sayac += 1

        vlog(f"  -> {sayac} yeni slug eklendi")

    log(f"Toplam {len(makineler)} benzersiz makine", "OK")
    return makineler

# ===================================================
# RESIM INDIRME
# ===================================================
def download_image(session, img_url, en_slug, index):
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    ext = Path(urlparse(img_url).path).suffix.lower()
    if ext not in ('.jpg', '.jpeg', '.png', '.webp', '.gif'):
        ext = '.jpg'

    filename  = f"{en_slug}-{index}{ext}"
    save_path = IMG_DIR / filename
    web_path  = f"/images/yilmaz/{filename}"

    if save_path.exists() and save_path.stat().st_size > 1000:
        vlog(f"    Zaten mevcut: {filename}")
        return web_path

    # Orijinal boyutlu URL (thumbnail suffix'ini kaldir)
    original_url = re.sub(r'-\d+x\d+\.', '.', img_url)

    for try_url in [original_url, img_url]:
        r = safe_get(session, try_url)
        if r and len(r.content) > 1000:
            save_path.write_bytes(r.content)
            vlog(f"    Indirildi: {filename} ({len(r.content)//1024}KB)")
            return web_path

    vlog(f"    Indirilemedi: {img_url[-50:]}")
    return img_url

# ===================================================
# SAYFA PARSE
# ===================================================
def parse_page(session, en_slug, urls, download_images):
    en_url = urls["en_url"]
    tr_url = urls.get("tr_url", "")

    resp = safe_get(session, en_url)
    if resp is None and tr_url:
        vlog(f"  EN 403, TR deneniyor...")
        resp = safe_get(session, tr_url)

    if resp is None:
        log(f"  Erisim basarisiz: {en_slug}", "WARN")
        return None

    soup = BeautifulSoup(resp.content, 'html.parser')

    # BASLIK
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

    # ACIKLAMA
    aciklama = ""
    skip_words = ['consent', 'cookie', 'loading', 'required field', 'zorunlu',
                  'subscribe', 'newsletter', 'javascript']
    for p in soup.find_all('p'):
        t = p.get_text(strip=True)
        if len(t) > 60 and not any(x in t.lower() for x in skip_words):
            aciklama = t
            break

    # RESIMLER - CloudFront URL'leri bul
    cdn_resimler = set()

    for img in soup.find_all('img'):
        for attr in ('src', 'data-src', 'data-lazy-src', 'data-original', 'data-img'):
            val = img.get(attr, '') or ''
            if 'cloudfront.net' in val and 'logo' not in val.lower():
                cdn_resimler.add(re.sub(r'-\d+x\d+\.', '.', val))

    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'cloudfront.net' in href and any(href.endswith(e) for e in
                ('.jpg','.jpeg','.png','.webp')):
            cdn_resimler.add(re.sub(r'-\d+x\d+\.', '.', href))

    # Ham HTML'de regex tarama
    for m_obj in re.finditer(
            r'https://[^\s"\'<>]+cloudfront\.net[^\s"\'<>]+\.(?:jpg|jpeg|png|webp)',
            resp.text):
        url = re.sub(r'-\d+x\d+\.', '.', m_obj.group())
        if 'logo' not in url.lower():
            cdn_resimler.add(url)

    cdn_resimler = sorted(cdn_resimler)

    # RESIM YOLLARI
    if download_images and cdn_resimler:
        resimler = []
        for idx, img_url in enumerate(cdn_resimler, 1):
            lokal = download_image(session, img_url, en_slug, idx)
            resimler.append(lokal)
            time.sleep(0.2)
    elif cdn_resimler:
        resimler = list(cdn_resimler)
    else:
        resimler = _mevcut_resim_bul(en_slug)

    # OZELLIK GRUPLARI
    ozellik_gruplari = {
        "STANDART AKSESUARLAR": [],
        "OPSIYONEL AKSESUARLAR": [],
        "GENEL OZELLIKLER": [],
    }

    kw_map = {
        "STANDART":  "STANDART AKSESUARLAR",
        "STANDARD":  "STANDART AKSESUARLAR",
        "OPTIONAL":  "OPSIYONEL AKSESUARLAR",
        "OPSIYONEL": "OPSIYONEL AKSESUARLAR",
        "GENERAL":   "GENEL OZELLIKLER",
        "GENEL":     "GENEL OZELLIKLER",
        "TECHNICAL": "GENEL OZELLIKLER",
        "TEKNIK":    "GENEL OZELLIKLER",
        "FEATURES":  "GENEL OZELLIKLER",
        "SPECIFICATIONS": "GENEL OZELLIKLER",
    }

    for hx in soup.find_all(['h2','h3','h4']):
        baslik = hx.get_text(strip=True).upper()
        grup = next((v for k, v in kw_map.items() if k in baslik), None)
        if not grup:
            continue
        ul = hx.find_next_sibling('ul')
        if ul:
            items = [li.get_text(strip=True) for li in ul.find_all('li')
                     if li.get_text(strip=True)]
            ozellik_gruplari[grup].extend(items)

    kategoriler, alt_kategoriler = kategori_belirle(en_slug)

    return {
        "slug": en_slug,
        "diller": {
            "tr": {
                "isim": isim,
                "aciklama": aciklama,
                "resimler": resimler,
                "ozellik_gruplari": ozellik_gruplari,
                "piktogramlar": {}
            }
        },
        "kategoriler": kategoriler,
        "alt_kategoriler": alt_kategoriler,
    }

def _mevcut_resim_bul(en_slug):
    if not IMG_DIR.exists():
        return []
    parts = en_slug.split('-')
    kod = []
    for i, p in enumerate(parts):
        kod.append(p)
        if any(c.isdigit() for c in p):
            if i+1 < len(parts) and len(parts[i+1]) <= 2 and parts[i+1].isalpha():
                if parts[i+1].lower() != kod[0].lower():
                    kod.append(parts[i+1])
            break
    model_k = "-".join(kod).lower()

    return [
        f"/images/yilmaz/{f.name}"
        for f in sorted(IMG_DIR.iterdir())
        if f.is_file() and f.stat().st_size > 1000
        and (f.name.lower().startswith(model_k + "-")
             or f.name.lower().startswith(model_k + "."))
    ]

# ===================================================
# ANA AKIS
# ===================================================
def main():
    print()
    print("=" * 64)
    print("  YILMAZ MAKINE GUNCELLEYICI v4.1")
    print("  Sitemap | EN resim isimleri | 403 bypass")
    print("=" * 64)
    print()

    test_mode       = "--test"    in sys.argv
    download_images = "--images"  in sys.argv
    skip_existing   = "--skip"    in sys.argv

    if test_mode:       log("TEST MODU - Ilk 3 makine", "WARN")
    if download_images: log("Resimler indirilecek (EN isimli)", "WARN")
    if skip_existing:   log("Mevcut slug'lar atlanacak", "WARN")

    mevcut_sluglar = set()
    if skip_existing and JSON_OUTPUT.exists():
        with open(JSON_OUTPUT, 'r', encoding='utf-8') as f:
            mevcut_sluglar = {m["slug"] for m in json.load(f)}
        log(f"Mevcut: {len(mevcut_sluglar)} slug atlanacak")

    session = build_session()
    log("Session hazir", "OK")

    tum_urls = sitemap_urls(session)

    if not tum_urls:
        log("Hic URL bulunamadi! Internet baglantisi ve sitemap URL'lerini kontrol et.", "ERR")
        sys.exit(1)

    if skip_existing:
        tum_urls = {k: v for k, v in tum_urls.items() if k not in mevcut_sluglar}
        log(f"Skip sonrasi: {len(tum_urls)} makine islenecek")

    items = list(tum_urls.items())
    if test_mode:
        items = items[:3]

    log(f"=== {len(items)} MAKINE ISLENIYOR ===", "SCAN")
    makineler = []
    hatali = 0

    for i, (en_slug, urls) in enumerate(items, 1):
        log(f"[{i}/{len(items)}] {en_slug}")
        time.sleep(DELAY)

        m = parse_page(session, en_slug, urls, download_images)

        if m:
            makineler.append(m)
            r_sayi = len(m['diller']['tr']['resimler'])
            o_sayi = sum(len(v) for v in m['diller']['tr']['ozellik_gruplari'].values())
            vlog(f"  -> {m['diller']['tr']['isim']} | {r_sayi} resim | {o_sayi} ozellik")
        else:
            hatali += 1

    if skip_existing and mevcut_sluglar and JSON_OUTPUT.exists():
        with open(JSON_OUTPUT, 'r', encoding='utf-8') as f:
            eski = json.load(f)
        yeni_s = {m["slug"] for m in makineler}
        makineler = [m for m in eski if m["slug"] not in yeni_s] + makineler

    makineler.sort(key=lambda m: m["slug"])

    if JSON_OUTPUT.exists():
        shutil.copy2(JSON_OUTPUT, JSON_BACKUP)
        log(f"Yedeklendi -> {JSON_BACKUP.name}", "OK")

    JSON_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(makineler, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 64)
    print(f"  TAMAMLANDI")
    print(f"  Toplam makine  : {len(makineler)}")
    print(f"  Hatali         : {hatali}")
    mode_str = "INDIRILDI (EN isimli)" if download_images else "CDN URL saklandi"
    print(f"  Resim modu     : {mode_str}")
    print("=" * 64)

    alu = sum(1 for m in makineler if "Aluminyum" in m.get("kategoriler",[]))
    pvc = sum(1 for m in makineler if "PVC" in m.get("kategoriler",[]))
    print(f"\n  Aluminyum: {alu} | PVC: {pvc}")

    kat_sayac = {}
    for m in makineler:
        for ak in m.get("alt_kategoriler",[]):
            key = f"{'/'.join(m.get('kategoriler',['?']))} / {ak}"
            kat_sayac[key] = kat_sayac.get(key, 0) + 1

    print("\n  Kategori dagilimi:")
    for k, v in sorted(kat_sayac.items(), key=lambda x: -x[1]):
        print(f"    {k:<42} {v:>3}  {'#'*min(v,25)}")

    if download_images and IMG_DIR.exists():
        print()
        log("Sahte dosyalar temizleniyor (< 1KB)...", "SCAN")
        silinen = sum(1 for f in IMG_DIR.iterdir()
                     if f.is_file() and f.stat().st_size < 1000
                     and not f.unlink())
        if silinen: log(f"{silinen} sahte dosya silindi", "OK")

    print(f"\n  Sonraki adim: npx astro dev")
    print()


if __name__ == "__main__":
    main()
