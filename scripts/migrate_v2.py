#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JAGUAR LTD - VERİ MİGRASYONU v1.0
Mevcut yilmaz.json'u yeni mimari formatina donusturur:
  - brand: "yilmaz" eklenir
  - kategoriler: ["Aluminyum"] -> category: "Aluminium"
  - alt_kategoriler: ["KESIM"] -> subcategory: "Cutting"
  - diller.tr -> diller.en (Ingilizce zaten TR'de saklaniyordu)
  - Isimler duzeltilir: "ACK 420 S - Up-Cutting..." -> "ACK 420 S"

Kullanim:
  python migrate_v2.py
"""
import sys, io, json, re, shutil, glob as glob_mod
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SCRIPT_DIR   = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
JSON_IN      = PROJECT_ROOT / "src" / "data" / "yilmaz.json"
JSON_OUT     = PROJECT_ROOT / "src" / "data" / "yilmaz.json"
YEDEK        = PROJECT_ROOT / "src" / "data" / f"machines_v1_yedek_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
IMG_DIR      = PROJECT_ROOT / "public" / "images" / "machines"

# Kategori cevirisi: TR/eski -> EN
KAT_EN = {
    "Aluminyum":  "Aluminium",
    "Alüminyum":  "Aluminium",
    "PVC":        "PVC",
}

ALT_KAT_EN = {
    "KESIM":              "Cutting",
    "ISLEME MERKEZLERI":  "Machining Centers",
    "ISLEME MERKEZI":     "Machining Centers",
    "FREZE":              "Routing & Milling",
    "KOSE PRES":          "Corner Crimping",
    "KERTME":             "End Milling",
    "PRES":               "Punch Press",
    "TASIMA":             "Transport & Storage",
    "AKTARMA":            "Conveyors",
    "TALAS TOPLAMA":      "Swarf Extraction",
    "MONTAJ":             "Assembly",
    "KAYNAK":             "Welding",
    "CAPAK ALMA":         "Corner Cleaning",
    "VIDALAMA":           "Screwdriving",
    "DIGER":              "Other",
}

def get_local_images(slug):
    """Slug'a ait yerel resimleri bul, /images/yilmaz/ yollarını döndür."""
    if not IMG_DIR.exists():
        return []
    matches = []
    for f in IMG_DIR.iterdir():
        if f.stem.startswith(slug + '-') or f.stem == slug:
            matches.append(f)
    def sort_key(f):
        m = re.search(r'-(\d+)$', f.stem)
        return int(m.group(1)) if m else 0
    matches.sort(key=sort_key)
    return [f'/images/yilmaz/{f.name}' for f in matches]


def duzelt_isim(isim):
    """
    "ACK 420 S - Up-Cutting Saw Machine" -> "ACK 420 S"
    "VCE 3500" -> "VCE 3500" (zaten temiz)
    """
    if ' - ' in isim:
        parts = isim.split(' - ')
        first = parts[0].strip()
        # Ilk kisim model kodu ise (buyuk harf + rakam) kullan
        if re.match(r'^[A-Z]{2,6}[\s\d]', first):
            return first
    return isim

def migrate(m):
    """Tek makineyi yeni formata donustur."""
    slug = m["slug"]

    # Eski TR dil verisini EN'e tasI (veri zaten Ingilizce)
    eski_tr = m.get("diller", {}).get("tr", {})

    # Resimler: once yerel dosyalar, yoksa cloudfront'tan kotu goruntuleri filtrele
    local_imgs = get_local_images(slug)
    if local_imgs:
        images = local_imgs
    else:
        raw = eski_tr.get("resimler", [])
        BAD = ('favicon', 'popup', 'logo', 'banner')
        images = [u for u in raw if not any(b in u.lower() for b in BAD)]

    # specs: once ust seviye, sonra diller.tr icindeki
    specs = m.get("specs", eski_tr.get("ozellik_gruplari", {}))

    yeni_en = {
        "name":        duzelt_isim(eski_tr.get("isim", slug.upper())),
        "description": eski_tr.get("aciklama", ""),
        "images":      images,
        "specs":       specs,
    }

    # Kategori donusumu
    eski_kats = m.get("kategoriler", [])
    yeni_kats = [KAT_EN.get(k, k) for k in eski_kats]

    # subcategory: yeni alan adi veya eski alt_kategoriler
    eski_alt = m.get("alt_kategoriler", m.get("subcategory", []))
    if isinstance(eski_alt, str):
        eski_alt = [eski_alt]
    yeni_alt = [ALT_KAT_EN.get(a, a) for a in eski_alt]

    return {
        "slug":        slug,
        "brand":       "yilmaz",
        "categories":  yeni_kats,        # ["Aluminium"] veya ["Aluminium","PVC"]
        "subcategory": yeni_alt[0] if yeni_alt else "Other",
        "diller": {
            "en": yeni_en
        }
    }

def main():
    print()
    print("=" * 56)
    print("  VERİ MİGRASYONU v1.0  (yilmaz.json -> yeni format)")
    print("=" * 56)
    print()

    if not JSON_IN.exists():
        print(f"  [X] Bulunamadi: {JSON_IN}")
        return

    with open(JSON_IN, 'r', encoding='utf-8') as f:
        eski = json.load(f)

    print(f"  [i] {len(eski)} makine okundu")

    # Yedekle
    shutil.copy2(JSON_IN, YEDEK)
    print(f"  [i] Yedeklendi -> {YEDEK.name}")

    # Donustur
    yeni = [migrate(m) for m in eski]

    # Kaydet
    with open(JSON_OUT, 'w', encoding='utf-8') as f:
        json.dump(yeni, f, ensure_ascii=False, indent=2)

    # Rapor
    print()
    print("=" * 56)
    alu = sum(1 for m in yeni if "Aluminium" in m["categories"])
    pvc = sum(1 for m in yeni if "PVC" in m["categories"])
    cift = sum(1 for m in yeni if len(m["categories"]) == 2)
    print(f"  Aluminium    : {alu}")
    print(f"  PVC          : {pvc}")
    print(f"  Both         : {cift}")
    print(f"  Toplam       : {len(yeni)}")

    from collections import Counter
    subkats = Counter(m["subcategory"] for m in yeni)
    print(f"\n  Subcategory dagilimi:")
    for k, v in sorted(subkats.items(), key=lambda x: -x[1]):
        print(f"    {k:<25} {v}")

    print(f"\n  [+] yilmaz.json guncellendi (yeni format)")
    print(f"  Sonraki: Astro sayfalarini guncelle")
    print()

if __name__ == "__main__":
    main()
