#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JAGUAR LTD - ISIM + RESIM DUZELTICI v1.0
Iki sorunu tek seferde cozer:
  1. "YILMAZ MACHINE" isimlerini slug'dan turkce isim uretir
  2. Bozuk/logo resimleri lokal dosyalarla degistirir

Kullanim:
  python duzeltici.py --dry    # Sadece rapor
  python duzeltici.py          # Uygula
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
JSON_PATH    = PROJECT_ROOT / "src" / "data" / "machines.json"
IMG_DIR      = PROJECT_ROOT / "public" / "images" / "machines"
YEDEK_PATH   = PROJECT_ROOT / "src" / "data" / f"machines_duzelt_yedek_{datetime.now().strftime('%Y%m%d_%H%M')}.json"

MIN_RESIM_BOYUTU = 1000  # 57 baytlik sahte dosyalari atla

# ===================================================
# ISIM HARITASI - EN slug -> guzel isim
# ===================================================
ISIM_HARITASI = {
    # ACK
    "ack-420-s":  "ACK 420 S",
    "ack-550":    "ACK 550",
    "ack-700":    "ACK 700",
    # AIM
    "aim-3410":   "AIM 3410",
    "aim-4420":   "AIM 4420",
    "aim-7420":   "AIM 7420",
    "aim-7510":   "AIM 7510",
    # ALM
    "alm-6510":   "ALM 6510",
    # CA
    "ca-601":     "CA 601",
    "ca-603":     "CA 603",
    # CCL
    "ccl-1661":   "CCL 1661",
    # CDC
    "cdc-600":    "CDC 600",
    # CK
    "ck-412":     "CK 412",
    # CNC
    "cnc-609":    "CNC 609",
    "cnc-611":    "CNC 611",
    # CPM
    "cpm-4150":   "CPM 4150 S",
    "cpm-6161":   "CPM 6161",
    # CRM
    "crm-201":    "CRM 201 S",
    "crm-250":    "CRM 250 S",
    # DC
    "dc-421-pbs": "DC 421 PBS",
    "dc-421-psd": "DC 421 PSD",
    "dc-550-pb":  "DC 550 PB",
    "dc-550-skh": "DC 550 SKH",
    # DK
    "dk-502":     "DK 502",
    "dk-540":     "DK 540",
    # DKN
    "dkn-300":    "DKN 300-600",
    # FR
    "fr-221":     "FR 221 S",
    "fr-222":     "FR 222",
    "fr-223":     "FR 223",
    "fr-226":     "FR 226 S",
    # GAS
    "gas-301":    "GAS 301",
    # GPT
    "gpt-1000":   "GPT 1000",
    # GT
    "gt-1000":    "GT 1000",
    # HDL
    "hdl-400":    "HDL 400-700",
    # HP
    "hp-1000":    "HP 1000",
    # KD
    "kd-305":     "KD 305",
    "kd-350-d":   "KD 350 D",
    "kd-350-m":   "KD 350 M",
    "kd-350-p":   "KD 350 P",
    "kd-400-d":   "KD 400 D",
    "kd-400-m":   "KD 400 M",
    "kd-400-p":   "KD 400 P",
    "kd-402":     "KD 402 S",
    # KM
    "km-211":     "KM 211",
    "km-212":     "KM 212",
    "km-215":     "KM 215 S",
    # KP
    "kp-110":     "KP 110",
    "kp-130":     "KP 130 CNC",
    "kp-180":     "KP 180",
    # KY
    "ky-305":     "KY 305",
    # MCA
    "mca-801":    "MCA 801",
    # MEM
    "mem-128":    "MEM 128",
    # MK
    "mk-420":     "MK 420",
    # MKN
    "mkn-serisi": "MKN Serisi",
    # NCR
    "ncr-300":    "NCR 300",
    # NSM
    "nsm-352":    "NSM 352-353",
    # PC
    "pc-4000":    "PC 4000",
    # PIM
    "pim-6508":   "PIM 6508 SE",
    "pim-6509":   "PIM 6509",
    # PT
    "pt-1000":    "PT 1000",
    "pt-2000":    "PT 2000",
    # PWB
    "pwb-4100":   "PWB 4100",
    # PYE
    "pye-101":    "PYE 101-104",
    # RS
    "rs-1000":    "RS 1000",
    # RT
    "rt-1000":    "RT 1000",
    # RYK
    "ryk-420-w":  "RYK 420 W",
    "ryk-420":    "RYK 420",
    # SCM
    "scm-420":    "SCM 420 L4-L7",
    # SDT
    "sdt-275":    "SDT 275",
    "sdt-280":    "SDT 280",
    # SK
    "sk-500-d":   "SK 500 D",
    "sk-500":     "SK 500",
    # SKN
    "skn-300":    "SKN 300-600",
    # SM
    "sm-201-sd":  "SM 201 SD",
    "sm-201":     "SM 201",
    "sm-206":     "SM 206",
    # SNM
    "snm-560-m":  "SNM 560 M",
    "snm-560":    "SNM 560 SRV",
    # ST
    "st-264":     "ST 264",
    # TK
    "tk-503":     "TK 503",
    "tk-505":     "TK 505",
    # VCE
    "vce-1570":   "VCE 1570",
    "vce-3500":   "VCE 3500",
    "vce-4000":   "VCE 4000",
    # VK
    "vk-420":     "VK 420",
    # VP
    "vp-1000":    "VP 1000",
    "vp-2000":    "VP 2000",
    # WAS
    "was-1000":   "WAS 1000",
    # WB
    "wb-4000":    "WB 4000",
    # WGM
    "wgm-202":    "WGM 202",
}

