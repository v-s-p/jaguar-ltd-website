#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JAGUAR LTD - KATEGORI ZENGINLESTIRICI v3.1
Tek ve cift kategorili dogru dagilim.

Kullanim:
  python zenginlestirici.py
  python zenginlestirici.py --dry
"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json, re, shutil
from pathlib import Path
from datetime import datetime

SCRIPT_DIR   = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
JSON_PATH    = PROJECT_ROOT / "src" / "data" / "yilmaz.json"
YEDEK_PATH   = PROJECT_ROOT / "src" / "data" / f"machines_zengin_yedek_{datetime.now().strftime('%Y%m%d_%H%M')}.json"

# ===================================================
# SADECE ALUMINYUM
# Isleme merkezleri ve aluminyuma ozel makineler
# ===================================================
SADECE_ALU = {
    "AIM": "ISLEME MERKEZLERI",
    "ALM": "ISLEME MERKEZLERI",
    "CPM": "ISLEME MERKEZLERI",  # Kompozit panel
    "KP":  "KOSE PRES",
    "PYE": "PRES",
    "SNM": "KERTME",             # Aluminyum cephe kertme
}

# ===================================================
# SADECE PVC
# ===================================================
SADECE_PVC = {
    "PIM": "ISLEME MERKEZI",
    "CCL": "ISLEME MERKEZI",
    "PCC": "ISLEME MERKEZI",
    "CNC": "ISLEME MERKEZI",
    "TK":  "KAYNAK",
    "DK":  "KAYNAK",
    "CA":  "CAPAK ALMA",
    "MCA": "CAPAK ALMA",
    "WGM": "CAPAK ALMA",
    "SM":  "VIDALAMA",
    "CK":  "KESIM",              # PVC cita kesme
    "ST":  "FREZE",              # PVC su tahliye
}

# ===================================================
# HER IKI KATEGORI - ALU + PVC
# Yilmaz sitesinde her iki listede de gorunenler
# ===================================================
CIFT_ALT = {
    # Kesim - hem alu hem pvc profil keser
    "KD":  "KESIM",
    "DC":  "KESIM",
    "ACK": "KESIM",
    "MK":  "KESIM",
    "RYK": "KESIM",
    "KY":  "KESIM",
    "VK":  "KESIM",
    "CDC": "KESIM",
    "SCM": "KESIM",
    "SK":  "KESIM",
    "SDT": "KESIM",
    # Freze / Router
    "FR":  "FREZE",
    "CRM": "FREZE",
    "NCR": "FREZE",
    # Kertme / End Milling
    "KM":  "KERTME",
    "MEM": "KERTME",
    # Tasima / Trolley
    "PT":  "TASIMA",
    "HP":  "TASIMA",
    "VP":  "TASIMA",
    "GPT": "TASIMA",
    "GT":  "TASIMA",
    "PC":  "TASIMA",
    # Aktarma / Konveyor
    "DKN": "AKTARMA",
    "SKN": "AKTARMA",
    "MKN": "AKTARMA",
    "HDL": "AKTARMA",
    # Talas Toplama
    "VCE": "TALAS TOPLAMA",
    "GAS": "TALAS TOPLAMA",
    # Montaj / Assembly
    "WAS": "MONTAJ",
    "WB":  "MONTAJ",
    "PWB": "MONTAJ",
    "RT":  "MONTAJ",
    "RS":  "MONTAJ",
    "NSM": "MONTAJ",
}

# Slug bazli ozel atamalar (prefix yetersiz kalinca)
OZEL = {
    "vce-1570":  (["PVC"], "TALAS TOPLAMA"),  # Kucuk vakum - sadece PVC
    "gas-301":   (["PVC"], "TALAS TOPLAMA"),  # Kucuk vakum - sadece PVC
    "cnc-609":   (["PVC"], "ISLEME MERKEZI"),
    "cnc-611":   (["PVC"], "ISLEME MERKEZI"),
    "pim-6508-se": (["PVC"], "ISLEME MERKEZI"),
    "cpm-4150-s":  (["Aluminyum"], "ISLEME MERKEZLERI"),
    "cpm-6161-double-station-composite-panel-processing-machine":
                   (["Aluminyum"], "ISLEME MERKEZLERI"),
    "sdt-275":   (["Aluminyum", "PVC"], "KESIM"),
    "rs-1000":   (["Aluminyum", "PVC"], "MONTAJ"),
}

