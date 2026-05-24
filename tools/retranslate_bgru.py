#!/usr/bin/env python3
"""
Re-translate BG and RU descriptions for enriched Gocmaksan machines.

Reads/writes individual canonical files (src/data/machines/gocmaksan/<slug>.json).
Does NOT touch machines where EN description < 500 chars (pdf_missing stubs).
Does NOT modify tercume_merkezi.py or the aggregate gocmaksan.json.

Usage:
    py tools/retranslate_bgru.py --dry-run          # dry run, first enriched slug
    py tools/retranslate_bgru.py --slug gms-sls-12-...  --dry-run
    py tools/retranslate_bgru.py --slug gms-sls-12-...  # single machine
    py tools/retranslate_bgru.py                    # all enriched machines (~39)
    py tools/retranslate_bgru.py --lang bg          # BG only
    py tools/retranslate_bgru.py --lang ru          # RU only

Requirements:
    pip install requests
    GEMINI_API_KEY in .env at repo root (or export as env var)

Safety:
    - Backs up JSON to _backup/pre_retranslate_<timestamp>/ before writing
    - 5 sec rate limit between Gemini calls (free tier: 15 RPM)
    - Log written to _retranslate_log.json (appends each run)
    - Only touches diller.bg.description and diller.ru.description
    - All other fields (name, images, specs, technical_data) preserved
"""

import argparse
import json
import os
import shutil
import sys
import time
import urllib3
from datetime import datetime
from pathlib import Path

import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── .env loader ───────────────────────────────────────────────────────────────
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    with open(_env_path, "r", encoding="utf-8") as _f:
        for _line in _f:
            if _line.startswith("GEMINI_API_KEY="):
                os.environ["GEMINI_API_KEY"] = _line.strip().split("=", 1)[1]

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
JSON_DIR = ROOT / "src" / "data" / "machines" / "gocmaksan"
BACKUP_ROOT = ROOT / "_backup"
LOG_PATH = ROOT / "_retranslate_log.json"

RATE_LIMIT_SECS = 5
MIN_EN_CHARS = 500  # below this = stub, skip

GEMINI_URL = (
    "https://generativelanguage.googleapis.com"
    "/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
)

LANG_NAMES = {
    "bg": "Bulgarian",
    "ru": "Russian",
}

# Heading translations so Gemini renders proper headings in each language
HEADING_HINTS = {
    "bg": "## Overview -> ## Общ преглед  |  ## Key Benefits -> ## Основни предимства  |  ## Engineering Highlights -> ## Технически характеристики",
    "ru": "## Overview -> ## Обзор  |  ## Key Benefits -> ## Ключевые преимущества  |  ## Engineering Highlights -> ## Технические особенности",
}

TRANSLATION_PROMPT = """You are a professional technical translator specializing in industrial machinery.

Translate the following English machine description into {language}.

Translation rules:
- Preserve ALL Markdown formatting: ## headings, paragraph breaks, **bold**
- Translate headings into natural {language} equivalents (hints: {heading_hints})
- Keep technical terms accurate and professional
- Maintain the same structure and number of paragraphs
- Do NOT add, remove, or merge sections
- Output ONLY the translated Markdown text, starting directly with the first ## heading

English source:
{text}"""


