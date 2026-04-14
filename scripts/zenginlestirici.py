#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║  JAGUAR LTD — VERİ ZENGİNLEŞTİRİCİ v1.0                  ║
║  KUSURSUZ_MASTER.json → machines.json                       ║
║  Mevcut veriyi kategori + lokal resim yolu ile zenginleştirir║
╚══════════════════════════════════════════════════════════════╝

Sıfırdan indirmez! Mevcut KUSURSUZ_MASTER.json'u okur,
kategorileri ekler, resim yollarını lokal dosyalara eşler,
ve machines.json'a yazar.

Kullanım:
  python zenginlestirici.py                # CDN resimleri kullan
  python zenginlestirici.py --lokal        # Lokal resim yollarını kullan
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════
# YAPILANDIRMA
# ═══════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

KAYNAK = PROJECT_ROOT / "_yedek" / "scripts" / "makine_verileri_KUSURSUZ_MASTER.json"
HEDEF  = PROJECT_ROOT / "src" / "data" / "machines.json"
YEDEK  = PROJECT_ROOT / "src" / "data" / f"machines_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
IMG_DIR = PROJECT_ROOT / "public" / "images" / "machines"

# Model kodu → (ana_kategori, alt_kategori) eşleştirmesi
KATEGORI_HARITASI = {
    # ─── ALÜMİNYUM ───
    "AIM":  ("Alüminyum", "İŞLEME MERKEZLERİ"),
    "ALM":  ("Alüminyum", "İŞLEME MERKEZLERİ"),
    "CPM":  ("Alüminyum", "İŞLEME MERKEZLERİ"),

    "KD":   ("Alüminyum", "KESİM"),
    "DC":   ("Alüminyum", "KESİM"),
    "ACK":  ("Alüminyum", "KESİM"),
    "SK":   ("Alüminyum", "KESİM"),
    "MK":   ("Alüminyum", "KESİM"),
    "RYK":  ("Alüminyum", "KESİM"),
    "KY":   ("Alüminyum", "KESİM"),
    "VK":   ("Alüminyum", "KESİM"),
    "SCM":  ("Alüminyum", "KESİM"),
    "CDC":  ("Alüminyum", "KESİM"),
    "SDT":  ("Alüminyum", "KESİM"),

    "FR":   ("Alüminyum", "FREZE"),
    "NCR":  ("Alüminyum", "FREZE"),
    "CRM":  ("Alüminyum", "FREZE"),

    "KP":   ("Alüminyum", "KÖŞE PRES"),

    "MEM":  ("Alüminyum", "KERTME"),
    "KM":   ("Alüminyum", "KERTME"),
    "SNM":  ("Alüminyum", "KERTME"),

    "PYE":  ("Alüminyum", "PRES"),

    "PT":   ("Alüminyum", "TAŞIMA"),
    "HP":   ("Alüminyum", "TAŞIMA"),
    "VP":   ("Alüminyum", "TAŞIMA"),
    "GPT":  ("Alüminyum", "TAŞIMA"),
    "GT":   ("Alüminyum", "TAŞIMA"),
    "PC":   ("Alüminyum", "TAŞIMA"),

    "DKN":  ("Alüminyum", "AKTARMA"),
    "SKN":  ("Alüminyum", "AKTARMA"),
    "MKN":  ("Alüminyum", "AKTARMA"),
    "HDL":  ("Alüminyum", "AKTARMA"),

    "VCE":  ("Alüminyum", "TALAŞ TOPLAMA"),
    "GAS":  ("Alüminyum", "TALAŞ TOPLAMA"),

    "WAS":  ("Alüminyum", "MONTAJ"),
    "WB":   ("Alüminyum", "MONTAJ"),
    "PWB":  ("Alüminyum", "MONTAJ"),
    "RT":   ("Alüminyum", "MONTAJ"),
    "RS":   ("Alüminyum", "MONTAJ"),

    # ─── PVC ───
    "PIM":  ("PVC", "İŞLEME MERKEZİ"),
    "CCL":  ("PVC", "İŞLEME MERKEZİ"),
    "PCC":  ("PVC", "İŞLEME MERKEZİ"),
    "NSM":  ("PVC", "İŞLEME MERKEZİ"),

    "TK":   ("PVC", "KAYNAK"),
    "DK":   ("PVC", "KAYNAK"),

    "CA":   ("PVC", "ÇAPAK ALMA"),
    "MCA":  ("PVC", "ÇAPAK ALMA"),
    "WGM":  ("PVC", "ÇAPAK ALMA"),

    "SM":   ("PVC", "VİDALAMA"),

    "CK":   ("PVC", "KESİM"),
    "ST":   ("PVC", "FREZE"),
}