def model_prefix(slug):
    match = re.match(r'^([a-zA-Z]+)', slug)
    return match.group(1).upper() if match else ""

def kategori_belirle(slug):
    slug_lower = slug.lower()

    # 1. Tam slug ozel atama
    if slug_lower in OZEL:
        cats, alt = OZEL[slug_lower]
        return cats, [alt]

    # 2. Slug baslangici ozel atama
    for k, (cats, alt) in OZEL.items():
        if slug_lower.startswith(k + "-") or slug_lower == k:
            return cats, [alt]

    prefix = model_prefix(slug)

    # 3. Sadece Aluminyum
    if prefix in SADECE_ALU:
        return ["Aluminyum"], [SADECE_ALU[prefix]]

    # 4. Sadece PVC
    if prefix in SADECE_PVC:
        return ["PVC"], [SADECE_PVC[prefix]]

    # 5. Her iki kategori
    if prefix in CIFT_ALT:
        return ["Aluminyum", "PVC"], [CIFT_ALT[prefix]]

    # 6. Slug icerigine gore
    if 'pvc' in slug_lower:
        return ["PVC"], ["DIGER"]

    return ["Aluminyum"], ["DIGER"]

def main():
    dry_run = "--dry" in sys.argv

    print()
    print("=" * 60)
    print("  KATEGORI ZENGINLESTIRICI v3.1")
    print("  Tek + Cift kategori dagilimi")
    print("=" * 60)
    print()

    if not JSON_PATH.exists():
        print(f"  [X] Bulunamadi: {JSON_PATH}")
        return

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        makineler = json.load(f)

    print(f"  [i] {len(makineler)} makine okundu")

    if not dry_run:
        shutil.copy2(JSON_PATH, YEDEK_PATH)
        print(f"  [i] Yedeklendi -> {YEDEK_PATH.name}")

    kategori_sayac = {}
    diger_listesi = []
    sadece_alu = sadece_pvc = cift = 0

    for m in makineler:
        slug = m.get("slug", "")
        kategoriler, alt_kategoriler = kategori_belirle(slug)

        m["kategoriler"]     = kategoriler
        m["alt_kategoriler"] = alt_kategoriler

        if "DIGER" in alt_kategoriler:
            diger_listesi.append(slug)

        if len(kategoriler) == 2:
            cift += 1
        elif "Aluminyum" in kategoriler:
            sadece_alu += 1
        else:
            sadece_pvc += 1

        key = f"[{'+'.join(k[0] for k in kategoriler)}] {alt_kategoriler[0]}"
        kategori_sayac[key] = kategori_sayac.get(key, 0) + 1

    if not dry_run:
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(makineler, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 60)
    print(f"  Sadece Aluminyum : {sadece_alu}")
    print(f"  Sadece PVC       : {sadece_pvc}")
    print(f"  Her Ikisi        : {cift}")
    print(f"  Toplam           : {len(makineler)}")
    print(f"  DIGER kalan      : {len(diger_listesi)}")

    if diger_listesi:
        print()
        print("  DIGER KALANLAR:")
        for s in diger_listesi:
            print(f"    {s}")

    print()
    print("  Kategori dagilimi:")
    for kat, sayi in sorted(kategori_sayac.items(), key=lambda x: -x[1]):
        bar = "#" * min(sayi, 25)
        print(f"    {kat:<40} {sayi:>3}  {bar}")

    if dry_run:
        print("\n  [DRY RUN] - Dosya degistirilmedi")
    else:
        print(f"\n  [+] yilmaz.json guncellendi")
        print("  Sonraki adim: npx astro dev")
    print()

if __name__ == "__main__":
    main()
