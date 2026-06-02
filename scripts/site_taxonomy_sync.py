#!/usr/bin/env python3
"""
site_taxonomy_sync.py — Yılmaz Machine + Göçmaksan taxonomy scraper.

Manufacturer sitelerinden product taxonomy'i çeker, machines.json /
gocmaksan.json'a yazar.

Modlar:
  DRY_RUN (default) → rapor yazar, JSON'lara dokunmaz
  WRITE             → TAXONOMY_WRITE=1 env var ile aktif

Kullanım:
  python scripts/site_taxonomy_sync.py           # dry-run
  TAXONOMY_WRITE=1 python scripts/site_taxonomy_sync.py  # write mode
"""

import sys, os, json, re, time
from pathlib import Path
import requests
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

# ─── CONFIG ───────────────────────────────────────────────────────────────────
DRY_RUN = os.getenv("TAXONOMY_WRITE", "0") != "1"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}
SLEEP = 2.5  # saniye — server'ı yormayalım

DATA_DIR         = Path("src/data")
MACHINES_JSON    = DATA_DIR / "yilmaz.json"
GOCMAKSAN_JSON   = DATA_DIR / "gocmaksan.json"
OVERRIDES_JSON   = DATA_DIR / "multi_category_overrides.json"

BASE_YILMAZ = "https://www.yilmazmachine.com.tr/en/product-category"

# ─── YILMAZ TAXONOMY TREE ────────────────────────────────────────────────────
# Hardcoded from sidebar scrape (2026-05-10).
# jaguar_sub = mevcut machines.json'daki subcategory değeri ile eşleşir.
# sub_subcategories = yeni sub_subcategory field için level-3 isimler.

