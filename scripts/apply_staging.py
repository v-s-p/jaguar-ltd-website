#!/usr/bin/env python3
"""
apply_staging.py — Phase 3: Staging'deki yeni makineleri siteye ekler.

src/data/_staging/new_machines_*.json dosyasındaki makineler için
src/data/machines/yilmaz/{slug}.json dosyaları OLUŞTURUR.
Var olan dosyalara DOKUNMAZ.
Sonra sync_machines_to_json.py çalıştırarak yilmaz.json'u rebuild eder.
Staging dosyasını arşivler.

Kullanım:
  python scripts/apply_staging.py
"""

import sys, os, json, shutil
from pathlib import Path
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")

ROOT         = Path(__file__).resolve().parent.parent
DATA_DIR     = ROOT / "src" / "data"
MACHINES_DIR = DATA_DIR / "machines" / "yilmaz"
STAGING_DIR  = DATA_DIR / "_staging"
ARCHIVE_DIR  = STAGING_DIR / "archive"


def find_latest_staging():
    files = sorted(STAGING_DIR.glob("new_machines_*.json"), reverse=True)
    return files[0] if files else None


def build_machine_skeleton(m):
    """Staging entry'den minimal makine JSON'u oluşturur."""
    slug = m["site_slug"]
    name_en = m.get("name_en") or slug_to_name(slug)
    name_bg = m.get("name_bg") or name_en
    name_ru = m.get("name_ru") or name_en
    desc_en = m.get("description_en", "")
    desc_bg = m.get("description_bg", "")
    desc_ru = m.get("description_ru", "")

    machine = {
        "slug":        slug,
        "brand":       "yilmaz",
        "categories":  m.get("categories", []),
        "subcategory": m.get("subcategory", ""),
        "diller": {
            "en": {
                "name":        name_en,
                "description": desc_en,
                "images":      [],
                "specs":       {},
            },
            "bg": {
                "name":        name_bg,
                "description": desc_bg,
                "images":      [],
                "specs":       {},
            },
            "ru": {
                "name":        name_ru,
                "description": desc_ru,
                "images":      [],
                "specs":       {},
            },
        },
    }
    if m.get("sub_subcategory"):
        machine["type"] = m["sub_subcategory"]
    return machine


def slug_to_name(slug):
    return " ".join(p.upper() for p in slug.split("-"))


def run_sync():
    """sync_machines_to_json.py mantığını inline çalıştırır."""
    import importlib.util
    sync_path = ROOT / "scripts" / "sync_machines_to_json.py"
    spec = importlib.util.spec_from_file_location("sync", sync_path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)


def main():
    staging_file = find_latest_staging()
    if not staging_file:
        print("❌ Staging dosyası bulunamadı.")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"🚀 APPLY STAGING — {staging_file.name}")
    print(f"{'='*60}\n")

    with open(staging_file, encoding="utf-8") as f:
        staging = json.load(f)

    machines = staging.get("new_machines", [])
    if not machines:
        print("✅ Uygulanacak makine yok.")
        _write_output(0, 0, [], staging_file.name)
        return

    applied  = []
    skipped  = []
    errors   = []

    for m in machines:
        slug      = m["site_slug"]
        out_file  = MACHINES_DIR / f"{slug}.json"

        if out_file.exists():
            skipped.append(slug)
            print(f"  ⏭️  {slug} — zaten var, atlandı")
            continue

        try:
            skeleton = build_machine_skeleton(m)
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(skeleton, f, ensure_ascii=False, indent=2)
            m["applied"] = True
            applied.append(slug)
            print(f"  ✅ {slug} oluşturuldu")
        except Exception as e:
            errors.append(slug)
            print(f"  ❌ {slug} — hata: {e}")

    # Staging'i güncelle
    staging["applied_at"] = datetime.now(timezone.utc).isoformat()
    with open(staging_file, "w", encoding="utf-8") as f:
        json.dump(staging, f, ensure_ascii=False, indent=2)

    if not applied:
        print("\n⚠️  Yeni dosya oluşturulmadı (hepsi atlandı veya hata).")
        _write_output(0, len(skipped), [], staging_file.name)
        return

    # yilmaz.json rebuild
    print(f"\n  🔄 yilmaz.json rebuild ediliyor...")
    run_sync()

    # Staging arşivle
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    archive_name = staging_file.stem + f"_applied_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.json"
    shutil.move(str(staging_file), str(ARCHIVE_DIR / archive_name))
    print(f"  📦 Staging arşivlendi: archive/{archive_name}")

    print(f"\n  ✅ {len(applied)} makine eklendi")
    if skipped:
        print(f"  ⏭️  {len(skipped)} atlandı (zaten var)")
    if errors:
        print(f"  ❌ {len(errors)} hata")

    _write_email_output(applied, skipped, errors, staging_file.name)


def _write_email_output(applied, skipped, errors, filename):
    repo_url = "https://github.com/v-s-p/jaguar-ltd-website"
    lines = []
    lines.append("━━━ UYGULAMA RAPORU ━━━")
    lines.append(f"Staging dosyası: {filename}")
    lines.append("")

    if applied:
        lines.append(f"✅ Siteye eklenen {len(applied)} yeni makine:")
        for s in applied:
            lines.append(f"  • {s}")
        lines.append("")
        lines.append("CMS'te görünmeleri için içeriklerini tamamlayabilirsin:")
        lines.append("  → Resim ekle")
        lines.append("  → Teknik özellikler (specs) doldur")
        lines.append("  → Açıklama kontrol et / düzenle")
        cms_url = "https://jaguar-ltd.com/admin"
        lines.append(f"  → {cms_url}")

    if skipped:
        lines.append(f"\n⏭️  {len(skipped)} makine atlandı (zaten katalogda var):")
        for s in skipped:
            lines.append(f"  • {s}")

    if errors:
        lines.append(f"\n❌ {len(errors)} makine eklenemedi:")
        for s in errors:
            lines.append(f"  • {s}")
        lines.append(f"  → Detaylar için: {repo_url}/actions")

    lines.append("")
    lines.append("──────────────────────────────")
    lines.append("Jaguar LTD — Otomatik CI/CD")

    email_body = "\n".join(lines)
    print("\n" + "="*60)
    print("📧 EMAIL GÖVDESİ:")
    print(email_body)

    gh_output = os.getenv("GITHUB_OUTPUT")
    if gh_output:
        escaped = email_body.replace("%", "%25").replace("\n", "%0A").replace("\r", "%0D")
        with open(gh_output, "a", encoding="utf-8") as f:
            f.write(f"applied={len(applied)}\n")
            f.write(f"skipped={len(skipped)}\n")
            f.write(f"errors={len(errors)}\n")
            f.write(f"email_body={escaped}\n")


def _write_output(applied, skipped, errors, filename):
    _write_email_output([], [], [], filename)


if __name__ == "__main__":
    main()
