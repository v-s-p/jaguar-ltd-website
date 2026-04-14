#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║  YILMAZ MAKİNE - JAGUAR LTD ENVANTER GÜNCELLEYİCİ v3.0   ║
║  yilmazmachine.com.tr → machines.json                       ║
║  Kenan Ataerk - Jaguar LTD                                  ║
╚══════════════════════════════════════════════════════════════╝

Kullanım:
  python yilmaz_guncelleyici.py              # Tüm ürünleri çek
  python yilmaz_guncelleyici.py --test       # Sadece 3 ürün çek (test modu)
  python yilmaz_guncelleyici.py --download   # Resimleri de indir (CDN yerine lokal)
  python yilmaz_guncelleyici.py --verbose    # Detaylı log

Gereksinimler:
  pip install requests beautifulsoup4
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import sys
import time
import re
import hashlib
from pathlib import Path
from urllib.parse import urljoin, urlparse
from datetime import datetime

# ═══════════════════════════════════════════════════
# YAPILANDIRMA
# ═══════════════════════════════════════════════════

BASE_URL = "https://www.yilmazmachine.com.tr"
LANG_PREFIX = "/en"  # İngilizce sayfalar (TR çevirisi de yapılabilir)

# Kategori sayfaları - buralardan ürün URL'leri keşfedilir
CATEGORY_PAGES = [
    f"{BASE_URL}{LANG_PREFIX}/product-category/aluminium/",
    f"{BASE_URL}{LANG_PREFIX}/product-category/pvc/",
]

# Alt kategori haritası - URL yolundan alt kategori belirleme
ALU_SUBCATEGORY_MAP = {
    "profile-machining": "İŞLEME MERKEZLERİ",
    "machining-center": "İŞLEME MERKEZLERİ",
    "processing-center": "İŞLEME MERKEZLERİ",
    "sheet-plate": "İŞLEME MERKEZLERİ",
    "saw-cutting": "KESİM",
    "double-head-cutting": "KESİM",
    "single-head-cutting": "KESİM",
    "radial-cutting": "KESİM",
    "slicing": "KESİM",
    "v-cutting": "KESİM",
    "portable-cutting": "KESİM",
    "milling": "FREZE",
    "router": "FREZE",
    "corner-crimping": "KÖŞE PRES",
    "end-milling": "KERTME",
    "facade-notching": "KERTME",
    "pressing": "PRES",
    "punch-press": "PRES",
    "transferring": "TAŞIMA",
    "trolley": "TAŞIMA",
    "conveying": "AKTARMA",
    "conveyor": "AKTARMA",
    "swarf-extraction": "TALAŞ TOPLAMA",
    "vacuum-swarf": "TALAŞ TOPLAMA",
    "assembling": "MONTAJ",
    "assembly": "MONTAJ",
    "work-bench": "MONTAJ",
    "work-beanch": "MONTAJ",
    "sash-assembly": "MONTAJ",
}

PVC_SUBCATEGORY_MAP = {
    "processing-center": "İŞLEME MERKEZİ",
    "welding-cleaning": "İŞLEME MERKEZİ",
    "profile-cutting-machining": "İŞLEME MERKEZİ",
    "cleaning": "ÇAPAK ALMA",
    "corner-cleaning": "ÇAPAK ALMA",
    "gasket-milling": "ÇAPAK ALMA",
    "cutting": "KESİM",
    "double-head-cutting": "KESİM",
    "single-head-cutting": "KESİM",
    "glazing-bead": "KESİM",
    "reinforcement-sheet": "KESİM",
    "portable-cutting": "KESİM",
    "milling": "FREZE",
    "router": "FREZE",
    "end-milling": "KERTME",
    "screwdriving": "VİDALAMA",
    "screwdriver": "VİDALAMA",
    "welding": "KAYNAK",
    "transferring": "TAŞIMA",
    "trolley": "TAŞIMA",
    "swarf-extraction": "TALAŞ TOPLAMA",
    "vacuum-swarf": "TALAŞ TOPLAMA",
    "conveying": "AKTARMA",
    "conveyor": "AKTARMA",
    "assembling": "MONTAJ",
    "assembly": "MONTAJ",
}