YILMAZ_TAXONOMY = {
    "Aluminium": {
        "url":       f"{BASE_YILMAZ}/aluminium/",
        "jaguar_cat": "Aluminium",
        "subcategories": {
            "Machining Centers": {
                "url":        f"{BASE_YILMAZ}/processing-centers/",
                "jaguar_sub": "Machining Centers",
                "sub_subcategories": {
                    "Profile Machining And Cutting Center": f"{BASE_YILMAZ}/profile-machining-and-cutting-center/",
                    "Sheet Plate Machining Center":         f"{BASE_YILMAZ}/sheet-plate-machining-center/",
                },
            },
            "Saw Cutting": {
                "url":        f"{BASE_YILMAZ}/saw-cutting-2/",
                "jaguar_sub": "Cutting",
                "sub_subcategories": {
                    "Double Head Cutting": f"{BASE_YILMAZ}/double-head-cutting/",
                    "Radial Cutting":      f"{BASE_YILMAZ}/radial-cutting-2/",
                    "Single Head Cutting": f"{BASE_YILMAZ}/single-head-cutting/",
                    "Slicing Machine":     f"{BASE_YILMAZ}/slicing-machine/",
                    "V Cutting":           f"{BASE_YILMAZ}/v-cutting/",
                    "Portable Cutting":    f"{BASE_YILMAZ}/portable-cutting/",
                },
            },
            "Milling": {
                "url":        f"{BASE_YILMAZ}/milling/",
                "jaguar_sub": "Routing & Milling",
                "sub_subcategories": {
                    "NC Router":             f"{BASE_YILMAZ}/numerical-controlled-nc-router/",
                    "Portable Copy Router":  f"{BASE_YILMAZ}/portable-copy-router-en-2/",
                    "Template Copy Router":  f"{BASE_YILMAZ}/template-copy-router/",
                },
            },
            "Corner Crimping": {
                "url":        f"{BASE_YILMAZ}/corner-crimping/",
                "jaguar_sub": "Corner Crimping",
                "sub_subcategories": {
                    "CNC Automatic Corner Crimping": f"{BASE_YILMAZ}/cnc-automatic-corner-crimping/",
                    "Hydraulic Corner Crimping":     f"{BASE_YILMAZ}/hydrolic-corner-crimping/",
                    "Pneumatic Corner Crimping":     f"{BASE_YILMAZ}/pneumatic-corner-crimping/",
                },
            },
            "End Milling": {
                "url":        f"{BASE_YILMAZ}/end-milling-2/",
                "jaguar_sub": "End Milling",
                "sub_subcategories": {
                    "Semi Automatic End Milling": f"{BASE_YILMAZ}/semi-automatic-end-milling/",
                    "Portable End Milling":       f"{BASE_YILMAZ}/portable-end-milling/",
                    "Facade Notching Saw":        f"{BASE_YILMAZ}/facade-notching-saw/",
                },
            },
            "Pressing": {
                "url":        f"{BASE_YILMAZ}/pressing/",
                "jaguar_sub": "Press",
                "sub_subcategories": {
                    "Manual Punch Press": f"{BASE_YILMAZ}/manual-punch-press/",
                },
            },
            "Transferring": {
                "url":        f"{BASE_YILMAZ}/transferring-en-2/",
                "jaguar_sub": "Handling",
                "sub_subcategories": {
                    "Trolley": f"{BASE_YILMAZ}/trolley/",
                },
            },
            "Conveying": {
                "url":        f"{BASE_YILMAZ}/conveying-en-2/",
                "jaguar_sub": "Conveyor",
                "sub_subcategories": {
                    "Conveyors": f"{BASE_YILMAZ}/conveyors/",
                },
            },
            "Swarf Extraction": {
                "url":        f"{BASE_YILMAZ}/swarf-extraction-en/",
                "jaguar_sub": "Vacuum",
                "sub_subcategories": {
                    "Vacuum Swarf Extractor": f"{BASE_YILMAZ}/vacuum-swarf-extractor-en/",
                },
            },
            "Assembling": {
                "url":        f"{BASE_YILMAZ}/assembling/",
                "jaguar_sub": "Assembly",
                "sub_subcategories": {
                    "Sash Assembly Station": f"{BASE_YILMAZ}/sash-assembly-station/",
                    "Work Bench":            f"{BASE_YILMAZ}/work-beanch/",
                },
            },
        },
    },
    "PVC": {
        "url":       f"{BASE_YILMAZ}/pvc/",
        "jaguar_cat": "PVC",
        "subcategories": {
            "Processing Center": {
                "url":        f"{BASE_YILMAZ}/processing-center/",
                "jaguar_sub": "Machining Centers",
                "sub_subcategories": {
                    "Four Head Corner Welding Cleaning Line": f"{BASE_YILMAZ}/four-head-corner-welding-cleaning-line/",
                    "Profile Cutting Machining Center":       f"{BASE_YILMAZ}/profile-cutting-machining-center/",
                },
            },
            "Cleaning": {
                "url":        f"{BASE_YILMAZ}/cleaning/",
                "jaguar_sub": "Corner Cleaning",
                "sub_subcategories": {
                    "CNC Corner Cleaning Machine":    f"{BASE_YILMAZ}/cnc-corner-cleaning-machine/",
                    "Manual Corner Cleaning Machine": f"{BASE_YILMAZ}/manual-corner-cleaning-machine/",
                    "Window Gasket Milling Machine":  f"{BASE_YILMAZ}/window-gasket-milling-machine/",
                },
            },
            "Cutting": {
                "url":        f"{BASE_YILMAZ}/cutting/",
                "jaguar_sub": "Cutting",
                "sub_subcategories": {
                    "Double Head Cutting":             f"{BASE_YILMAZ}/double-head-cutting-2/",
                    "Glazing Bead Cutting":            f"{BASE_YILMAZ}/glazing-bead-cutting/",
                    "Reinforcement Sheet Band Saw":    f"{BASE_YILMAZ}/reinforcement-sheet-band-saw/",
                    "Reinforcement Sheet Circular Saw":f"{BASE_YILMAZ}/reinforcement-sheet-circular-saw/",
                    "Single Head Cutting":             f"{BASE_YILMAZ}/single-head-cutting-2/",
                    "Portable Cutting":                f"{BASE_YILMAZ}/portable-cutting-2/",
                },
            },
            "Milling": {
                "url":        f"{BASE_YILMAZ}/milling-en-2/",
                "jaguar_sub": "Routing & Milling",
                "sub_subcategories": {
                    "Template Copy Router Machine": f"{BASE_YILMAZ}/template-copy-router-machine/",
                    "Portable Copy Router":         f"{BASE_YILMAZ}/portable-copy-router-en/",
                },
            },
            "End Milling": {
                "url":        f"{BASE_YILMAZ}/end-milling-3/",
                "jaguar_sub": "End Milling",
                "sub_subcategories": {
                    "End Milling Machine":  f"{BASE_YILMAZ}/end-milling-machine-2/",
                    "Portable End Milling": f"{BASE_YILMAZ}/portable-end-milling-en/",
                },
            },
            "Screwdriving": {
                "url":        f"{BASE_YILMAZ}/screwdriving-en/",
                "jaguar_sub": "Screwdriving",
                "sub_subcategories": {
                    "Double Head Screwdriving":    f"{BASE_YILMAZ}/double-head-reinforcement-stell-screwdriver-en/",
                    "Single Head Screwdriving":    f"{BASE_YILMAZ}/single-head-reinforcement-stell-screwdriver-en/",
                    "Mullion Connector Assembly":  f"{BASE_YILMAZ}/automatic-mullion-connector-assembly-machine/",
                },
            },
            "Welding": {
                "url":        f"{BASE_YILMAZ}/welding/",
                "jaguar_sub": "Welding",
                "sub_subcategories": {
                    "Double Corner Welding": f"{BASE_YILMAZ}/double-corner-welding/",
                    "Four Corner Welding":   f"{BASE_YILMAZ}/four-corner-welding/",
                    "Single Corner Welding": f"{BASE_YILMAZ}/single-corner-welding/",
                },
            },
            "Transferring": {
                "url":        f"{BASE_YILMAZ}/transferring-en-3/",
                "jaguar_sub": "Handling",
                "sub_subcategories": {
                    "Trolley": f"{BASE_YILMAZ}/trolley-en/",
                },
            },
            "Swarf Extraction": {
                "url":        f"{BASE_YILMAZ}/swarf-extraction-en-2/",
                "jaguar_sub": "Vacuum",
                "sub_subcategories": {
                    "Vacuum Swarf Extractor": f"{BASE_YILMAZ}/vacuum-swarf-extractor-en-2/",
                },
            },
            "Conveying": {
                "url":        f"{BASE_YILMAZ}/conveying-en/",
                "jaguar_sub": "Conveyor",
                "sub_subcategories": {
                    "Conveyors": f"{BASE_YILMAZ}/conveyors-en/",
                },
            },
            "Assembling": {
                "url":        f"{BASE_YILMAZ}/assembling-en/",
                "jaguar_sub": "Assembly",
                "sub_subcategories": {
                    "Sash Assembly Station": f"{BASE_YILMAZ}/sash-assembly-station-en/",
                    "Work Bench":            f"{BASE_YILMAZ}/work-beanches/",
                },
            },
        },
    },
}

