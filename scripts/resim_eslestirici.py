#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JAGUAR LTD - LOKAL RESIM ESLESTIRICI v1.0
yilmaz.json'daki bozuk CDN logo.svg resimlerini
public/images/yilmaz/ klasoründeki lokal dosyalarla degistirir.

Kullanim:
  python resim_eslestirici.py          # Gercek calistir
  python resim_eslestirici.py --dry    # Sadece rapor
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
IMG_DIR      = PROJECT_ROOT / "public" / "images" / "machines"
YEDEK_PATH   = PROJECT_ROOT / "src" / "data" / f"machines_resim_yedek_{datetime.now().strftime('%Y%m%d_%H%M')}.json"

def model_kod(slug):
    """
    EN slug'dan model kodunu cikar:
    ack-420-s-up-cutting-saw-machine  -> ack-420-s
    kd-350-d-miter-saw-machine        -> kd-350-d
    aim-7510-aluminium-profile-...    -> aim-7510
    fr-223-fr-223s-portable-...       -> fr-223
    """
    parts = slug.split("-")
    result = []
    for i, p in enumerate(parts):
        result.append(p)
        if any(c.isdigit() for c in p):
            # Sonraki parca varsa ve tek/cift harf suffix ise al
            if i+1 < len(parts) and len(parts[i+1]) <= 2 and parts[i+1].isalpha():
                # Ama ayni slug tekrari degilse (fr-223-fr gibi)
                if parts[i+1] != result[0]:
                    result.append(parts[i+1])
            break
    return "-".join(result)

def lokal_resim_bul(model_k, img_dir):
    """
    model_k ornegi: ack-420-s
    img_dir iceriginde: ack-420-s-alttan-cikma-kesme-makinesi-1.png gibi dosyalar arar
    Sirali liste doner: ['/images/yilmaz/ack-420-s-...-1.png', ...]
    """
    if not img_dir.exists():
        return []
    
    bulunanlar = []
    for f in sorted(img_dir.iterdir()):
        if not f.is_file():
            continue
        fname = f.name.lower()
        # Dosya adi model koduyla basliyor mu?
        if fname.startswith(model_k + "-") or fname.startswith(model_k + "."):
            bulunanlar.append(f"/images/yilmaz/{f.name}")
    
    return bulunanlar

def is_broken(resimler):
    """Resim listesi bozuk mu? (logo.svg veya bos)"""
    if not resimler:
        return True
    return "logo.sv" in resimler[0] or resimler[0].endswith("logo.svg")

def main():
    dry_run = "--dry" in sys.argv

    print()
    print("=" * 60)
    print("  LOKAL RESIM ESLESTIRICI v1.0")
    print("=" * 60)
    print()

    if not JSON_PATH.exists():
        print(f"  [X] Bulunamadi: {JSON_PATH}")
        return
    if not IMG_DIR.exists():
        print(f"  [X] Resim klasoru yok: {IMG_DIR}")
        return

    lokal_dosyalar = list(IMG_DIR.iterdir())
    print(f"  [i] {len(lokal_dosyalar)} lokal resim dosyasi mevcut")

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        makineler = json.load(f)
    print(f"  [i] {len(makineler)} makine okundu")

    if not dry_run:
        shutil.copy2(JSON_PATH, YEDEK_PATH)
        print(f"  [i] Yedeklendi -> {YEDEK_PATH.name}")

    eslesti = 0
    eslesmedi = 0
    zaten_iyi = 0

    print()
    for m in makineler:
        slug = m["slug"]
        tr = m.get("diller", {}).get("tr", {})
        resimler = tr.get("resimler", [])

        # Zaten iyi mi?
        if not is_broken(resimler):
            zaten_iyi += 1
            continue

        # Model kodu bul
        mk = model_kod(slug)

        # Lokal resim ara
        lokal = lokal_resim_bul(mk, IMG_DIR)

        if lokal:
            if not dry_run:
                # Tum dillerin resimlerini guncelle
                for dil_verisi in m.get("diller", {}).values():
                    dil_verisi["resimler"] = lokal
            eslesti += 1
            print(f"  [+] {slug[:45]:<45} -> {len(lokal)} resim ({mk})")
        else:
            eslesmedi += 1
            print(f"  [!] ESLESME YOK: {slug} (model: {mk})")

    if not dry_run:
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(makineler, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 60)
    print(f"  Eslesti      : {eslesti}")
    print(f"  Eslesemedi   : {eslesmedi}")
    print(f"  Zaten iyi    : {zaten_iyi}")
    print(f"  Toplam       : {len(makineler)}")

    if eslesmedi > 0:
        print()
        print("  [!] Uyari: Eslesemeyen makineler CDN'den gelecek.")
        print("      yilmaz_guncelleyici.py --download ile indirebilirsin.")

    if dry_run:
        print("\n  [DRY RUN] - Dosya degistirilmedi")
    else:
        print(f"\n  [+] yilmaz.json guncellendi")
        print("  Sonraki adim: npx astro dev")
    print()

if __name__ == "__main__":
    main()