# Model kodu → alt kategori eşleştirmesi (fallback)
MODEL_SUBCATEGORY_MAP = {
    # İşleme Merkezleri
    "AIM": "İŞLEME MERKEZLERİ", "ALM": "İŞLEME MERKEZLERİ", "PIM": "İŞLEME MERKEZİ",
    "CPM": "İŞLEME MERKEZLERİ", "CCL": "İŞLEME MERKEZİ", "PCC": "İŞLEME MERKEZİ",
    "CNC": "İŞLEME MERKEZLERİ", "NSM": "İŞLEME MERKEZİ",
    # Kesim
    "KD": "KESİM", "DC": "KESİM", "ACK": "KESİM", "SK": "KESİM", "MK": "KESİM",
    "RYK": "KESİM", "KY": "KESİM", "VK": "KESİM", "SCM": "KESİM", "CDC": "KESİM",
    "SDT": "KESİM", "CK": "KESİM",
    # Freze
    "FR": "FREZE", "NCR": "FREZE", "CRM": "FREZE",
    # Köşe Pres
    "KP": "KÖŞE PRES",
    # Kertme / End Milling
    "MEM": "KERTME", "KM": "KERTME", "SNM": "KERTME",
    # Kaynak
    "TK": "KAYNAK", "DK": "KAYNAK",
    # Çapak Alma / Temizleme
    "CA": "ÇAPAK ALMA", "MCA": "ÇAPAK ALMA", "WGM": "ÇAPAK ALMA",
    # Vidalama
    "SM": "VİDALAMA",
    # Pres
    "PYE": "PRES",
    # Taşıma
    "PT": "TAŞIMA", "HP": "TAŞIMA", "VP": "TAŞIMA", "GPT": "TAŞIMA", "GT": "TAŞIMA",
    "PC": "TAŞIMA",
    # Aktarma / Konveyör
    "DKN": "AKTARMA", "SKN": "AKTARMA", "MKN": "AKTARMA", "HDL": "AKTARMA",
    # Talaş Toplama
    "VCE": "TALAŞ TOPLAMA", "GAS": "TALAŞ TOPLAMA",
    # Montaj
    "WAS": "MONTAJ", "WB": "MONTAJ", "PWB": "MONTAJ", "RT": "MONTAJ", "RS": "MONTAJ",
    # Su Tahliye
    "ST": "FREZE",
}

# Dosya yolları (script, Jaguar-ltd proje kökü)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
JSON_OUTPUT = PROJECT_ROOT / "src" / "data" / "machines.json"
JSON_BACKUP = PROJECT_ROOT / "src" / "data" / f"machines_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
IMG_DIR = PROJECT_ROOT / "public" / "images" / "machines"

# HTTP ayarları
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
}
REQUEST_DELAY = 1.2  # Saniye, sunucuyu yormamak için
MAX_RETRIES = 3


# ═══════════════════════════════════════════════════
# YARDIMCI FONKSİYONLAR
# ═══════════════════════════════════════════════════

VERBOSE = "--verbose" in sys.argv or "-v" in sys.argv

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "ℹ️", "OK": "✅", "WARN": "⚠️", "ERR": "❌", "SCAN": "🔍"}.get(level, "  ")
    print(f"  [{timestamp}] {prefix} {msg}")

def vlog(msg):
    """Verbose log — sadece --verbose modunda gösterilir."""
    if VERBOSE:
        log(msg, "SCAN")

def safe_request(url, retries=MAX_RETRIES):
    """Hata toleranslı HTTP GET isteği."""
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            if attempt < retries - 1:
                wait = (attempt + 1) * 2
                vlog(f"Tekrar deneniyor ({attempt+1}/{retries}): {url} — {wait}s bekleniyor...")
                time.sleep(wait)
            else:
                log(f"BAŞARISIZ: {url} — {e}", "ERR")
                return None

def slugify(text):
    """URL-güvenli slug oluştur."""
    text = text.lower().strip()
    # Türkçe karakter dönüşümü
    tr_map = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    text = text.translate(tr_map)
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def url_to_slug(url):
    """Ürün URL'sinden slug çıkar."""
    path = urlparse(url).path.rstrip("/")
    # /en/products/aim-7420 → aim-7420
    slug = path.split("/")[-1]
    return slug

def extract_model_prefix(name):
    """Makine adından model prefix'i çıkar: 'AIM 7420' → 'AIM'"""
    match = re.match(r'^([A-ZÇĞİÖŞÜa-z]+)', name.strip())
    if match:
        return match.group(1).upper()
    return ""