GOCMAKSAN_CATEGORIES = [
    ("Bending Machines",   "bukme-makinalari"),
    ("Portable Bending",   "portatif-bukme-makinalari"),
    ("Stirrup Bending",    "etriye-bukme-makinalari"),
    ("Spiral Bending",     "spiral-bukme-makinalari"),
    ("Dowel Bar Bending",  "filiz-demir-bukme-makinalari"),
    ("Cutting Machines",   "kesme-makinalari"),
    ("Portable Cutting",   "portatif-kesme-makinalari"),
    ("Combined Machines",  "insaat-demiri-kesme-ve-bukme-kombine-makinalari"),
    ("Light Construction", "hafif-insaat-makinalari"),
    ("Steel Factory",      "demir-tesisi-cozumleri"),
    ("Hand Tools",         "insaatci-el-aletleri"),
]

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def model_key(slug: str) -> str:
    """İlk 3 slug parçası → model kodu (örn: 'aim-7420')."""
    return "-".join(slug.split("-")[:3]).lower()


def fetch_html(url: str) -> BeautifulSoup | None:
    """URL'den HTML al, BeautifulSoup döndür. Hata varsa None."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        if resp.status_code == 200:
            return BeautifulSoup(resp.text, "lxml")
        print(f"  ⚠️  HTTP {resp.status_code}: {url}")
        return None
    except Exception as e:
        print(f"  ❌ Fetch error ({url}): {e}")
        return None


def extract_yilmaz_slugs(soup: BeautifulSoup) -> set[str]:
    """Yılmaz category page'inden product slug'larını çıkar."""
    slugs = set()
    pattern = re.compile(r"/en/products/([^/?#]+)/?$")
    for a in soup.find_all("a", href=pattern):
        m = pattern.search(a["href"])
        if m:
            slugs.add(m.group(1))
    return slugs


def scrape_yilmaz_category(url: str) -> set[str]:
    """Pagination dahil tüm ürün slug'larını toplar."""
    all_slugs: set[str] = set()
    page = 1
    while True:
        page_url = url if page == 1 else f"{url}page/{page}/"
        soup = fetch_html(page_url)
        if soup is None:
            break
        found = extract_yilmaz_slugs(soup)
        if not found:
            break
        prev = len(all_slugs)
        all_slugs |= found
        if len(all_slugs) == prev:   # yeni ürün gelmedi → son sayfa
            break
        page += 1
        time.sleep(SLEEP)
    return all_slugs


