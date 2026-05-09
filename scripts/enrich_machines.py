#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JAGUAR LTD - machines.json ZENGİNLEŞTİRİCİ
Her Yılmaz makinesi için teknik tablo + PDF katalog linkini çeker.
Sadece eksik olanları günceller (zaten doluysa atlar).

Kullanım:
  python enrich_machines.py           # tümünü işle
  python enrich_machines.py --test    # ilk 3 makine
  python enrich_machines.py --slug ack-420-s-up-cutting-saw-machine
"""
import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

import requests
from bs4 import BeautifulSoup
import json, re, time, shutil
from pathlib import Path
from urllib.parse import urljoin
from datetime import datetime

BASE    = "https://www.yilmazmachine.com.tr"
JSON    = Path(__file__).parent.parent / "src" / "data" / "machines.json"
DELAY   = 1.8
RETRIES = 3


def build_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"{BASE}/en/",
        "Connection": "keep-alive",
    })
    try:
        s.get(f"{BASE}/en/", timeout=15, allow_redirects=True)
    except Exception:
        pass
    return s


def safe_get(session, url):
    for attempt in range(RETRIES):
        try:
            r = session.get(url, timeout=30, allow_redirects=True)
            if r.status_code == 200:
                return r
            elif r.status_code == 403:
                print(f"    [!] 403 — bekleniyor ({attempt+1}/{RETRIES})")
                time.sleep(3 * (attempt + 1))
            else:
                print(f"    [!] HTTP {r.status_code}")
                return None
        except requests.RequestException as e:
            print(f"    [!] Hata: {e}")
            time.sleep(2)
    return None


KEY_MAP = {
    "elektrik":         "Motor Power",
    "donus_hizi":       "Blade Speed",
    "cap":              "Blade Diameter",
    "debi":             "Air Consumption",
    "basinc":           "Air Pressure",
    "agirlik":          "Weight",
    "urun_agirligi":    "Weight",
    "boyut":            "Dimensions",
    "boyutlar":         "Dimensions",
    "kesme":            "Cutting Capacity",
    "kesme_kapasitesi": "Cutting Capacity",
    "kuvvet":           "Force",
    "hiz":              "Speed",
    "voltaj":           "Voltage",
    "guc":              "Power",
    "motor":            "Motor",
    "sicaklik":         "Temperature",
    "devir":            "RPM",
    "tabla":            "Table Size",
    "ilerleme":         "Feed Rate",
    "stroke":           "Stroke",
    "pres_kuvveti":     "Press Force",
}


def extract_technical_data(soup):
    """Yılmaz 'tech-specs' div'inden teknik tablo verilerini çeker."""
    data = {}

    # Yöntem 1 (birincil): div.tech-specs → div.table-row-{key} → div.text-row
    tech_div = soup.find('div', class_='tech-specs')
    if tech_div:
        for col in tech_div.find_all('div', class_=True):
            classes = col.get('class', [])
            raw_key = next((c.replace('table-row-', '') for c in classes if c.startswith('table-row-')), None)
            if not raw_key:
                continue
            text_row = col.find('div', class_='text-row')
            val = text_row.get_text(strip=True) if text_row else ''
            if val:
                label = KEY_MAP.get(raw_key, raw_key.replace('_', ' ').title())
                data[label] = val
        if data:
            return data

    # Yöntem 2 (fallback): <table> etiketleri
    for table in soup.find_all('table'):
        for row in table.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                val = cells[1].get_text(strip=True)
                # Sadece sayısal değer içerenleri al
                if key and val and len(key) < 50 and re.search(r'\d', val):
                    data[key] = val

    return data