def determine_categories(product_url, product_name, parent_category_url=""):
    """URL ve ürün adından ana kategori ve alt kategori belirle."""
    url_lower = product_url.lower()
    parent_lower = parent_category_url.lower()
    
    # Ana kategori belirleme
    ana_kategori = "Alüminyum"  # Varsayılan
    if "pvc" in parent_lower or "pvc" in url_lower:
        ana_kategori = "PVC"
    elif "aluminium" in parent_lower or "aluminum" in url_lower or "alu" in parent_lower:
        ana_kategori = "Alüminyum"
    
    # Alt kategori belirleme - URL yolundaki ipuçlarını kontrol et
    alt_kategoriler = set()
    subcat_map = PVC_SUBCATEGORY_MAP if ana_kategori == "PVC" else ALU_SUBCATEGORY_MAP
    
    for key, value in subcat_map.items():
        if key in url_lower or key in parent_lower:
            alt_kategoriler.add(value)
    
    # Eğer URL'den bulamadıysak, model kodundan dene
    if not alt_kategoriler:
        prefix = extract_model_prefix(product_name)
        if prefix in MODEL_SUBCATEGORY_MAP:
            alt_kategoriler.add(MODEL_SUBCATEGORY_MAP[prefix])
    
    # Hâlâ boşsa genel kategori ata
    if not alt_kategoriler:
        alt_kategoriler.add("DİĞER")
    
    return [ana_kategori], sorted(list(alt_kategoriler))

def download_image(img_url, output_dir):
    """Resmi indir ve dosya yolunu döndür. CDN URL'si verilirse orijinal kaliteyi al."""
    try:
        # Thumbnail URL'yi orijinale çevir (500x275 gibi boyutlandırılmış → orijinal)
        original_url = re.sub(r'-\d+x\d+\.', '.', img_url)
        
        # Dosya adını URL'den çıkar
        parsed = urlparse(original_url)
        filename = os.path.basename(parsed.path)
        if not filename or '.' not in filename:
            # Hash ile unique isim üret
            filename = hashlib.md5(original_url.encode()).hexdigest()[:12] + ".jpg"
        
        output_path = output_dir / filename
        
        if output_path.exists():
            vlog(f"Zaten var, atlanıyor: {filename}")
            return f"/images/machines/{filename}"
        
        resp = safe_request(original_url)
        if resp and resp.status_code == 200:
            output_path.write_bytes(resp.content)
            vlog(f"İndirildi: {filename} ({len(resp.content)//1024}KB)")
            return f"/images/machines/{filename}"
    except Exception as e:
        vlog(f"Resim indirme hatası: {img_url} — {e}")
    
    return None


# ═══════════════════════════════════════════════════
# ÜRÜN KEŞFİ — Kategori sayfalarından ürün URL'lerini topla
# ═══════════════════════════════════════════════════

def discover_subcategory_pages(category_url):
    """Bir ana kategori sayfasındaki tüm alt kategori link'lerini bul."""
    log(f"Kategori taranıyor: {category_url}", "SCAN")
    resp = safe_request(category_url)
    if not resp:
        return []
    
    soup = BeautifulSoup(resp.content, 'html.parser')
    subcategory_urls = set()
    
    # Sidebar'daki kategori linklerini tara
    for link in soup.find_all('a', href=True):
        href = link['href']
        # product-category altındaki linkleri bul
        if '/product-category/' in href and href != category_url:
            full_url = urljoin(BASE_URL, href)
            if full_url.startswith(BASE_URL):
                subcategory_urls.add(full_url)
    
    log(f"  → {len(subcategory_urls)} alt kategori bulundu", "OK")
    return list(subcategory_urls)

def discover_product_urls(page_url):
    """Bir kategori/alt-kategori sayfasındaki ürün link'lerini bul."""
    resp = safe_request(page_url)
    if not resp:
        return []
    
    soup = BeautifulSoup(resp.content, 'html.parser')
    product_urls = []
    
    # Ürün kartlarındaki linkleri bul
    # Yılmaz Machine sitesinde ürünler /en/products/ altında
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(BASE_URL, href)
        # /en/products/XYZ/ formatındaki linkleri seç
        if re.match(r'https?://www\.yilmazmachine\.com\.tr/en/products/[^/]+/?$', full_url):
            product_urls.append(full_url)
        # Eski format: /en/urunler/XYZ/ veya /urunler/XYZ/
        elif re.match(r'https?://www\.yilmazmachine\.com\.tr(/en)?/urunler/[^/]+/?$', full_url):
            product_urls.append(full_url)
    
    return list(set(product_urls))

