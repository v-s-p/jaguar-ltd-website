#!/usr/bin/env python3
"""
tools/fill_missing_yilmaz_ru_specs.py
======================================
Fill missing diller.ru.specs for Yilmaz machines by translating
diller.en.specs items (EN -> RU) via Gemini.

Only processes machines where diller.ru.specs is absent but diller.en.specs exists.
Idempotent: skips if diller.ru.specs already populated.

Usage:
    py tools/fill_missing_yilmaz_ru_specs.py                # dry-run all missing
    py tools/fill_missing_yilmaz_ru_specs.py --apply        # write + sync
    py tools/fill_missing_yilmaz_ru_specs.py --single aim-3410
    py tools/fill_missing_yilmaz_ru_specs.py --single aim-3410 --apply
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import io
import datetime
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# UTF-8 stdout for Cyrillic on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)

REPO_ROOT   = Path(__file__).resolve().parent.parent
YILMAZ_DIR  = REPO_ROOT / "src" / "data" / "machines" / "yilmaz"
SYNC_SCRIPT = REPO_ROOT / "scripts" / "sync_machines_to_json.py"

MODEL_NAME      = "gemini-2.5-flash"
GEMINI_URL      = (
    "https://generativelanguage.googleapis.com"
    f"/v1beta/models/{MODEL_NAME}:generateContent?key={{key}}"
)
RATE_LIMIT_SECS = 3

# Model codes that must stay Latin (never Cyrillicised in spec items)
_UPPER_CYR_RE = re.compile(r"\b[А-ЯЁ]{2,}\b")

# ---------------------------------------------------------------------------
# .env loader
# ---------------------------------------------------------------------------
_env_path = REPO_ROOT / ".env"
if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        if _line.startswith("GEMINI_API_KEY="):
            os.environ.setdefault("GEMINI_API_KEY", _line.split("=", 1)[1].strip())


def load_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        print("ERROR: GEMINI_API_KEY not found in .env or environment.", file=sys.stderr)
        sys.exit(1)
    return key


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------
PROMPT_TEMPLATE = """\
You are a professional technical translator (English -> Russian) specializing in
CNC machinery and manufacturing equipment.

Translate the following machine spec items from English to Russian.

RULES:
1. Model codes and product numbers MUST stay in Latin script — NEVER transliterate:
   VCE 3500, AIM 3410, CAMQUIX, HSK F63, USB, CNC, PLC, CAD, CAM, ISO
   CORRECT: "Вакуумный экстрактор VCE 3500"
   WRONG:   "Вакуумный экстрактор ВЦЕ 3500"

2. Dimensions and measurements stay as-is (e.g. Ø5, 180 mm, 4-axis).

3. Use professional Russian technical language — sentence case.

4. Preserve the meaning precisely — do NOT simplify or expand.

5. Output ONLY a JSON object with the same spec key names and translated item arrays.
   No markdown fences, no commentary.

INPUT (JSON):
{input_json}

Expected output format:
{{
  "standard_accessories": ["...", "..."],
  "optional_accessories": ["...", "..."],
  "general_features":     ["...", "..."]
}}

