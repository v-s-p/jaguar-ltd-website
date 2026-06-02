#!/usr/bin/env python3
"""
scrape_discovery.py — Phase 1: Yeni makine keşfi (siteye yazmaz).

YILMAZ sitesini scrape eder, mevcut katalogla karşılaştırır.
Sadece YENİ makineleri src/data/_staging/new_machines_YYYY-MM.json'a yazar.
Mevcut makinelerdeki farkları rapor olarak üretir (uygulama YOK).

Kullanım:
  python scripts/scrape_discovery.py

Çıktılar:
  src/data/_staging/new_machines_YYYY-MM.json
  stdout'a email gövdesi (GITHUB_OUTPUT'a da yazar)
"""

import sys, os, json, re, time
from pathlib import Path
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

# ─── CONFIG ───────────────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}
SLEEP = 2.5

ROOT          = Path(__file__).resolve().parent.parent
DATA_DIR      = ROOT / "src" / "data"
MACHINES_DIR  = DATA_DIR / "machines" / "yilmaz"
STAGING_DIR   = DATA_DIR / "_staging"
STAGING_DIR.mkdir(parents=True, exist_ok=True)

BASE_YILMAZ = "https://www.yilmazmachine.com.tr/en/product-category"

# ─── YILMAZ TAXONOMY TREE (kaynak: site_taxonomy_sync.py) ────────────────────
YILMAZ_TAXONOMY = {
    "Aluminium": {
        "jaguar_cat": "Aluminium",
        "subcategories": {
            "Machining Centers": {
                "url": f"{BASE_YILMAZ}/processing-centers/",
                "jaguar_sub": "Processing Centers",
                "sub_subcategories": {
                    "Profile Machining And Cutting Center": f"{BASE_YILMAZ}/profile-machining-and-cutting-center/",
                    "Sheet Plate Machining Center":         f"{BASE_YILMAZ}/sheet-plate-machining-center/",
                },
            },
            "Saw Cutting": {
                "url": f"{BASE_YILMAZ}/saw-cutting-2/",
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
                "url": f"{BASE_YILMAZ}/milling/",
                "jaguar_sub": "Milling",
                "sub_subcategories": {
                    "NC Router":            f"{BASE_YILMAZ}/numerical-controlled-nc-router/",
                    "Portable Copy Router": f"{BASE_YILMAZ}/portable-copy-router-en-2/",
                    "Template Copy Router": f"{BASE_YILMAZ}/template-copy-router/",
                },
            },
            "Corner Crimping": {
                "url": f"{BASE_YILMAZ}/corner-crimping/",
                "jaguar_sub": "Corner Crimping",
                "sub_subcategories": {
                    "CNC Automatic Corner Crimping": f"{BASE_YILMAZ}/cnc-automatic-corner-crimping/",
                    "Hydraulic Corner Crimping":     f"{BASE_YILMAZ}/hydrolic-corner-crimping/",
                    "Pneumatic Corner Crimping":     f"{BASE_YILMAZ}/pneumatic-corner-crimping/",
                },
            },
            "End Milling": {
                "url": f"{BASE_YILMAZ}/end-milling-2/",
                "jaguar_sub": "End Milling",
                "sub_subcategories": {
                    "Semi Automatic End Milling": f"{BASE_YILMAZ}/semi-automatic-end-milling/",
                    "Portable End Milling":       f"{BASE_YILMAZ}/portable-end-milling/",
                    "Facade Notching Saw":        f"{BASE_YILMAZ}/facade-notching-saw/",
                },
            },
            "Pressing": {
                "url": f"{BASE_YILMAZ}/pressing/",
                "jaguar_sub": "Pressing",
                "sub_subcategories": {
                    "Manual Punch Press": f"{BASE_YILMAZ}/manual-punch-press/",
                },
            },
            "Transferring": {
                "url": f"{BASE_YILMAZ}/transferring-en-2/",
                "jaguar_sub": "Transferring",
                "sub_subcategories": {
                    "Trolley": f"{BASE_YILMAZ}/trolley/",
                },
            },
            "Conveying": {
                "url": f"{BASE_YILMAZ}/conveying-en-2/",
                "jaguar_sub": "Conveying",
                "sub_subcategories": {
                    "Conveyors": f"{BASE_YILMAZ}/conveyors/",
                },
            },
            "Swarf Extraction": {
                "url": f"{BASE_YILMAZ}/swarf-extraction-en/",
                "jaguar_sub": "Swarf Extraction",
                "sub_subcategories": {
                    "Vacuum Swarf Extractor": f"{BASE_YILMAZ}/vacuum-swarf-extractor-en/",
                },
            },
            "Assembling": {
                "url": f"{BASE_YILMAZ}/assembling/",
                "jaguar_sub": "Assembling",
                "sub_subcategories": {
                    "Sash Assembly Station": f"{BASE_YILMAZ}/sash-assembly-station/",
                    "Work Bench":            f"{BASE_YILMAZ}/work-beanch/",
                },
            },
        },
    },
    "PVC": {
        "jaguar_cat": "PVC",
        "subcategories": {
            "Processing Center": {
                "url": f"{BASE_YILMAZ}/processing-center/",
                "jaguar_sub": "Processing Centers",
                "sub_subcategories": {
                    "Four Head Corner Welding Cleaning Line": f"{BASE_YILMAZ}/four-head-corner-welding-cleaning-line/",
                    "Profile Cutting Machining Center":       f"{BASE_YILMAZ}/profile-cutting-machining-center/",
                },
            },
            "Cleaning": {
                "url": f"{BASE_YILMAZ}/cleaning/",
                "jaguar_sub": "Cleaning",
                "sub_subcategories": {
                    "CNC Corner Cleaning Machine":    f"{BASE_YILMAZ}/cnc-corner-cleaning-machine/",
                    "Manual Corner Cleaning Machine": f"{BASE_YILMAZ}/manual-corner-cleaning-machine/",
                    "Window Gasket Milling Machine":  f"{BASE_YILMAZ}/window-gasket-milling-machine/",
                },
            },
            "Cutting": {
                "url": f"{BASE_YILMAZ}/cutting/",
                "jaguar_sub": "Cutting",
                "sub_subcategories": {
                    "Double Head Cutting":              f"{BASE_YILMAZ}/double-head-cutting-2/",
                    "Glazing Bead Cutting":             f"{BASE_YILMAZ}/glazing-bead-cutting/",
                    "Reinforcement Sheet Band Saw":     f"{BASE_YILMAZ}/reinforcement-sheet-band-saw/",
                    "Reinforcement Sheet Circular Saw": f"{BASE_YILMAZ}/reinforcement-sheet-circular-saw/",
                    "Single Head Cutting":              f"{BASE_YILMAZ}/single-head-cutting-2/",
                    "Portable Cutting":                 f"{BASE_YILMAZ}/portable-cutting-2/",
                },
            },
            "Milling": {
                "url": f"{BASE_YILMAZ}/milling-en-2/",
                "jaguar_sub": "Milling",
                "sub_subcategories": {
                    "Template Copy Router Machine": f"{BASE_YILMAZ}/template-copy-router-machine/",
                    "Portable Copy Router":         f"{BASE_YILMAZ}/portable-copy-router-en/",
                },
            },
            "End Milling": {
                "url": f"{BASE_YILMAZ}/end-milling-3/",
                "jaguar_sub": "End Milling",
                "sub_subcategories": {
                    "End Milling Machine":  f"{BASE_YILMAZ}/end-milling-machine-2/",
                    "Portable End Milling": f"{BASE_YILMAZ}/portable-end-milling-en/",
                },
            },
            "Screwdriving": {
                "url": f"{BASE_YILMAZ}/screwdriving-en/",
                "jaguar_sub": "Screwdriving",
                "sub_subcategories": {
                    "Double Head Screwdriving":   f"{BASE_YILMAZ}/double-head-reinforcement-stell-screwdriver-en/",
                    "Single Head Screwdriving":   f"{BASE_YILMAZ}/single-head-reinforcement-stell-screwdriver-en/",
                    "Mullion Connector Assembly": f"{BASE_YILMAZ}/automatic-mullion-connector-assembly-machine/",
                },
            },
            "Welding": {
                "url": f"{BASE_YILMAZ}/welding/",
                "jaguar_sub": "Welding",
                "sub_subcategories": {
                    "Double Corner Welding": f"{BASE_YILMAZ}/double-corner-welding/",
                    "Four Corner Welding":   f"{BASE_YILMAZ}/four-corner-welding/",
                    "Single Corner Welding": f"{BASE_YILMAZ}/single-corner-welding/",
                },
            },
            "Transferring": {
                "url": f"{BASE_YILMAZ}/transferring-en-3/",
                "jaguar_sub": "Transferring",
                "sub_subcategories": {
                    "Trolley": f"{BASE_YILMAZ}/trolley-en/",
                },
            },
            "Swarf Extraction": {
                "url": f"{BASE_YILMAZ}/swarf-extraction-en-2/",
                "jaguar_sub": "Swarf Extraction",
                "sub_subcategories": {
                    "Vacuum Swarf Extractor": f"{BASE_YILMAZ}/vacuum-swarf-extractor-en-2/",
                },
            },
            "Conveying": {
                "url": f"{BASE_YILMAZ}/conveying-en/",
                "jaguar_sub": "Conveyor",
                "sub_subcategories": {
                    "Conveyors": f"{BASE_YILMAZ}/conveyors-en/",
                },
            },
            "Assembling": {
                "url": f"{BASE_YILMAZ}/assembling-en/",
                "jaguar_sub": "Assembling",
                "sub_subcategories": {
                    "Sash Assembly Station": f"{BASE_YILMAZ}/sash-assembly-station-en/",
                    "Work Bench":            f"{BASE_YILMAZ}/work-beanches/",
                },
            },
        },
    },
}

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def fetch_html(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        if resp.status_code == 200:
            return BeautifulSoup(resp.text, "lxml")
        print(f"  ⚠️  HTTP {resp.status_code}: {url}")
        return None
    except Exception as e:
        print(f"  ❌ Fetch error ({url}): {e}")
        return None


def scrape_category_slugs(url):
    all_slugs = set()
    pattern = re.compile(r"/en/products/([^/?#]+)/?$")
    page = 1
    while True:
        page_url = url if page == 1 else f"{url}page/{page}/"
        soup = fetch_html(page_url)
        if soup is None:
            break
        found = set()
        for a in soup.find_all("a", href=pattern):
            m = pattern.search(a["href"])
            if m:
                found.add(m.group(1))
        if not found:
            break
        prev = len(all_slugs)
        all_slugs |= found
        if len(all_slugs) == prev:
            break
        page += 1
        time.sleep(SLEEP)
    return all_slugs


def slug_to_name(slug):
    """ACK-420-S → ACK 420 S"""
    return " ".join(p.upper() for p in slug.split("-"))


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    now = datetime.now(timezone.utc)
    month_key = now.strftime("%Y-%m")
    scraped_at = now.isoformat()

    print(f"\n{'='*60}")
    print(f"🔍 JAGUAR — YILMAZ Discovery Scrape ({month_key})")
    print(f"{'='*60}\n")

    # ── Mevcut katalog slugları ──────────────────────────────────────────────
    existing_slugs = {f.stem for f in MACHINES_DIR.glob("*.json")}
    print(f"  Mevcut katalog: {len(existing_slugs)} makine\n")

    # ── YILMAZ sitesini scrape et ────────────────────────────────────────────
    site_taxonomy = {}  # slug → {categories, subcategory, sub_subcategory}

    for l1_name, l1_data in YILMAZ_TAXONOMY.items():
        jaguar_cat = l1_data["jaguar_cat"]
        print(f"  📂 {l1_name}")
        for l2_name, l2_data in l1_data["subcategories"].items():
            jaguar_sub = l2_data["jaguar_sub"]
            # L3 önce
            for l3_name, l3_url in l2_data["sub_subcategories"].items():
                slugs = scrape_category_slugs(l3_url)
                time.sleep(SLEEP)
                for s in slugs:
                    site_taxonomy.setdefault(s, {"categories": set(), "subcategory": None, "sub_subcategory": None})
                    site_taxonomy[s]["categories"].add(jaguar_cat)
                    if site_taxonomy[s]["subcategory"] is None:
                        site_taxonomy[s]["subcategory"]     = jaguar_sub
                        site_taxonomy[s]["sub_subcategory"] = l3_name
            # L2 backup
            slugs_l2 = scrape_category_slugs(l2_data["url"])
            time.sleep(SLEEP)
            for s in slugs_l2:
                site_taxonomy.setdefault(s, {"categories": set(), "subcategory": None, "sub_subcategory": None})
                site_taxonomy[s]["categories"].add(jaguar_cat)
                if site_taxonomy[s]["subcategory"] is None:
                    site_taxonomy[s]["subcategory"] = jaguar_sub

    print(f"\n  ✅ Scrape tamamlandı — {len(site_taxonomy)} unique ürün")

    # ── Yeni makine tespiti ──────────────────────────────────────────────────
    # site'de var ama katalogda yok
    new_site_slugs = [s for s in site_taxonomy if s not in existing_slugs]

    # model key ile tekrar kontrol (slug formatı farklı olabilir)
    def model_key(slug):
        return "-".join(slug.split("-")[:3]).lower()

    existing_model_keys = {model_key(s) for s in existing_slugs}
    truly_new = [s for s in new_site_slugs if model_key(s) not in existing_model_keys]

    # ── Taxonomy farkı (mevcut makineler) ────────────────────────────────────
    taxonomy_diffs = []
    for existing_file in MACHINES_DIR.glob("*.json"):
        with open(existing_file, encoding="utf-8") as f:
            machine = json.load(f)
        slug = machine.get("slug", existing_file.stem)
        # site'de eşleşen entry bul
        site_entry = site_taxonomy.get(slug) or next(
            (v for k, v in site_taxonomy.items() if model_key(k) == model_key(slug)), None
        )
        if not site_entry:
            continue
        cur_cats = set(machine.get("categories") or [])
        site_cats = site_entry["categories"]
        if site_cats - cur_cats:
            taxonomy_diffs.append({
                "slug": slug,
                "field": "categories",
                "current": sorted(cur_cats),
                "site_value": sorted(cur_cats | site_cats),
                "note": f"Site'de ek kategori: {sorted(site_cats - cur_cats)}"
            })

    # ── Staging JSON yaz ─────────────────────────────────────────────────────
    new_machines_list = []
    for s in sorted(truly_new):
        tax = site_taxonomy[s]
        new_machines_list.append({
            "site_slug":       s,
            "categories":      sorted(tax["categories"]),
            "subcategory":     tax.get("subcategory"),
            "sub_subcategory": tax.get("sub_subcategory"),
            "name_en":         None,
            "description_en":  None,
            "name_bg":         None,
            "description_bg":  None,
            "name_ru":         None,
            "description_ru":  None,
            "translated":      False,
            "applied":         False,
        })

    staging = {
        "scraped_at":      scraped_at,
        "brand":           "yilmaz",
        "new_machines":    new_machines_list,
        "taxonomy_diffs":  taxonomy_diffs,
        "summary": {
            "existing_count": len(existing_slugs),
            "site_count":     len(site_taxonomy),
            "new_count":      len(truly_new),
            "diff_count":     len(taxonomy_diffs),
        },
    }

    staging_file = STAGING_DIR / f"new_machines_{month_key}.json"
    with open(staging_file, "w", encoding="utf-8") as f:
        json.dump(staging, f, ensure_ascii=False, indent=2)

    print(f"\n  📄 Staging: {staging_file}")
    print(f"  Yeni makine: {len(truly_new)}")
    print(f"  Taxonomy farkı: {len(taxonomy_diffs)}")

    # ── GitHub Actions output ─────────────────────────────────────────────────
    gh_output = os.getenv("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as f:
            f.write(f"new_count={len(truly_new)}\n")
            f.write(f"diff_count={len(taxonomy_diffs)}\n")
            f.write(f"staging_file={staging_file.name}\n")
            f.write(f"month_key={month_key}\n")

    # ── Email gövdesi oluştur ─────────────────────────────────────────────────
    repo_url = "https://github.com/v-s-p/jaguar-ltd-website"
    lines = []
    lines.append("━━━ YILMAZ SCRAPE RAPORU ━━━")
    lines.append(f"Tarih: {now.strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"Mevcut katalog: {len(existing_slugs)} makine")
    lines.append(f"Site'de bulunan: {len(site_taxonomy)} ürün")
    lines.append("")

    if truly_new:
        lines.append(f"📦 YENİ MAKİNELER ({len(truly_new)} adet):")
        for m in new_machines_list:
            cats = ", ".join(m["categories"])
            sub  = m.get("subcategory") or "?"
            lines.append(f"  • {m['site_slug']}  ({cats} › {sub})")
    else:
        lines.append("✅ YENİ MAKİNE YOK — Katalog güncel.")

    lines.append("")

    if taxonomy_diffs:
        lines.append(f"⚠️  MEVCUT MAKİNELERDE FARK ({len(taxonomy_diffs)} adet) — otomatik uygulanmaz:")
        for d in taxonomy_diffs[:10]:
            lines.append(f"  • {d['slug']}: {d['note']}")
        if len(taxonomy_diffs) > 10:
            lines.append(f"  ... ve {len(taxonomy_diffs) - 10} tane daha (staging JSON'da tam liste)")
        lines.append("  → Değişiklik istersen CMS üzerinden manuel güncelle.")
    else:
        lines.append("✅ MEVCUT MAKİNELERDE FARK YOK.")

    lines.append("")
    lines.append("━━━ SONRAKI ADIMLAR ━━━")
    lines.append("")

    if truly_new:
        lines.append("Bu email bilgilendirme amaçlıdır. Siteye ETKİSİ YOKTUR.")
        lines.append("")
        lines.append("ADIM 1 — BG/RU Çeviri (isteğe bağlı):")
        lines.append(f"  → {repo_url}/actions/workflows/translate-staging.yml")
        lines.append("  → Sağ üstte yeşil 'Run workflow' butonuna tıkla")
        lines.append("  → Açılan kutuda tekrar 'Run workflow' bas")
        lines.append("  → Tamamlandığında email alacaksın")
        lines.append("")
        lines.append("ADIM 2 — Yeni Makineleri Siteye Ekle:")
        lines.append(f"  → {repo_url}/actions/workflows/apply-staging.yml")
        lines.append("  → Aynı şekilde 'Run workflow' ile tetikle")
        lines.append("  → Sadece YENİ makineler eklenir, mevcutlara DOKUNULMAZ")
        lines.append("")
        lines.append("NOT: Her iki adımı da atlayabilirsin, hiçbir şey değişmez.")
    else:
        lines.append("Yapılacak bir şey yok. Bir sonraki aylık scrape'i bekle.")

    lines.append("")
    lines.append("──────────────────────────────")
    lines.append("Jaguar LTD — Otomatik CI/CD")
    lines.append(f"{repo_url}/actions")

    email_body = "\n".join(lines)
    print("\n" + "="*60)
    print("📧 EMAIL GÖVDESİ:")
    print("="*60)
    print(email_body)

    if gh_output:
        # Multiline output için GitHub Actions encoding
        email_body_escaped = email_body.replace("%", "%25").replace("\n", "%0A").replace("\r", "%0D")
        with open(gh_output, "a", encoding="utf-8") as f:
            f.write(f"email_body={email_body_escaped}\n")

    return len(truly_new)


if __name__ == "__main__":
    count = main()
    sys.exit(0)