def discover_all_products():
    """Tüm kategori sayfalarını tarayarak benzersiz ürün URL'lerini topla."""
    log("═══ ÜRÜN KEŞFİ BAŞLIYOR ═══")
    
    all_products = {}  # URL → parent_category_url
    
    for cat_url in CATEGORY_PAGES:
        time.sleep(REQUEST_DELAY)
        
        # Ana kategori sayfasındaki ürünleri bul
        direct_products = discover_product_urls(cat_url)
        for url in direct_products:
            if url not in all_products:
                all_products[url] = cat_url
        
        # Alt kategori sayfalarını keşfet
        subcategory_urls = discover_subcategory_pages(cat_url)
        
        for sub_url in subcategory_urls:
            time.sleep(REQUEST_DELAY * 0.5)
            sub_products = discover_product_urls(sub_url)
            vlog(f"  {sub_url.split('/')[-2]}: {len(sub_products)} ürün")
            for url in sub_products:
                if url not in all_products:
                    all_products[url] = sub_url  # Alt kategori URL'sini de sakla
    
    log(f"═══ TOPLAM {len(all_products)} BENZERSİZ ÜRÜN BULUNDU ═══", "OK")
    return all_products


# ═══════════════════════════════════════════════════
# ÜRÜN PARSE — Tekil ürün sayfasından veri çıkar
# ═══════════════════════════════════════════════════