def extract_gocmaksan_slugs(soup: BeautifulSoup, cat_slug: str) -> set[str]:
    """Göçmaksan category page'inden ürün slug'larını çıkar."""
    slugs = set()
    pattern = re.compile(rf"/eng/{re.escape(cat_slug)}/([^/?#]+)")
    for a in soup.find_all("a", href=pattern):
        m = pattern.search(a["href"])
        if m:
            prod_slug = m.group(1)
            if prod_slug and not prod_slug.startswith("#"):
                slugs.add(prod_slug)
    return slugs


def load_overrides() -> dict:
    if OVERRIDES_JSON.exists():
        with open(OVERRIDES_JSON, encoding="utf-8") as f:
            return json.load(f)
    return {}


# ─── YILMAZ SCRAPER ───────────────────────────────────────────────────────────

def fetch_yilmaz() -> dict:
    """
    Returns:
      {
        site_slug: {
          "categories":        set[str],   # "Aluminium", "PVC"
          "subcategory":       str | None, # Jaguar-normalized level-2
          "sub_subcategory":   str | None, # level-3 display name
          "yilmaz_sub":        str | None, # raw Yılmaz level-2 name
        }
      }
    """
    print("\n🌍 Yılmaz Machine taxonomy scraping başlıyor...")
    taxonomy: dict = {}

    total_requests = 0

    for l1_name, l1_data in YILMAZ_TAXONOMY.items():
        jaguar_cat = l1_data["jaguar_cat"]
        print(f"\n  📂 Level 1: {l1_name}")

        for l2_name, l2_data in l1_data["subcategories"].items():
            jaguar_sub  = l2_data["jaguar_sub"]

            # Level 3 önce — daha spesifik
            for l3_name, l3_url in l2_data["sub_subcategories"].items():
                print(f"    🔍 L3: {l3_name}")
                slugs = scrape_yilmaz_category(l3_url)
                total_requests += 1
                time.sleep(SLEEP)
                for slug in slugs:
                    if slug not in taxonomy:
                        taxonomy[slug] = {
                            "categories":      set(),
                            "subcategory":     None,
                            "sub_subcategory": None,
                            "yilmaz_sub":      None,
                        }
                    taxonomy[slug]["categories"].add(jaguar_cat)
                    # Sub-sub sadece ilk atamada (en spesifik kazanır)
                    if taxonomy[slug]["sub_subcategory"] is None:
                        taxonomy[slug]["sub_subcategory"] = l3_name
                        taxonomy[slug]["subcategory"]     = jaguar_sub
                        taxonomy[slug]["yilmaz_sub"]      = l2_name

            # Level 2 — subcategory backup (L3'te yakalanmayan makineler için)
            print(f"    🔍 L2: {l2_name}")
            slugs_l2 = scrape_yilmaz_category(l2_data["url"])
            total_requests += 1
            time.sleep(SLEEP)
            for slug in slugs_l2:
                if slug not in taxonomy:
                    taxonomy[slug] = {
                        "categories":      set(),
                        "subcategory":     None,
                        "sub_subcategory": None,
                        "yilmaz_sub":      None,
                    }
                taxonomy[slug]["categories"].add(jaguar_cat)
                if taxonomy[slug]["subcategory"] is None:
                    taxonomy[slug]["subcategory"] = jaguar_sub
                    taxonomy[slug]["yilmaz_sub"]  = l2_name

    print(f"\n  ✅ Yılmaz scrape tamamlandı — {len(taxonomy)} unique ürün, {total_requests} istek")
    return taxonomy


# ─── GOCMAKSAN SCRAPER ────────────────────────────────────────────────────────

