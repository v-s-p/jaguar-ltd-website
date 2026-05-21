#!/usr/bin/env python3
"""
Enrich gocmaksan machine descriptions from PDF catalogs using Gemini.

Usage:
    py tools/enrich_gocmaksan_descriptions.py --slug gms-sls-12-... --dry-run
    py tools/enrich_gocmaksan_descriptions.py --slug gms-sls-12-...
    py tools/enrich_gocmaksan_descriptions.py                           # mass run 47 machines

Requirements:
    pip install google-genai python-dotenv
    Add GEMINI_API_KEY=your_key to .env at repo root (or export as env var)

Safety:
    - Backs up JSON to _backup/pre_enrichment_gocmaksan_<timestamp>/ before writing
    - 5 sec rate limit between Gemini calls (free tier: 15 RPM)
    - Log written to _enrichment_log.json (appends each run)
    - Only touches diller.en.description — all other fields preserved
"""

import argparse
import json
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# ── Resolve project root (two levels up from tools/) ─────────────────────────
ROOT = Path(__file__).resolve().parent.parent
JSON_DIR = ROOT / "src" / "data" / "machines" / "gocmaksan"
PDF_DIR = ROOT / "public" / "catalogs" / "gocmaksan"
BACKUP_ROOT = ROOT / "_backup"
LOG_PATH = ROOT / "_enrichment_log.json"

RATE_LIMIT_SECS = 5          # free tier: 15 RPM ≈ 4 sec; 5 is safe
MODEL = "gemini-2.0-flash"

# ── Gemini prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a technical copywriter reading a PDF product catalog for an industrial machine.

Your task: extract and write ONLY narrative/prose that describes:
- What the machine does and its core purpose
- Which industries or professionals use it
- Key operational benefits and advantages
- Typical applications or workflows it enables
- Notable engineering or design highlights (if described in prose, not as a spec)

FORMAT:
- Markdown with ## section headings (e.g. ## Overview, ## Applications, ## Key Benefits)
- 2 to 5 focused paragraphs total
- English only, professional tone
- Do NOT use bullet lists — write full sentences and paragraphs

STRICTLY SKIP — do not mention, list, or reference:
- Technical specification tables (dimensions, weight, voltage, RPM, Hz, kW, mm, bar, etc.)
- Supplied equipment / accessories lists
- Page headers, page footers, company addresses, phone numbers
- Model reference numbers, HS codes, part numbers
- Image captions or photo descriptions
- Price information

If the PDF has no narrative prose at all (specs-only document), write 2–3 original paragraphs
describing the machine's evident purpose and user benefit based on context — without
inventing or repeating any specific numeric values.

Begin your response directly with the first ## heading. No preamble."""


def get_client():
    """Initialize Gemini client from env variable."""
    try:
        from google import genai
    except ImportError:
        print("ERROR: google-genai not installed. Run: pip install google-genai", file=sys.stderr)
        sys.exit(1)

    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        print("ERROR: GEMINI_API_KEY not set. Add it to .env at repo root, or export as env var.", file=sys.stderr)
        sys.exit(1)

    return genai.Client(api_key=key)


def get_all_slugs() -> list[str]:
    return sorted(p.stem for p in JSON_DIR.glob("*.json"))


def backup_json(slug: str, timestamp: str) -> Path:
    backup_dir = BACKUP_ROOT / f"pre_enrichment_gocmaksan_{timestamp}"
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
        encoding="utf-8"
    )


def call_gemini(client, pdf_path: Path, slug: str) -> str:
    """Upload PDF to Gemini Files API and extract prose description."""
    from google.genai import types

    # Upload PDF
    with open(pdf_path, "rb") as f:
        uploaded = client.files.upload(
            file=f,
            config=types.UploadFileConfig(
                mime_type="application/pdf",
                display_name=slug,
            ),
        )

    # Wait until file is ACTIVE (usually instant, but be safe)
    for _ in range(15):
        info = client.files.get(name=uploaded.name)
        state = getattr(info.state, "name", str(info.state))
        if state == "ACTIVE":
            break
        time.sleep(2)
    else:
        raise RuntimeError(f"File {uploaded.name} never became ACTIVE (state={state})")

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[
                types.Part.from_uri(
                    file_uri=uploaded.uri,
                    mime_type="application/pdf",
                ),
                SYSTEM_PROMPT,
            ],
        )
        return response.text.strip()
    finally:
        # Clean up uploaded file to avoid quota accumulation
        try:
            client.files.delete(name=uploaded.name)
        except Exception:
            pass