def parse_product_page(url, parent_category_url="", download_images=False):
    """Bir ürün sayfasını parse ederek makine verisini JSON formatında döndür."""
    resp = safe_request(url)
    if not resp:
        return None
    
    soup = BeautifulSoup(resp.content, 'html.parser')
    
    # ── Makine Adı ──
    # Breadcrumb'daki son element veya h1 başlığı
    title_tag = soup.find('h1')
    if not title_tag:
        # Breadcrumb'dan dene
        breadcrumbs = soup.find_all('li')
        if breadcrumbs:
            title_tag = breadcrumbs[-1]
    
    makine_adi = ""
    if title_tag:
        makine_adi = title_tag.get_text(strip=True)
    
    # Eğer başlık "Products" gibi genel bir şeyse slug'dan al
    if not makine_adi or makine_adi.lower() in ("products", "ürünler", "aluminium", "pvc"):
        makine_adi = url_to_slug(url).upper().replace("-", " ")
    
    # ── Açıklama ──
    # Ürün açıklaması genellikle galeri sonrasındaki ilk paragrafta
    aciklama = ""
    # Sayfadaki tüm <p> etiketlerini tara, 50 karakterden uzun olanı al
    for p_tag in soup.find_all('p'):
        text = p_tag.get_text(strip=True)
        if len(text) > 50 and not text.startswith(("Loading", "Required", "Full Name", "E-mail")):
            # Form alanlarını ve navigasyon metinlerini atla
            if "consent" not in text.lower() and "cookie" not in text.lower():
                aciklama = text
                break
    
    # ── Galeri Resimleri ──
    resimler = []
    
    # 1. Yöntem: CloudFront CDN linklerini bul (ana galeri)
    for img_tag in soup.find_all('img'):
        src = img_tag.get('src', '') or ''
        # Lazy-loaded resimleri de kontrol et
        data_src = img_tag.get('data-src', '') or img_tag.get('data-lazy-src', '') or ''
        
        img_url = data_src if data_src and 'cloudfront' in data_src else src
        
        if not img_url or 'svg+xml' in img_url:
            continue
        
        if 'cloudfront.net' in img_url and 'wp-content/uploads' in img_url:
            # Thumbnail → orijinal boyut
            original = re.sub(r'-\d+x\d+\.', '.', img_url)
            if original not in resimler:
                resimler.append(original)
    
    # 2. Yöntem: <a> etiketlerinden tam boyut resim linkleri
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if 'cloudfront.net' in href and 'wp-content/uploads' in href:
            if href.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                if href not in resimler:
                    resimler.append(href)
    
    # Resim indirme (opsiyonel)
    if download_images and resimler:
        IMG_DIR.mkdir(parents=True, exist_ok=True)
        lokal_resimler = []
        for img_url in resimler:
            lokal_yol = download_image(img_url, IMG_DIR)
            lokal_resimler.append(lokal_yol if lokal_yol else img_url)
        resimler = lokal_resimler
    
    # ── Özellik Grupları (h3 başlıkları altındaki ul listeleri) ──
    ozellik_gruplari = {}
    
    # h3 etiketlerini tara
    for h3 in soup.find_all('h3'):
        baslik = h3.get_text(strip=True).upper()
        
        # Bilinen özellik grup başlıkları
        target_keywords = [
            "STANDARD", "STANDART", "OPTIONAL", "OPSİYONEL", "OPSIYONEL",
            "GENERAL", "GENEL", "TECHNICAL", "TEKNİK", "TEKNIK",
            "ACCESORIES", "ACCESSORIES", "AKSESUARLAR", "ÖZELLİKLER",
            "FEATURES", "SPECIFICATIONS"
        ]
        
        if any(kw in baslik for kw in target_keywords):
            # Başlığı Türkçeleştir
            tr_baslik = baslik
            if "STANDARD" in baslik or "STANDART" in baslik:
                tr_baslik = "STANDART AKSESUARLAR"
            elif "OPTIONAL" in baslik or "OPSİYONEL" in baslik:
                tr_baslik = "OPSİYONEL AKSESUARLAR"
            elif "GENERAL" in baslik or "GENEL" in baslik:
                tr_baslik = "GENEL ÖZELLİKLER"
            elif "TECHNICAL" in baslik or "TEKNİK" in baslik:
                tr_baslik = "TEKNİK ÖZELLİKLER"
            
            # Başlığın hemen sonrasındaki <ul> listesini bul
            maddeler = []
            next_elem = h3.find_next_sibling()
            while next_elem:
                if next_elem.name == 'ul':
                    for li in next_elem.find_all('li'):
                        madde = li.get_text(strip=True)
                        if madde:
                            maddeler.append(madde)
                    break
                elif next_elem.name in ('h2', 'h3', 'h4'):
                    break  # Bir sonraki başlığa geçtiyse dur
                next_elem = next_elem.find_next_sibling()
            
            if tr_baslik not in ozellik_gruplari:
                ozellik_gruplari[tr_baslik] = maddeler
            else:
                ozellik_gruplari[tr_baslik].extend(maddeler)
    
    # Eğer h3'te bulamadıysak h4'leri de dene (eski format)
    if not ozellik_gruplari:
        for h4 in soup.find_all('h4'):
            baslik = h4.get_text(strip=True).upper()
            target_keywords = ["STANDARD", "STANDART", "OPTIONAL", "GENERAL", "GENEL", "OPSİYONEL"]
            if any(kw in baslik for kw in target_keywords):
                tr_baslik = baslik
                if "STANDARD" in baslik or "STANDART" in baslik:
                    tr_baslik = "STANDART AKSESUARLAR"
                elif "OPTIONAL" in baslik or "OPSİYONEL" in baslik:
                    tr_baslik = "OPSİYONEL AKSESUARLAR"
                elif "GENERAL" in baslik or "GENEL" in baslik:
                    tr_baslik = "GENEL ÖZELLİKLER"
                
                maddeler = []
                ul = h4.find_next_sibling('ul')
                if ul:
                    for li in ul.find_all('li'):
                        madde = li.get_text(strip=True)
                        if madde:
                            maddeler.append(madde)
                
                ozellik_gruplari[tr_baslik] = maddeler
    
    # Boş grupları varsayılan olarak oluştur
    for default_key in ["STANDART AKSESUARLAR", "OPSİYONEL AKSESUARLAR", "GENEL ÖZELLİKLER"]:
        if default_key not in ozellik_gruplari:
            ozellik_gruplari[default_key] = []
    
    # ── Slug ──
    slug = url_to_slug(url)
    
    # ── Kategoriler ──
    kategoriler, alt_kategoriler = determine_categories(url, makine_adi, parent_category_url)
    
    # ── Sonuç JSON ──
    makine = {
        "slug": slug,
        "diller": {
            "tr": {
                "isim": makine_adi,
                "aciklama": aciklama,
                "resimler": resimler,
                "ozellik_gruplari": ozellik_gruplari,
                "piktogramlar": {}
            }
        },
        "kategoriler": kategoriler,
        "alt_kategoriler": alt_kategoriler
    }
    
    return makine