def fetch_gocmaksan() -> dict:
    """
    Returns:
      {
        full_site_slug: {"categories": set[str]}
      }
    """
    print("\n🌍 Göçmaksan taxonomy scraping başlıyor...")
    taxonomy: dict = {}

    for cat_name, cat_slug in GOCMAKSAN_CATEGORIES:
        url = f"https://www.gocmaksan.com/eng/{cat_slug}"
        print(f"  🔍 {cat_name}")
        soup = fetch_html(url)
        if soup is None:
            time.sleep(SLEEP)
            continue
        slugs = extract_gocmaksan_slugs(soup, cat_slug)
        for slug in slugs:
            taxonomy.setdefault(slug, {"categories": set()})
            taxonomy[slug]["categories"].add(cat_name)
        time.sleep(SLEEP)

    print(f"  ✅ Göçmaksan scrape tamamlandı — {len(taxonomy)} unique ürün")
    return taxonomy


# ─── JSON MERGE ───────────────────────────────────────────────────────────────

def match_jaguar(jaguar_slug: str, site_taxonomy: dict) -> dict | None:
    """Jaguar slug'ı için site taxonomy entry'si bul (direct veya model-key)."""
    if jaguar_slug in site_taxonomy:
        return site_taxonomy[jaguar_slug]
    key = model_key(jaguar_slug)
    for site_slug, data in site_taxonomy.items():
        if model_key(site_slug) == key:
            return data
    return None


def merge_yilmaz(machines: list, site_tax: dict, overrides: dict) -> dict:
    changes = {
        "added_multi_cat":   [],   # slug: eski→yeni
        "added_sub_sub":     [],
        "updated_subcategory": [],
        "no_match":          [],
        "overridden":        [],
    }

    for m in machines:
        slug = m["slug"]

        if slug in overrides:
            # Apply domain-knowledge categories (overrides scrape result)
            old_cats = set(m.get("categories") or [])
            override_cats = sorted(overrides[slug])
            if set(override_cats) != old_cats:
                changes["added_multi_cat"].append({
                    "slug": slug,
                    "old": sorted(old_cats),
                    "new": override_cats,
                })
                m["categories"] = override_cats
            changes["overridden"].append(slug)
            continue

        tax = match_jaguar(slug, site_tax)
        if tax is None:
            changes["no_match"].append(slug)
            continue

        # categories — union, sıralı
        old_cats = set(m.get("categories") or [])
        new_cats = tax["categories"]
        merged_cats = sorted(old_cats | new_cats)
        if set(merged_cats) != old_cats:
            changes["added_multi_cat"].append({
                "slug": slug,
                "old": sorted(old_cats),
                "new": merged_cats,
            })
            m["categories"] = merged_cats

        # subcategory
        if tax.get("subcategory") and not m.get("subcategory"):
            changes["updated_subcategory"].append(slug)
            m["subcategory"] = tax["subcategory"]

        # sub_subcategory (yeni field)
        if tax.get("sub_subcategory") and not m.get("sub_subcategory"):
            changes["added_sub_sub"].append({
                "slug": slug,
                "val": tax["sub_subcategory"],
            })
            m["sub_subcategory"] = tax["sub_subcategory"]

    return changes


def merge_gocmaksan(machines: list, site_tax: dict, overrides: dict) -> dict:
    changes = {
        "multi_cat_found": [],
        "category_updated": [],
        "no_match": [],
    }

    for m in machines:
        slug = m["slug"]
        if slug in overrides:
            continue

        # Göçmaksan'da Jaguar slug'ları tam eşleşmez — model key ile ara
        tax = match_jaguar(slug, site_tax)
        if tax is None:
            changes["no_match"].append(slug)
            continue

        cats = tax["categories"]
        if len(cats) > 1:
            changes["multi_cat_found"].append({"slug": slug, "cats": sorted(cats)})

        # Mevcut category field'ı güncelle (Göçmaksan için `category` string)
        primary_cat = sorted(cats)[0] if cats else None
        if primary_cat and m.get("category") != primary_cat and len(cats) == 1:
            changes["category_updated"].append({
                "slug": slug,
                "old": m.get("category"),
                "new": primary_cat,
            })
            m["category"] = primary_cat

    return changes


# ─── REPORT ───────────────────────────────────────────────────────────────────