# Bazı slug'lar için özel/override kategori atamaları
OZEL_ATAMALAR = {
    "cnc-609":  ("PVC", "İŞLEME MERKEZİ"),
    "cnc-611":  ("PVC", "İŞLEME MERKEZİ"),
    "vce-1570": ("PVC", "TALAŞ TOPLAMA"),
    "vce-3500": ("PVC", "TALAŞ TOPLAMA"),
    "vce-4000": ("PVC", "TALAŞ TOPLAMA"),
    "rs-1000":  ("Alüminyum", "MONTAJ"),
    "sdt-275":  ("Alüminyum", "KESİM"),
    "gas-301":  ("PVC", "TALAŞ TOPLAMA"),
}


# ═══════════════════════════════════════════════════
# FONKSİYONLAR
# ═══════════════════════════════════════════════════

def model_prefix_cek(slug_or_name):
    """Slug veya isimden model prefix çıkar."""
    text = slug_or_name.upper().replace("-", " ")
    match = re.match(r'^([A-Z]+)', text)
    return match.group(1) if match else ""

def kategori_belirle(slug, isim):
    """Slug ve isimden ana kategori + alt kategori belirle."""
    # Önce özel atamalar
    if slug in OZEL_ATAMALAR:
        ana, alt = OZEL_ATAMALAR[slug]
        return [ana], [alt]

    # Model kodundan dene
    prefix = model_prefix_cek(slug)
    if prefix in KATEGORI_HARITASI:
        ana, alt = KATEGORI_HARITASI[prefix]
        return [ana], [alt]

    # İsimden ipucu
    isim_lower = isim.lower()
    if "pvc" in isim_lower:
        return ["PVC"], ["DİĞER"]
    elif "alüm" in isim_lower or "aluminum" in isim_lower:
        return ["Alüminyum"], ["DİĞER"]

    return ["Alüminyum"], ["DİĞER"]

def lokal_resimleri_bul(slug):
    """Slug'a göre lokal resim dosyalarını listele."""
    if not IMG_DIR.exists():
        return []

    resimler = []
    for f in sorted(IMG_DIR.iterdir()):
        if f.is_file() and f.name.startswith(slug):
            resimler.append(f"/images/machines/{f.name}")
    return resimler


def main():
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  🔧 JAGUAR LTD — VERİ ZENGİNLEŞTİRİCİ                    ║")
    print("║     KUSURSUZ_MASTER → machines.json                        ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    lokal_mod = "--lokal" in sys.argv

    # 1. Kaynak dosyayı oku
    if not KAYNAK.exists():
        print(f"  ❌ Kaynak bulunamadı: {KAYNAK}")
        sys.exit(1)

    with open(KAYNAK, 'r', encoding='utf-8') as f:
        makineler = json.load(f)

    print(f"  📖 {len(makineler)} makine okundu: {KAYNAK.name}")

    # 2. Her makineyi zenginleştir
    zengin_makineler = []
    kategori_sayac = {}

    for m in makineler:
        slug = m["slug"]
        tr = m.get("diller", {}).get("tr", {})
        isim = tr.get("isim", slug.upper())

        # Kategorileri ekle
        kategoriler, alt_kategoriler = kategori_belirle(slug, isim)
        m["kategoriler"] = kategoriler
        m["alt_kategoriler"] = alt_kategoriler

        # Resim yollarını güncelle
        if lokal_mod:
            lokal_resimler = lokal_resimleri_bul(slug)
            if lokal_resimler:
                # Her dil için lokal resimleri ata
                for dil_kodu, dil_verisi in m.get("diller", {}).items():
                    dil_verisi["resimler"] = lokal_resimler

        # Sayaç
        for ak in alt_kategoriler:
            key = f"{kategoriler[0]} → {ak}"
            kategori_sayac[key] = kategori_sayac.get(key, 0) + 1

        zengin_makineler.append(m)

    # 3. Slug'a göre sırala
    zengin_makineler.sort(key=lambda m: m["slug"])

    # 4. Yedekle
    if HEDEF.exists():
        import shutil
        shutil.copy2(HEDEF, YEDEK)
        print(f"  💾 Yedeklendi → {YEDEK.name}")

    # 5. Yaz
    HEDEF.parent.mkdir(parents=True, exist_ok=True)
    with open(HEDEF, 'w', encoding='utf-8') as f:
        json.dump(zengin_makineler, f, ensure_ascii=False, indent=2)

    # 6. Rapor
    print(f"\n  ✅ {len(zengin_makineler)} makine → {HEDEF.name}")
    resim_modu = "LOKAL" if lokal_mod else "CDN"
    print(f"  🖼️  Resim modu: {resim_modu}")

    print(f"\n  📋 Kategori Dağılımı:")
    for kat, sayi in sorted(kategori_sayac.items(), key=lambda x: -x[1]):
        bar = "█" * min(sayi, 30)
        print(f"     {kat:.<35} {sayi:>3} {bar}")

    alu = sum(1 for m in zengin_makineler if "Alüminyum" in m["kategoriler"])
    pvc = sum(1 for m in zengin_makineler if "PVC" in m["kategoriler"])
    print(f"\n  📊 Alüminyum: {alu} | PVC: {pvc} | Toplam: {len(zengin_makineler)}")
    print(f"\n  💡 Sonraki adım: npx astro dev")
    print()


if __name__ == "__main__":
    main()