Output only the JSON object.
"""


# ---------------------------------------------------------------------------
# Gemini call
# ---------------------------------------------------------------------------

def call_gemini(specs_en: dict, api_key: str) -> dict:
    """Send all spec groups in one call; return translated dict."""
    input_json = json.dumps(specs_en, ensure_ascii=False, indent=2)
    prompt = PROMPT_TEMPLATE.format(input_json=input_json)

    url = GEMINI_URL.format(key=api_key)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "response_mime_type": "application/json",
        },
    }

    resp = requests.post(url, json=payload, timeout=120, verify=False)
    body = resp.json()

    if "error" in body:
        raise RuntimeError(f"Gemini API error: {body['error'].get('message', body['error'])}")
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")

    raw_text = body["candidates"][0]["content"]["parts"][0]["text"].strip()

    # Strip markdown fences if present
    if raw_text.startswith("```"):
        lines = raw_text.splitlines()
        raw_text = "\n".join(l for l in lines if not l.startswith("```")).strip()

    return json.loads(raw_text)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_translated(en_specs: dict, ru_specs: dict) -> list[str]:
    """Return list of warning strings (empty = all OK)."""
    warnings = []

    for key in en_specs:
        if key not in ru_specs:
            warnings.append(f"Missing key '{key}' in translation output")
            continue
        en_items = en_specs[key]
        ru_items = ru_specs[key]
        if len(ru_items) != len(en_items):
            warnings.append(
                f"Key '{key}': EN has {len(en_items)} items, RU has {len(ru_items)}"
            )
        # Check for Cyrillic model codes (heuristic)
        for item in ru_items:
            m = _UPPER_CYR_RE.search(item[:20])
            if m:
                warnings.append(
                    f"Key '{key}': possible Cyrillic model code '{m.group()}' in: {item[:60]!r}"
                )
                break

    # Check for unexpected extra keys
    for key in ru_specs:
        if key not in en_specs:
            warnings.append(f"Unexpected extra key '{key}' in translation output")

    return warnings


# ---------------------------------------------------------------------------
# Collect target machines
# ---------------------------------------------------------------------------

def collect_targets(single: str | None) -> list[Path]:
    all_files = sorted(f for f in YILMAZ_DIR.glob("*.json")
                       if not f.stem.startswith("_") and ".bak" not in f.name)

    targets = []
    for path in all_files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        en_specs = (data.get("diller") or {}).get("en", {}).get("specs")
        ru_specs = (data.get("diller") or {}).get("ru", {}).get("specs")

        # Skip: no EN specs to translate from
        if not en_specs or not isinstance(en_specs, dict):
            continue
        # Skip: RU specs already exist (idempotent)
        if ru_specs and isinstance(ru_specs, dict) and ru_specs:
            continue

        targets.append(path)

    if single:
        fragment = single.lower()
        matched = [p for p in targets if fragment in p.stem.lower()]
        if not matched:
            print(f"[!] No target found matching '{single}' (already has RU specs or no EN specs?)")
            sys.exit(1)
        return matched

    return targets


# ---------------------------------------------------------------------------
# Apply: inject RU specs into machine data
# ---------------------------------------------------------------------------

def inject_ru_specs(data: dict, ru_specs: dict) -> dict:
    """Write ru_specs into diller.ru.specs; all other fields preserved."""
    new_data = dict(data)
    diller = dict(data.get("diller") or {})
    ru_lang = dict(diller.get("ru") or {})
    ru_lang["specs"] = ru_specs
    diller["ru"] = ru_lang
    new_data["diller"] = diller
    return new_data


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Fill missing Yilmaz RU specs via Gemini EN->RU")
    parser.add_argument("--apply", action="store_true", help="Write translations to disk + sync")
    parser.add_argument("--single", metavar="SLUG", help="Process only matching slug(s)")
    args = parser.parse_args()

    dry_run = not args.apply
    mode = "DRY-RUN" if dry_run else "APPLY"
    print(f"=== fill_missing_yilmaz_ru_specs.py [{mode}] ===\n")

    targets = collect_targets(args.single)
    print(f"Target machines (missing RU specs): {len(targets)}\n")

    if not targets:
        print("[OK] Nothing to do — all machines already have RU specs or no EN specs.")
        return

    api_key = load_api_key()

    results = []

    for path in targets:
        data = json.loads(path.read_text(encoding="utf-8"))
        slug = data.get("slug", path.stem)
        en_specs: dict = data["diller"]["en"]["specs"]

        print(f"[*] {slug}")
        print(f"    EN keys: {list(en_specs.keys())}")
        print(f"    EN item counts: { {k: len(v) for k, v in en_specs.items()} }")

        try:
            t0 = time.time()
            ru_specs = call_gemini(en_specs, api_key)
            elapsed = time.time() - t0
        except Exception as e:
            print(f"    ERROR: {e}", file=sys.stderr)
            results.append({"slug": slug, "status": "error", "error": str(e), "path": path, "data": data, "ru_specs": None})
            time.sleep(RATE_LIMIT_SECS)
            continue

        warnings = validate_translated(en_specs, ru_specs)

        # Print side-by-side diff
        print(f"    Translation complete ({elapsed:.1f}s):")
        for key in en_specs:
            ru_items = ru_specs.get(key, [])
            en_items = en_specs[key]
            print(f"    [{key}] ({len(en_items)} items)")
            for i, en_item in enumerate(en_items):
                ru_item = ru_items[i] if i < len(ru_items) else "(MISSING)"
                print(f"      EN: {en_item[:80]}")
                print(f"      RU: {ru_item[:80]}")

        if warnings:
            print(f"    WARNINGS ({len(warnings)}):")
            for w in warnings:
                print(f"      [!] {w}")
        else:
            print(f"    Validation: OK")

        results.append({
            "slug": slug, "status": "ready", "path": path,
            "data": data, "ru_specs": ru_specs, "warnings": warnings
        })

        time.sleep(RATE_LIMIT_SECS)

    # Summary before writing
    ready = [r for r in results if r["status"] == "ready"]
    errors = [r for r in results if r["status"] == "error"]
    total_warnings = sum(len(r.get("warnings", [])) for r in ready)

    print(f"\n{'='*60}")
    print(f"Ready: {len(ready)} | Errors: {len(errors)} | Warnings: {total_warnings}")

    if dry_run:
        print("\n[DRY-RUN] No files written. Pass --apply to write.")
        return

    if not ready:
        print("[OK] Nothing to write.")
        return

    # Backup
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = YILMAZ_DIR / f"_pre_ru_specs_backup_{ts}"
    backup_dir.mkdir(exist_ok=True)
    for r in ready:
        shutil.copy2(r["path"], backup_dir / r["path"].name)
    print(f"[OK] Backup: {backup_dir}")

    # Write
    for r in ready:
        new_data = inject_ru_specs(r["data"], r["ru_specs"])
        r["path"].write_text(
            json.dumps(new_data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8"
        )
        print(f"[OK] Written: {r['slug']}")

    # Sync
    if SYNC_SCRIPT.exists():
        print("\n[*] Running sync_machines_to_json.py ...")
        result = subprocess.run(
            [sys.executable, str(SYNC_SCRIPT)],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        if result.returncode == 0:
            print("[OK] Sync complete.")
        else:
            print(f"[!] Sync error:\n{result.stderr[:500]}")
    else:
        print(f"[!] Sync script not found at {SYNC_SCRIPT}")


if __name__ == "__main__":
    main()