# ═══════════════════════════════════════════════════
# ANA AKIŞ
# ═══════════════════════════════════════════════════

def main():
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  🏭 YILMAZ MAKİNE → JAGUAR LTD ENVANTER GÜNCELLEYİCİ     ║")
    print("║     yilmazmachine.com.tr → machines.json                   ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    test_mode = "--test" in sys.argv
    download_images = "--download" in sys.argv
    
    if test_mode:
        log("⚡ TEST MODU — Sadece ilk 3 ürün çekilecek", "WARN")
    if download_images:
        log("📥 Resimler de lokal olarak indirilecek", "WARN")
    
    # 1. Ürün URL'lerini keşfet
    all_products = discover_all_products()
    
    if not all_products:
        log("Hiç ürün bulunamadı! Site yapısı değişmiş olabilir.", "ERR")
        sys.exit(1)
    
    product_list = list(all_products.items())
    
    if test_mode:
        product_list = product_list[:3]
        log(f"Test modu: {len(product_list)} ürün işlenecek")
    
    # 2. Her ürünü parse et
    log(f"═══ {len(product_list)} ÜRÜN PARSE EDİLİYOR ═══")
    tum_makineler = []
    hatali_sayisi = 0
    
    for i, (product_url, parent_cat_url) in enumerate(product_list, 1):
        slug = url_to_slug(product_url)
        log(f"[{i}/{len(product_list)}] {slug}")
        
        time.sleep(REQUEST_DELAY)
        
        makine = parse_product_page(product_url, parent_cat_url, download_images)
        
        if makine:
            tum_makineler.append(makine)
            isim = makine['diller']['tr']['isim']
            resim_sayisi = len(makine['diller']['tr']['resimler'])
            ozellik_sayisi = sum(len(v) for v in makine['diller']['tr']['ozellik_gruplari'].values())
            vlog(f"  → {isim} | {resim_sayisi} resim | {ozellik_sayisi} özellik | {makine['alt_kategoriler']}")
        else:
            hatali_sayisi += 1
            log(f"  → PARSE BAŞARISIZ: {product_url}", "WARN")
    
    # 3. Slug'a göre sırala
    tum_makineler.sort(key=lambda m: m['slug'])
    
    # 4. Mevcut dosyayı yedekle
    if JSON_OUTPUT.exists():
        try:
            import shutil
            shutil.copy2(JSON_OUTPUT, JSON_BACKUP)
            log(f"Mevcut dosya yedeklendi → {JSON_BACKUP.name}", "OK")
        except Exception as e:
            log(f"Yedekleme hatası: {e}", "WARN")
    
    # 5. JSON dosyasını yaz
    JSON_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(tum_makineler, f, ensure_ascii=False, indent=2)
    
    # 6. Rapor
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print(f"║  ✅ GÜNCELLEME TAMAMLANDI                                  ║")
    print(f"║  📊 Toplam makine: {len(tum_makineler):>4}                                  ║")
    print(f"║  ❌ Hatalı:        {hatali_sayisi:>4}                                  ║")
    print(f"║  📁 Çıktı: {str(JSON_OUTPUT.name):>20}                       ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    # Kategori özeti
    alu_count = sum(1 for m in tum_makineler if "Alüminyum" in m.get('kategoriler', []))
    pvc_count = sum(1 for m in tum_makineler if "PVC" in m.get('kategoriler', []))
    print(f"\n  📊 Alüminyum: {alu_count} | PVC: {pvc_count}")
    
    # Alt kategori dağılımı
    alt_kat_dagilim = {}
    for m in tum_makineler:
        for ak in m.get('alt_kategoriler', []):
            alt_kat_dagilim[ak] = alt_kat_dagilim.get(ak, 0) + 1
    
    if alt_kat_dagilim:
        print("\n  📋 Alt Kategori Dağılımı:")
        for kat, sayi in sorted(alt_kat_dagilim.items(), key=lambda x: -x[1]):
            bar = "█" * min(sayi, 30)
            print(f"     {kat:.<25} {sayi:>3} {bar}")
    
    print(f"\n  💡 Sonraki adım: 'npx astro build' ile siteyi yeniden oluştur!")
    print()


if __name__ == "__main__":
    main()