def isim_bul(slug):
    """Slug'dan isim bul - uzundan kisaya eslestir."""
    slug_lower = slug.lower()
    # Uzun eslesmeden kisa eslesmeye dogru
    for key in sorted(ISIM_HARITASI.keys(), key=len, reverse=True):
        if slug_lower.startswith(key):
            return ISIM_HARITASI[key]
    # Fallback: ilk 2-3 kelimeyi büyük harfe çevir
    parts = slug.split("-")
    code_parts = []
    for p in parts:
        if any(c.isdigit() for c in p):
            code_parts.append(p.upper())
            # Sonraki parca suffix mi?
            idx = parts.index(p)
            if idx+1 < len(parts) and len(parts[idx+1]) <= 2:
                code_parts.append(parts[idx+1].upper())
            break
        else:
            code_parts.append(p.upper())
    return " ".join(code_parts[:3])

def is_broken_resim(resimler):
    """Resim listesi bozuk mu?"""
    if not resimler:
        return True
    first = resimler[0]
    return "logo.sv" in first or first.endswith("logo.svg") or not first

def lokal_resim_bul(slug, img_dir):
    """
    EN slug'dan model kodu cikartip lokal resimleri bul.
    57 baytlik sahte dosyalari atla.
    """
    if not img_dir.exists():
        return []

    # Model kodu cikart: ack-550-up-cutting -> ack-550
    parts = slug.split("-")
    kod_parcalar = []
    for p in parts:
        kod_parcalar.append(p)
        if any(c.isdigit() for c in p):
            idx = parts.index(p)
            if idx+1 < len(parts) and len(parts[idx+1]) <= 2 and parts[idx+1].isalpha():
                if parts[idx+1] != kod_parcalar[0]:  # fr-223-fr gibi tekrari engelle
                    kod_parcalar.append(parts[idx+1])
            break
    model_k = "-".join(kod_parcalar)

    bulunanlar = []
    for f in sorted(img_dir.iterdir()):
        if not f.is_file():
            continue
        # 57 baytlik sahte dosyalari atla
        if f.stat().st_size < MIN_RESIM_BOYUTU:
            continue
        fname = f.name.lower()
        if fname.startswith(model_k + "-") or fname.startswith(model_k + "."):
            bulunanlar.append(f"/images/machines/{f.name}")

    return bulunanlar

def main():
    dry_run = "--dry" in sys.argv

    print()
    print("=" * 60)
    print("  ISIM + RESIM DUZELTICI v1.0")
    print("=" * 60)
    print()

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        makineler = json.load(f)

    print(f"  [i] {len(makineler)} makine")
    if not dry_run:
        shutil.copy2(JSON_PATH, YEDEK_PATH)
        print(f"  [i] Yedeklendi -> {YEDEK_PATH.name}")

    isim_duzelt = 0
    resim_duzelt = 0
    resim_yok = 0

    for m in makineler:
        slug = m["slug"]
        tr = m.get("diller", {}).get("tr", {})

        # --- ISIM DUZELT ---
        mevcut_isim = tr.get("isim", "")
        if mevcut_isim.upper().strip("®") in ("YILMAZ MACHINE", "YILMAZ"):
            yeni_isim = isim_bul(slug)
            if not dry_run:
                m["diller"]["tr"]["isim"] = yeni_isim
            isim_duzelt += 1
            print(f"  [isim] {slug[:40]:<40} -> {yeni_isim}")

        # --- RESIM DUZELT ---
        resimler = tr.get("resimler", [])
        if is_broken_resim(resimler):
            lokal = lokal_resim_bul(slug, IMG_DIR)
            if lokal:
                if not dry_run:
                    for dil_verisi in m.get("diller", {}).values():
                        dil_verisi["resimler"] = lokal
                resim_duzelt += 1
            else:
                resim_yok += 1
                print(f"  [!resim] {slug} - lokal resim yok!")

    if not dry_run:
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(makineler, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 60)
    print(f"  Isim duzeltildi  : {isim_duzelt}")
    print(f"  Resim duzeltildi : {resim_duzelt}")
    print(f"  Resim bulunamadi : {resim_yok}")
    if dry_run:
        print("\n  [DRY RUN]")
    else:
        print("\n  [+] machines.json guncellendi")
        print("  Sonraki: npx astro dev")
    print()

if __name__ == "__main__":
    main()
