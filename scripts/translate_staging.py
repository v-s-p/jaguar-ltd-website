#!/usr/bin/env python3
"""
translate_staging.py — Phase 2: Staging JSON'daki yeni makineleri çevirir.

src/data/_staging/new_machines_*.json içindeki makineler için
Gemini API ile BG ve RU çevirisi yapar.
Sadece staging dosyasını günceller — siteye YAZMAZ.

Kullanım:
  GEMINI_API_KEY=xxx python scripts/translate_staging.py
"""

import sys, os, json, time
from pathlib import Path
from datetime import datetime, timezone

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding="utf-8")

ROOT        = Path(__file__).resolve().parent.parent
STAGING_DIR = ROOT / "src" / "data" / "_staging"

API_KEY = os.environ.get("GEMINI_API_KEY")


def gemini_translate(name_en, desc_en, target_lang):
    """Gemini ile teknik çeviri. (name, description) tuple döndürür."""
    lang_map = {"bg": "Bulgarian", "ru": "Russian"}
    lang = lang_map.get(target_lang, target_lang)
    prompt = f"""Sen endüstriyel alüminyum/PVC pencere makineleri konusunda uzman bir çevirmensin.
Aşağıdaki makine adını ve açıklamasını {lang} diline teknik terimleri koruyarak çevir.
Model kodlarını (büyük harfli kısayollar) ASLA çevirme.
Yanıtı sadece şu formatta ver:
ISIM: <çevrilmiş isim>
ACIKLAMA: <çevrilmiş açıklama>

Makine adı: {name_en}
Açıklama: {desc_en or ''}"""

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        resp = requests.post(
            url, params={"key": API_KEY}, json=payload,
            timeout=30, verify=False
        )
        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        lines = [l for l in text.strip().split("\n") if l.strip()]
        name_t = lines[0].replace("ISIM:", "").strip() if lines else ""
        desc_t = lines[1].replace("ACIKLAMA:", "").strip() if len(lines) > 1 else ""
        return name_t, desc_t
    except Exception as e:
        print(f"    ❌ API hatası ({target_lang}): {e}")
        return None, None


def find_latest_staging():
    files = sorted(STAGING_DIR.glob("new_machines_*.json"), reverse=True)
    return files[0] if files else None


def main():
    if not API_KEY:
        print("❌ GEMINI_API_KEY eksik.")
        sys.exit(1)

    staging_file = find_latest_staging()
    if not staging_file:
        print("❌ Staging dosyası bulunamadı. Önce scrape_discovery.py çalıştır.")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"🌐 TRANSLATE STAGING — {staging_file.name}")
    print(f"{'='*60}\n")

    with open(staging_file, encoding="utf-8") as f:
        staging = json.load(f)

    machines = staging.get("new_machines", [])
    if not machines:
        print("✅ Çevrilecek makine yok (new_machines boş).")
        _write_output(0, 0, staging_file.name)
        return

    todo = [m for m in machines if not m.get("translated")]
    print(f"  Toplam: {len(machines)} makine, çevrilecek: {len(todo)}\n")

    success = 0
    failed  = 0

    for m in todo:
        slug    = m["site_slug"]
        name_en = m.get("name_en") or _name_from_slug(slug)
        desc_en = m.get("description_en", "")

        print(f"  🔄 {slug}")
        for lang in ("bg", "ru"):
            name_key = f"name_{lang}"
            desc_key = f"description_{lang}"
            if m.get(name_key):
                print(f"       {lang}: zaten var, atlanıyor")
                continue
            name_t, desc_t = gemini_translate(name_en, desc_en, lang)
            time.sleep(3)
            if name_t:
                m[name_key] = name_t
                m[desc_key] = desc_t
                print(f"       {lang}: ✅ {name_t[:50]}")
            else:
                print(f"       {lang}: ❌ başarısız")
                failed += 1

        if m.get("name_bg") and m.get("name_ru"):
            m["translated"] = True
            success += 1

    staging["translated_at"] = datetime.now(timezone.utc).isoformat()

    with open(staging_file, "w", encoding="utf-8") as f:
        json.dump(staging, f, ensure_ascii=False, indent=2)

    print(f"\n  ✅ {success} makine çevrildi, {failed} başarısız")
    print(f"  📄 Güncellendi: {staging_file}")

    _write_email_output(success, failed, machines, staging_file.name)


def _name_from_slug(slug):
    parts = slug.split("-")
    # Model kodu: büyük harfli parçaları bul (örn: ACK, 420, S)
    return " ".join(p.upper() for p in parts)


def _write_email_output(success, failed, machines, filename):
    repo_url = "https://github.com/v-s-p/jaguar-ltd-website"
    lines = []
    lines.append("━━━ ÇEVİRİ RAPORU ━━━")
    lines.append(f"Staging dosyası: {filename}")
    lines.append(f"Başarılı: {success} makine")
    if failed:
        lines.append(f"Başarısız: {failed} makine")
    lines.append("")

    translated = [m for m in machines if m.get("translated")]
    if translated:
        lines.append("Çevrilen makineler:")
        for m in translated:
            lines.append(f"  • {m['site_slug']}")
            if m.get("name_bg"):
                lines.append(f"    BG: {m['name_bg']}")
            if m.get("name_ru"):
                lines.append(f"    RU: {m['name_ru']}")

    lines.append("")
    lines.append("━━━ SONRAKI ADIM ━━━")
    lines.append("")
    lines.append("Staging JSON'u inceledikten sonra siteye eklemek için:")
    lines.append(f"  → {repo_url}/actions/workflows/apply-staging.yml")
    lines.append("  → 'Run workflow' butonuna bas")
    lines.append("  → Sadece YENİ makineler eklenir, mevcutlara DOKUNULMAZ")
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
            f.write(f"success={success}\n")
            f.write(f"failed={failed}\n")
            f.write(f"email_body={escaped}\n")


def _write_output(success, failed, filename):
    gh_output = os.getenv("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as f:
            f.write(f"success={success}\nfailed={failed}\n")


if __name__ == "__main__":
    main()