def get_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        print(
            "ERROR: GEMINI_API_KEY not set. "
            "Add it to .env at repo root, or export as env var.",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def get_all_slugs() -> list[str]:
    return sorted(p.stem for p in JSON_DIR.glob("*.json"))


def backup_json(slug: str, timestamp: str) -> Path:
    backup_dir = BACKUP_ROOT / f"pre_retranslate_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    src = JSON_DIR / f"{slug}.json"
    dst = backup_dir / f"{slug}.json"
    shutil.copy2(src, dst)
    return dst


def load_log() -> dict:
    if LOG_PATH.exists():
        try:
            return json.loads(LOG_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"runs": []}
    return {"runs": []}


def save_log(log: dict) -> None:
    LOG_PATH.write_text(
        json.dumps(log, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def translate_text(text: str, lang: str, api_key: str) -> str:
    """Translate text to target language via Gemini REST API."""
    prompt = TRANSLATION_PROMPT.format(
        language=LANG_NAMES[lang],
        heading_hints=HEADING_HINTS[lang],
        text=text,
    )

    url = GEMINI_URL.format(key=api_key)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2},
    }

    res = requests.post(url, json=payload, timeout=60, verify=False)
    resp_json = res.json()

    if "error" in resp_json:
        raise RuntimeError(resp_json["error"]["message"])

    return resp_json["candidates"][0]["content"]["parts"][0]["text"].strip()


def process_slug(
    slug: str,
    api_key: str,
    dry_run: bool,
    timestamp: str,
    langs: list[str],
) -> dict:
    """Process one machine slug. Returns a log-ready result dict."""
    json_path = JSON_DIR / f"{slug}.json"

    if not json_path.exists():
        return {"slug": slug, "status": "json_missing"}

    data = json.loads(json_path.read_text(encoding="utf-8"))
    en_desc = (data.get("diller", {}).get("en", {}) or {}).get("description", "") or ""

    if len(en_desc) < MIN_EN_CHARS:
        return {"slug": slug, "status": "stub_skip", "en_len": len(en_desc)}

    result: dict = {
        "slug": slug,
        "status": "ok" if not dry_run else "dry_run_ok",
        "en_len": len(en_desc),
        "translations": {},
    }

    if not dry_run:
        backup_path = backup_json(slug, timestamp)
        result["backup"] = str(backup_path)

    translation_errors = []

    for idx, lang in enumerate(langs):
        try:
            translated = translate_text(en_desc, lang, api_key)
        except Exception as e:
            result["translations"][lang] = {"status": "error", "error": str(e)[:200]}
            translation_errors.append(lang)
            # still rate-limit on error to avoid hammering
            if idx < len(langs) - 1:
                time.sleep(RATE_LIMIT_SECS)
            continue

        result["translations"][lang] = {
            "status": "dry_run_ok" if dry_run else "ok",
            "len": len(translated),
            "preview": translated[:250],
        }

        if not dry_run:
            if "diller" not in data:
                data["diller"] = {}
            if lang not in data["diller"] or data["diller"][lang] is None:
                data["diller"][lang] = {}
            data["diller"][lang]["description"] = translated

        # Rate limit between langs (but skip after last)
        if idx < len(langs) - 1:
            time.sleep(RATE_LIMIT_SECS)

    if translation_errors:
        result["status"] = "partial_error" if len(translation_errors) < len(langs) else "error"

    if not dry_run and not translation_errors:
        json_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    elif not dry_run and translation_errors and len(translation_errors) < len(langs):
        # Partial success — still write what we have
        json_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Re-translate BG/RU descriptions for enriched Gocmaksan machines."
    )
    parser.add_argument(
        "--slug", default=None,
        help="Process a single machine slug (omit for all enriched machines)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Do not write JSON files; print preview in log",
    )
    parser.add_argument(
        "--lang", choices=["bg", "ru", "both"], default="both",
        help="Which language(s) to translate (default: both)",
    )
    args = parser.parse_args()

    api_key = get_api_key()
    slugs = [args.slug] if args.slug else get_all_slugs()
    langs = ["bg", "ru"] if args.lang == "both" else [args.lang]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(
        f"Mode: {'DRY RUN' if args.dry_run else 'WRITE'} | "
        f"Langs: {'+'.join(langs).upper()} | "
        f"Machines (total): {len(slugs)} | "
        f"Timestamp: {timestamp}"
    )
    if not args.dry_run and len(slugs) > 1:
        print(f"Backup dir: {BACKUP_ROOT / f'pre_retranslate_{timestamp}'}")
    print(f"Estimated time (enriched only): ~{len(slugs) * len(langs) * RATE_LIMIT_SECS // 60} min\n")

    log = load_log()
    run_entry: dict = {
        "timestamp": timestamp,
        "dry_run": args.dry_run,
        "langs": langs,
        "slugs": slugs if len(slugs) <= 5 else f"{len(slugs)} machines",
        "results": [],
    }
    counts: dict[str, int] = {}

    for i, slug in enumerate(slugs):
        print(f"[{i+1}/{len(slugs)}] {slug} ...", end=" ", flush=True)

        result = process_slug(slug, api_key, args.dry_run, timestamp, langs)
        run_entry["results"].append(result)

        status = result["status"]
        counts[status] = counts.get(status, 0) + 1

        if status in ("ok", "dry_run_ok"):
            parts = [
                f"{lang}:{tr.get('len', 0)}"
                for lang, tr in result.get("translations", {}).items()
            ]
            print(f"{status} | EN:{result['en_len']} -> {', '.join(parts)}")
        elif status == "stub_skip":
            print(f"SKIP (stub EN: {result['en_len']} chars)")
        elif status in ("partial_error", "error"):
            errs = [
                f"{lang}:{v['error'][:80]}"
                for lang, v in result.get("translations", {}).items()
                if v.get("status") == "error"
            ]
            print(f"ERROR: {' | '.join(errs)}")
        else:
            print(status)

        # Rate limit only after machines that made API calls, and not after the last
        made_calls = status in ("ok", "dry_run_ok", "partial_error", "error")
        if made_calls and i < len(slugs) - 1:
            time.sleep(RATE_LIMIT_SECS)

    # ── Summary ───────────────────────────────────────────────────────────────
    run_entry["summary"] = counts
    log["runs"].append(run_entry)
    save_log(log)

    print()
    print("=== Summary ===")
    for k, v in sorted(counts.items()):
        if v:
            print(f"  {k}: {v}")
    print(f"\nLog -> {LOG_PATH.relative_to(ROOT)}")

    if args.dry_run:
        first_ok = next(
            (r for r in run_entry["results"] if r["status"] == "dry_run_ok"), None
        )
        if first_ok:
            print(f"\n--- DRY RUN preview ({first_ok['slug']}) ---")
            for lang, tr in first_ok.get("translations", {}).items():
                print(f"\n[{lang.upper()}] {tr.get('preview', '')[:400]}")
            print("\n--- (see _retranslate_log.json for full output) ---")


if __name__ == "__main__":
    main()
