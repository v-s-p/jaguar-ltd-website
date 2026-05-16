#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JAGUAR LTD - RESIM TEMIZLEYICI v1.0
1. JSON'daki sahte/bozuk resim yollarini kaldirir (57B dosyalar + URL-encoded isimler)
2. Rapor verir

Kullanim:
  python resim_temizle.py --dry    # Sadece rapor
  python resim_temizle.py          # Uygula
"""

import sys, io, json, os, shutil, re
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SCRIPT_DIR   = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
JSON_PATH    = PROJECT_ROOT / "src" / "data" / "yilmaz.json"
IMG_DIR      = PROJECT_ROOT / "public" / "images" / "machines"
YEDEK_PATH   = PROJECT_ROOT / "src" / "data" / f"machines_temiz_yedek_{datetime.now().strftime('%Y%m%d_%H%M')}.json"

MIN_BOYUT = 1000  # 57 B sahte dosyalari atla

def is_broken(img_path_str):
    """Resim yolu bozuk mu?"""
    # URL-encoded karakterler (% ile) - Kiril/Bulgarca dosya adi
    if '%' in img_path_str:
        return True, "url-encoded"
    # Disk'te 57B sahte mi?
    fname = img_path_str.lstrip("/images/yilmaz/")
    fpath = IMG_DIR / fname
    if fpath.exists() and fpath.stat().st_size < MIN_BOYUT:
        return True, f"sahte ({fpath.stat().st_size}B)"
    if not fpath.exists():
        return True, "dosya yok"
    return False, ""

def main():
    dry = "--dry" in sys.argv

    print()
    print("=" * 56)
    print("  RESIM TEMIZLEYICI v1.0")
    print("=" * 56)
    print()

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"  [i] {len(data)} makine")

    if not dry:
        shutil.copy2(JSON_PATH, YEDEK_PATH)
        print(f"  [i] Yedeklendi -> {YEDEK_PATH.name}")

    toplam_kaldirilan = 0
    etkilenen_makine = 0

    for m in data:
        isim = m["diller"]["tr"]["isim"]
        temizler = []
        kaldirilanlar = []

        for r in m["diller"]["tr"].get("resimler", []):
            broken, neden = is_broken(r)
            if broken:
                kaldirilanlar.append((r, neden))
            else:
                temizler.append(r)

        if kaldirilanlar:
            etkilenen_makine += 1
            toplam_kaldirilan += len(kaldirilanlar)
            print(f"\n  [{isim}]")
            for r, neden in kaldirilanlar:
                fname = r.split("/")[-1][:50]
                print(f"    - KALDIRILDI ({neden}): {fname}")
            print(f"    Kalan resim: {len(temizler)}")

            if not dry:
                m["diller"]["tr"]["resimler"] = temizler

    if not dry and etkilenen_makine > 0:
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 56)
    print(f"  Etkilenen makine  : {etkilenen_makine}")
    print(f"  Kaldirilan resim  : {toplam_kaldirilan}")

    if dry:
        print("\n  [DRY RUN] - Dosya degistirilmedi")
    else:
        print("\n  [+] yilmaz.json guncellendi")
    print()

    # 57B sahte dosyalar hakkinda bilgi
    print("  NOT: 57B sahte dosyalar disk'te duruyor.")
    print("  Silmek icin: python resim_temizle.py --sil-sahte")
    print()

    if "--sil-sahte" in sys.argv:
        print("  Sahte dosyalar siliniyor...")
        silinen = 0
        for f in IMG_DIR.iterdir():
            if f.is_file() and f.stat().st_size < MIN_BOYUT:
                print(f"    SILINDI: {f.name}")
                f.unlink()
                silinen += 1
        print(f"  {silinen} sahte dosya silindi.")

if __name__ == "__main__":
    main()