def process_slug(slug: str, client, dry_run: bool, timestamp: str) -> dict:
    """Process one machine slug. Returns a log-ready result dict."""
    json_path = JSON_DIR / f"{slug}.json"
    pdf_path = PDF_DIR / f"{slug}.pdf"

    if not json_path.exists():
        return {"slug": slug, "status": "json_missing"}

    if not pdf_path.exists():
        return {
            "slug": slug,
            "status": "pdf_missing",
            "old_length": len(
                json.loads(json_path.read_text(encoding="utf-8"))
                .get("diller", {}).get("en", {}).get("description", "")
            ),
        }

    data = json.loads(json_path.read_text(encoding="utf-8"))
    old_desc = data.get("diller", {}).get("en", {}).get("description", "")

    try:
        new_desc = call_gemini(client, pdf_path, slug)
    except Exception as e:
        return {
            "slug": slug,
            "status": "gemini_error",
            "error": str(e),
            "old_length": len(old_desc),
        }

    result = {
        "slug": slug,
        "status": "dry_run_ok" if dry_run else "ok",
        "old_length": len(old_desc),
        "new_length": len(new_desc),
        "preview": new_desc[:300],
    }

    if dry_run:
        result["full_output"] = new_desc
    else:
        # Backup first, then write
        backup_path = backup_json(slug, timestamp)
        result["backup"] = str(backup_path)

        # Replace only the description field
        if "diller" not in data:
            data["diller"] = {}
        if "en" not in data["diller"]:
            data["diller"]["en"] = {}
        data["diller"]["en"]["description"] = new_desc

        json_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Enrich gocmaksan descriptions from PDF catalogs via Gemini."
    )
    parser.add_argument(
        "--slug", default=None,
        help="Process a single machine slug (omit for all 47 machines)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Do not write JSON files; include full Gemini output in log",
    )
    args = parser.parse_args()

    client = get_client()

    slugs = [args.slug] if args.slug else get_all_slugs()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"Mode: {'DRY RUN' if args.dry_run else 'WRITE'} | "
          f"Machines: {len(slugs)} | Timestamp: {timestamp}")
    if not args.dry_run and len(slugs) > 1:
        backup_dir = BACKUP_ROOT / f"pre_enrichment_gocmaksan_{timestamp}"
        print(f"Backup dir: {backup_dir}")
    print()

    log = load_log()
    run_entry: dict = {
        "timestamp": timestamp,
        "dry_run": args.dry_run,
        "slugs": slugs if len(slugs) <= 5 else f"{len(slugs)} machines",
        "results": [],
    }

    counts: dict[str, int] = {}

    api_calls = 0  # track actual API calls for rate limiting

    for i, slug in enumerate(slugs):
        print(f"[{i + 1}/{len(slugs)}] {slug} ...", end=" ", flush=True)

        result = process_slug(slug, client, args.dry_run, timestamp)
        run_entry["results"].append(result)

        status = result["status"]
        counts[status] = counts.get(status, 0) + 1

        # Human-readable line
        if status in ("ok", "dry_run_ok"):
            print(f"{status} | {result['old_length']} → {result['new_length']} chars")
        elif status == "pdf_missing":
            print(f"SKIP (no PDF)")
        elif status == "gemini_error":
            print(f"ERROR: {result.get('error', '?')}")
        else:
            print(status)

        # Rate limit: only between actual Gemini calls
        needs_api = status in ("ok", "dry_run_ok")
        if needs_api:
            api_calls += 1
        if needs_api and i < len(slugs) - 1:
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
    print(f"\nLog written to: {LOG_PATH.relative_to(ROOT)}")

    if args.dry_run and run_entry["results"]:
        first_ok = next(
            (r for r in run_entry["results"] if r["status"] == "dry_run_ok"), None
        )
        if first_ok:
            print(f"\n--- DRY RUN full_output preview ({first_ok['slug']}) ---")
            print(first_ok.get("full_output", "")[:800])
            print("--- (see _enrichment_log.json for complete output) ---")


if __name__ == "__main__":
    main()
