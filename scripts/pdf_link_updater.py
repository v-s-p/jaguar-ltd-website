# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
PDF catalog link updater - gocmaksan + yilmaz JSON
Usage: python pdf_link_updater.py [--write]
Without --write: report-only mode
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GOCMAKSAN_JSON = ROOT / "src" / "data" / "gocmaksan.json"
YILMAZ_JSON = ROOT / "src" / "data" / "yilmaz.json"
GOCMAKSAN_PDF_DIR = ROOT / "public" / "catalogs" / "gocmaksan"

WRITE_MODE = "--write" in sys.argv

# ── helpers ──────────────────────────────────────────────────────────────────

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ saved {path.name}")

def gocmaksan_pdfs():
    """Returns dict: stem → filename  e.g. 'gms-b-36-...' → 'gms-b-36-....pdf'"""
    return {p.stem: p.name for p in GOCMAKSAN_PDF_DIR.glob("*.pdf")}

def find_pdf_for_slug(slug, pdf_map):
    """
    1. Exact match: slug == stem
    2. Prefix match: stem.startswith(slug)  (handles -sy0wu suffix etc.)
    Returns filename or None.
    """
    if slug in pdf_map:
        return pdf_map[slug]
    for stem, fname in pdf_map.items():
        if stem.startswith(slug):
            return fname
    return None

# ── İş 1: Gocmaksan ─────────────────────────────────────────────────────────

print("\n====================================")
print("IS 1 - GOCMAKSAN PDF LINKLERI")
print("====================================")

goc_data = load_json(GOCMAKSAN_JSON)
pdf_map = gocmaksan_pdfs()

print(f"PDF dosyaları: {len(pdf_map)}")
print(f"Makine sayısı: {len(goc_data)}\n")

matched = []
unmatched = []
already_had = []

for machine in goc_data:
    slug = machine["slug"]
    existing = machine.get("diller", {}).get("en", {}).get("pdf_catalog", None)
    pdf_fname = find_pdf_for_slug(slug, pdf_map)

    if pdf_fname:
        new_val = f"/catalogs/gocmaksan/{pdf_fname}"
        if existing == new_val:
            already_had.append(slug)
        else:
            matched.append((slug, existing, new_val))
        # update
        if WRITE_MODE:
            machine.setdefault("diller", {}).setdefault("en", {})["pdf_catalog"] = new_val
    else:
        unmatched.append((slug, existing))

print(f"MATCHED   : {len(matched) + len(already_had)}")
print(f"  - zaten doğru: {len(already_had)}")
print(f"  - güncellenecek: {len(matched)}")
print(f"UNMATCHED : {len(unmatched)}\n")

if matched:
    print("Güncellenecek makineler:")
    for slug, old, new in matched:
        print(f"  {slug}")
        print(f"    eski: {old!r}")
        print(f"    yeni: {new!r}")

if unmatched:
    print("\nPDF bulunamayan makineler:")
    for slug, existing in unmatched:
        print(f"  {slug}  (mevcut: {existing!r})")

if WRITE_MODE:
    save_json(GOCMAKSAN_JSON, goc_data)
    print(f"\n✅ Gocmaksan JSON güncellendi: {len(matched)} makine değişti")
else:
    print("\n[RAPOR MODU — yazmak için --write ekle]")

# ── İş 2: Yilmaz ─────────────────────────────────────────────────────────────

print("\n====================================")
print("IS 2 - YILMAZ PDF LINKLERI")
print("====================================")

yil_data = load_json(YILMAZ_JSON)
print(f"Makine sayısı: {len(yil_data)}\n")

PVC_PATH = "/catalogs/yilmaz/PVC-KATALOG.pdf"
ALU_PATH = "/catalogs/yilmaz/ALUMINIUM-KATALOG.pdf"

pvc_count = 0
alu_count = 0
empty_count = 0
update_count = 0

for machine in yil_data:
    cats = machine.get("categories", [])
    if not isinstance(cats, list):
        cats = [cats] if cats else []

    # determine catalog
    if "PVC" in cats and "Aluminium" in cats:
        # use first
        new_val = PVC_PATH if cats[0] == "PVC" else ALU_PATH
    elif "PVC" in cats:
        new_val = PVC_PATH
        pvc_count += 1
    elif "Aluminium" in cats:
        new_val = ALU_PATH
        alu_count += 1
    else:
        new_val = ""
        empty_count += 1

    existing = machine.get("diller", {}).get("en", {}).get("pdf_catalog", None)
    if new_val and existing != new_val:
        update_count += 1

    if WRITE_MODE and new_val:
        machine.setdefault("diller", {}).setdefault("en", {})["pdf_catalog"] = new_val

print(f"PVC makineler    : {pvc_count}")
print(f"Aluminium makineler: {alu_count}")
print(f"Kategori yok     : {empty_count}")
print(f"Güncellenecek    : {update_count}")

if WRITE_MODE:
    save_json(YILMAZ_JSON, yil_data)
    print(f"\n✅ Yilmaz JSON güncellendi: {update_count} makine değişti")
else:
    print("\n[RAPOR MODU — yazmak için --write ekle]")

print("\nBitti.")