def extract_catalog(soup, page_url):
    """'Catalogue Page' metnine sahip PDF linkini bulur."""
    # Yöntem 1: "Catalogue Page" metnli + .pdf href
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True).lower()
        if '.pdf' in href.lower() and ('catalogue page' in text or 'catalog page' in text):
            return href if href.startswith('http') else urljoin(page_url, href)

    # Yöntem 2: cloudfront .pdf linki (ilk bulduğu)
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '.pdf' in href.lower() and 'cloudfront' in href:
            return href

    # Yöntem 3: Herhangi bir .pdf linki ("/en/media/catalogs/" gibi dizinleri hariç tut)
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.lower().endswith('.pdf'):
            return href if href.startswith('http') else urljoin(page_url, href)

    return None


def enrich_one(session, machine):
    """Tek makineyi zenginleştirir. Değişen alan varsa True döner."""
    slug = machine['slug']
    en   = machine.setdefault('diller', {}).setdefault('en', {})

    needs_tech = not en.get('technical_data')
    needs_cat  = not en.get('catalog')

    if not needs_tech and not needs_cat:
        return False

    page_url = f"{BASE}/en/products/{slug}/"
    r = safe_get(session, page_url)
    if not r:
        print(f"    [X] Sayfa açılamadı: {page_url}")
        return False

    soup = BeautifulSoup(r.content, 'html.parser')
    changed = False

    if needs_tech:
        tech = extract_technical_data(soup)
        en['technical_data'] = tech
        changed = True
        print(f"    + teknik_tablo: {len(tech)} alan")

    if needs_cat:
        cat = extract_catalog(soup, page_url)
        en['catalog'] = cat
        changed = True
        if cat:
            print(f"    + katalog: ...{cat[-60:]}")
        else:
            print(f"    - katalog: bulunamadı")

    return changed


def main():
    test_mode  = '--test'  in sys.argv
    only_slug  = None
    if '--slug' in sys.argv:
        idx = sys.argv.index('--slug')
        if idx + 1 < len(sys.argv):
            only_slug = sys.argv[idx + 1]

    print()
    print("=" * 60)
    print("  JAGUAR LTD — machines.json ZENGİNLEŞTİRİCİ")
    print("=" * 60)

    with open(JSON, 'r', encoding='utf-8') as f:
        machines = json.load(f)

    # Yedek
    yedek = JSON.parent / f"machines_enrich_yedek_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    shutil.copy2(JSON, yedek)
    print(f"  Yedek: {yedek.name}")
    print(f"  Toplam: {len(machines)} makine\n")

    if only_slug:
        machines_to_process = [m for m in machines if m['slug'] == only_slug]
    elif test_mode:
        machines_to_process = machines[:3]
    else:
        machines_to_process = machines

    session = build_session()
    updated = 0

    for i, m in enumerate(machines_to_process, 1):
        slug = m['slug']
        en   = m.get('diller', {}).get('en', {})
        has_tech = bool(en.get('technical_data'))
        has_cat  = bool(en.get('catalog'))

        if has_tech and has_cat:
            print(f"[{i:>3}/{len(machines_to_process)}] {slug[:55]} — atlandı")
            continue

        missing = []
        if not has_tech: missing.append('teknik')
        if not has_cat:  missing.append('katalog')
        print(f"[{i:>3}/{len(machines_to_process)}] {slug[:55]}  ({', '.join(missing)} eksik)")

        time.sleep(DELAY)

        if enrich_one(session, m):
            updated += 1

    # Kaydet
    with open(JSON, 'w', encoding='utf-8') as f:
        json.dump(machines, f, ensure_ascii=False, indent=2)

    # Özet
    has_t = sum(1 for x in machines if x.get('diller',{}).get('en',{}).get('technical_data'))
    has_c = sum(1 for x in machines if x.get('diller',{}).get('en',{}).get('catalog'))
    print()
    print("=" * 60)
    print(f"  Güncellenen  : {updated} makine")
    print(f"  Teknik tablo : {has_t}/{len(machines)}")
    print(f"  Katalog      : {has_c}/{len(machines)}")
    print(f"  [+] machines.json kaydedildi")
    print()


if __name__ == "__main__":
    main()