def print_yilmaz_report(site_tax: dict, jaguar_machines: list, changes: dict):
    print("\n" + "="*60)
    print("📊 YILMAZ SCRAPE RAPORU")
    print("="*60)

    # Toplam
    alu_slugs = {s for s, d in site_tax.items() if "Aluminium" in d["categories"]}
    pvc_slugs = {s for s, d in site_tax.items() if "PVC" in d["categories"]}
    multi     = alu_slugs & pvc_slugs
    print(f"  Aluminium listesi:  {len(alu_slugs)} ürün")
    print(f"  PVC listesi:        {len(pvc_slugs)} ürün")
    print(f"  Toplam unique:      {len(site_tax)} ürün")
    print(f"  Multi-cat (iki listede de): {len(multi)} ürün")
    if multi:
        for s in sorted(multi)[:8]:
            print(f"    → {s}")
        if len(multi) > 8:
            print(f"    ... ve {len(multi)-8} tane daha")

    # AIM 7420 / AIM 4420 özel check
    print()
    for check_slug in ["aim-7420", "aim-4420"]:
        tax = match_jaguar(check_slug, site_tax)
        if tax:
            print(f"  🔎 {check_slug}: cats={sorted(tax['categories'])}  sub={tax.get('subcategory')}  sub_sub={tax.get('sub_subcategory')}")
        else:
            print(f"  🔎 {check_slug}: site'de bulunamadı")

    # Taxonomy örneği — 3 makine
    print("\n  Örnek taxonomy (3 makine):")
    count = 0
    for slug, d in site_tax.items():
        if d.get("sub_subcategory"):
            print(f"    {slug}")
            print(f"      cats={sorted(d['categories'])}  sub={d['subcategory']}  sub_sub={d['sub_subcategory']}")
            count += 1
            if count >= 3:
                break

    # Slug match raporu
    jaguar_slugs = {m["slug"] for m in jaguar_machines}
    matched   = sum(1 for s in jaguar_slugs if match_jaguar(s, site_tax))
    unmatched = [s for s in jaguar_slugs if not match_jaguar(s, site_tax)]
    print(f"\n  Jaguar ↔ Site match: {matched}/{len(jaguar_slugs)}")
    if unmatched:
        print(f"  Eşleşmeyen ({len(unmatched)}):")
        for s in unmatched[:10]:
            print(f"    - {s}")

    # Change summary
    print(f"\n  Multi-cat eklenen:     {len(changes['added_multi_cat'])}")
    print(f"  sub_subcategory eklenen: {len(changes['added_sub_sub'])}")
    print(f"  subcategory güncellenen: {len(changes['updated_subcategory'])}")
    print(f"  Override korunan:      {len(changes['overridden'])}")
    print(f"  No match:              {len(changes['no_match'])}")

    if changes["added_multi_cat"]:
        print("\n  Multi-cat değişiklikleri (ilk 5):")
        for c in changes["added_multi_cat"][:5]:
            print(f"    {c['slug']}: {c['old']} → {c['new']}")

    if changes["added_sub_sub"]:
        print("\n  sub_subcategory örnekleri (ilk 5):")
        for c in changes["added_sub_sub"][:5]:
            print(f"    {c['slug']}: {c['val']}")

    mode = "DRY-RUN (dosyalara yazılmadı)" if DRY_RUN else "WRITE MODE — yilmaz.json güncellendi"
    print(f"\n  Mod: {mode}")


def print_gocmaksan_report(site_tax: dict, jaguar_machines: list, changes: dict):
    print("\n" + "="*60)
    print("📊 GOCMAKSAN SCRAPE RAPORU")
    print("="*60)
    print(f"  Site'de unique ürün: {len(site_tax)}")
    print(f"  Multi-cat tespit:    {len(changes['multi_cat_found'])}")
    if changes["multi_cat_found"]:
        for c in changes["multi_cat_found"]:
            print(f"    → {c['slug']}: {c['cats']}")

    jaguar_slugs = {m["slug"] for m in jaguar_machines}
    matched   = sum(1 for s in jaguar_slugs if match_jaguar(s, site_tax))
    unmatched = [s for s in jaguar_slugs if not match_jaguar(s, site_tax)]
    print(f"  Jaguar ↔ Site match: {matched}/{len(jaguar_slugs)}")
    if unmatched:
        print(f"  Eşleşmeyen ({len(unmatched)}):")
        for s in unmatched[:10]:
            print(f"    - {s}")

    mode = "DRY-RUN" if DRY_RUN else "WRITE MODE — gocmaksan.json güncellendi"
    print(f"  Mod: {mode}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*60}")
    print(f"🔧 JAGUAR TAXONOMY SYNC")
    print(f"   Mod: {'DRY-RUN (dosyalara dokunmaz)' if DRY_RUN else 'WRITE MODE'}")
    print(f"{'='*60}")

    overrides = load_overrides()
    if overrides:
        print(f"  📋 Override dosyası yüklendi: {len(overrides)} makine korunuyor")

    # ── Yılmaz ──────────────────────────────────────────────────────────────
    yilmaz_tax = fetch_yilmaz()

    with open(MACHINES_JSON, encoding="utf-8") as f:
        machines = json.load(f)

    # Deep copy for dry-run (mock mutations)
    import copy
    machines_work = copy.deepcopy(machines)

    yilmaz_changes = merge_yilmaz(machines_work, yilmaz_tax, overrides)
    print_yilmaz_report(yilmaz_tax, machines, yilmaz_changes)

    print("\n" + "─"*60)
    print("⏸️  DUR #1 — Yılmaz raporu yukarıda. Göçmaksan'a devam etmek için")
    print("   ENTER'a bas (ya da Ctrl+C ile çık)...")
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        pass

    # ── Göçmaksan ───────────────────────────────────────────────────────────
    gocmaksan_tax = fetch_gocmaksan()

    with open(GOCMAKSAN_JSON, encoding="utf-8") as f:
        gocmaksan = json.load(f)

    gocmaksan_work = copy.deepcopy(gocmaksan)
    gocmaksan_changes = merge_gocmaksan(gocmaksan_work, gocmaksan_tax, overrides)
    print_gocmaksan_report(gocmaksan_tax, gocmaksan, gocmaksan_changes)

    print("\n" + "─"*60)
    print("⏸️  DUR #2 — Göçmaksan raporu yukarıda. JSON merge dry-run için")
    print("   ENTER'a bas (ya da Ctrl+C ile çık)...")
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        pass

    # ── DRY-RUN merge özeti ─────────────────────────────────────────────────
    print("\n" + "="*60)
    print("📋 DUR #3 — JSON MERGE DRY-RUN ÖZETİ")
    print("="*60)
    print(f"  yilmaz.json değişecekler:")
    print(f"    Multi-cat ekleme:         {len(yilmaz_changes['added_multi_cat'])} makine")
    print(f"    sub_subcategory ekleme:   {len(yilmaz_changes['added_sub_sub'])} makine")
    print(f"    subcategory güncelleme:   {len(yilmaz_changes['updated_subcategory'])} makine")

    total_y = (len(yilmaz_changes['added_multi_cat']) +
               len(yilmaz_changes['added_sub_sub']) +
               len(yilmaz_changes['updated_subcategory']))
    print(f"    TOPLAM etkilenen kayıt:   {total_y}")

    # Diff örnekleri
    print("\n  Diff örnekleri (yilmaz.json):")
    shown = 0
    for m_new, m_old in zip(machines_work, machines):
        if m_new != m_old and shown < 5:
            slug = m_new["slug"]
            print(f"    [{slug}]")
            for key in ("categories", "subcategory", "sub_subcategory"):
                v_old = m_old.get(key)
                v_new = m_new.get(key)
                if v_old != v_new:
                    print(f"      {key}: {v_old!r} → {v_new!r}")
            shown += 1

    if DRY_RUN:
        print(f"\n  ⚠️  DRY-RUN — hiçbir dosyaya yazılmadı.")
        print(f"  Yazmak için: TAXONOMY_WRITE=1 python scripts/site_taxonomy_sync.py")
    else:
        # WRITE
        with open(MACHINES_JSON, "w", encoding="utf-8") as f:
            json.dump(machines_work, f, ensure_ascii=False, indent=2)
        with open(GOCMAKSAN_JSON, "w", encoding="utf-8") as f:
            json.dump(gocmaksan_work, f, ensure_ascii=False, indent=2)
        print(f"\n  ✅ yilmaz.json ve gocmaksan.json güncellendi!")

    print("\n🎉 Taxonomy sync tamamlandı.")


if __name__ == "__main__":
    main()
