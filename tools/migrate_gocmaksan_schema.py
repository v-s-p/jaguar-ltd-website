#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Göçmaksan şema migrasyonu: 47 makineyi Yılmaz baseline şemasına hizalar.

Dönüşümler:
  1. subcategory   : array KALIR (log'a yazılır, dokunulmaz)
  2. specs         : top-level -> diller.en.specs  (key rename dahil)
  3. TECHNICAL DATA: specs içinden -> diller.en.technical_data  (ayrı field)
  4. FEATURED FEATURES -> GENERAL FEATURES (rename, içerik aynı)
  5. CAPACITIES / CAPACITY / SUPPLIED EQUIPMENT: ayrı blok olarak diller.en.specs'e taşınır, merge YOK
  6. pdf_catalog   : top-level çift varsa sil; sadece diller.en'de kalsın
  7. type          : eksikse "machine" ekle
  8. related_products: kaldır
  9. Empty cleanup : boş string/list/dict key'leri kaldır

Usage:
    py tools/migrate_gocmaksan_schema.py                          # dry-run tümü
    py tools/migrate_gocmaksan_schema.py --single sls-12          # dry-run tek
    py tools/migrate_gocmaksan_schema.py --apply                  # yaz
    py tools/migrate_gocmaksan_schema.py --apply --single sls-12  # tek yaz (test)
    py tools/migrate_gocmaksan_schema.py --report-out _audit/MIGRATION_DRYRUN_REPORT.md

Güvenlik:
    - --apply çalıştırılmadan önce otomatik yedek alır:
      src/data/machines/gocmaksan/_pre_migration_backup_<timestamp>/
    - Idempotent: ikinci çalışmada değişiklik yok (zaten migrate edilmiş kontrol)
    - name, description, images, pdf_catalog içerikleri asla değiştirilmez
"""

import argparse
import copy
import difflib
import io
import json
import os
import shutil
import sys as _sys

# Force UTF-8 stdout so BG/RU content doesn't crash on Windows terminals
if hasattr(_sys.stdout, "buffer"):
    _sys.stdout = io.TextIOWrapper(
        _sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True
    )
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT    = Path(__file__).parent.parent
MACHINES_DIR = REPO_ROOT / "src" / "data" / "machines" / "gocmaksan"
AGGREGATE    = REPO_ROOT / "src" / "data" / "gocmaksan.json"
SYNC_SCRIPT  = REPO_ROOT / "tools" / "sync_machines_to_json.py"

# Anomaly accumulator (populated during migration, printed in dry-run report)
_anomalies: list[dict] = []


# ---------------------------------------------------------------------------
# Core migration logic
# ---------------------------------------------------------------------------

def migrate_machine(data: dict) -> tuple[dict, list[str]]:
    """
    Apply all migrations to a single machine dict.
    Returns (migrated_dict, log_lines).
    Idempotent: already-migrated fields are detected and skipped.
    """
    m    = copy.deepcopy(data)
    slug = m.get("slug", "?")
    log  = []

    # ── 1. subcategory: report only, DO NOT MODIFY ─────────────────────────
    sc = m.get("subcategory")
    if isinstance(sc, list):
        log.append(f"subcategory: array {sc} — kept as-is")
    elif isinstance(sc, str):
        log.append(f"subcategory: string '{sc}' — kept as-is")
    else:
        log.append("subcategory: absent — skip")

    # ── 2-5. specs migration ───────────────────────────────────────────────
    top_specs = m.pop("specs", None)

    if top_specs is None:
        # Already migrated or was never present
        if m.get("diller", {}).get("en", {}).get("specs"):
            log.append("specs: already in diller.en.specs — skip")
        else:
            log.append("specs: not present — skip")
    else:
        specs_work = dict(top_specs)  # shallow copy for mutation

        # ── 3. TECHNICAL DATA -> diller.en.technical_data ──────────────────
        td = specs_work.pop("TECHNICAL DATA", None)
        if isinstance(td, dict):
            if td:  # non-empty dict -> move to diller.en.technical_data
                m.setdefault("diller", {}).setdefault("en", {})["technical_data"] = td
                log.append(f"TECHNICAL DATA -> diller.en.technical_data ({len(td)} keys)")
            else:   # empty dict {} -> discard, empty cleanup will not emit it
                log.append("TECHNICAL DATA: empty dict — discarded (not written)")
        elif td is not None:
            log.append(f"WARN: TECHNICAL DATA unexpected type {type(td).__name__} — kept in specs")
            specs_work["TECHNICAL DATA"] = td

        # ── 4. FEATURED FEATURES -> GENERAL FEATURES (rename only, no merge) ─
        ff = specs_work.pop("FEATURED FEATURES", None)
        if ff is not None:
            specs_work["GENERAL FEATURES"] = ff
            log.append(f"FEATURED FEATURES ({len(ff)} items) -> GENERAL FEATURES (renamed)")

        # ── 5. CAPACITIES, CAPACITY, SUPPLIED EQUIPMENT: keep as separate blocks
        caps = specs_work.get("CAPACITIES")
        if caps is not None:
            log.append(f"CAPACITIES ({len(caps)} items) -> diller.en.specs.CAPACITIES (kept separate)")

        cap = specs_work.pop("CAPACITY", None)
        if cap is not None:
            # Normalize CAPACITY (singular, hand tools) -> CAPACITIES for consistency
            existing_caps = specs_work.get("CAPACITIES")
            if existing_caps is None:
                specs_work["CAPACITIES"] = cap
                log.append(f"CAPACITY ({len(cap)} items) -> CAPACITIES (normalized key)")
            else:
                specs_work["CAPACITIES"] = existing_caps + cap
                log.append(f"CAPACITY ({len(cap)} items) -> merged into existing CAPACITIES")

        se = specs_work.get("SUPPLIED EQUIPMENT")
        if se is not None:
            log.append(f"SUPPLIED EQUIPMENT ({len(se)} items) -> diller.en.specs (kept separate)")

        # Unexpected remaining keys (anything not in known set)
        known_keys = {"GENERAL FEATURES", "CAPACITIES", "SUPPLIED EQUIPMENT"}
        for k in list(specs_work.keys()):
            if k not in known_keys:
                _anomalies.append({"slug": slug, "issue": f"unexpected specs key: '{k}'"})
                log.append(f"WARN: unexpected specs key '{k}' — kept as-is")

        # Assemble diller.en.specs (preserve key order: GENERAL FEATURES, CAPACITIES, SUPPLIED EQUIPMENT)
        en_specs: dict = {}
        for key in ("GENERAL FEATURES", "CAPACITIES", "SUPPLIED EQUIPMENT"):
            if key in specs_work:
                en_specs[key] = specs_work.pop(key)
        for k, v in specs_work.items():  # any unexpected leftovers
            en_specs[k] = v

        if en_specs:
            m.setdefault("diller", {}).setdefault("en", {})["specs"] = en_specs
            log.append(f"diller.en.specs set: {list(en_specs.keys())}")
        else:
            log.append("specs: all keys empty after processing — diller.en.specs not written")

    # ── 6. pdf_catalog: remove top-level duplicate ─────────────────────────
    top_pdf = m.get("pdf_catalog")
    en_pdf  = m.get("diller", {}).get("en", {}).get("pdf_catalog")

    if top_pdf and en_pdf:
        del m["pdf_catalog"]
        log.append(f"pdf_catalog top-level removed (diller.en already has it)")
    elif top_pdf and not en_pdf:
        # Move top-level to diller.en
        m.setdefault("diller", {}).setdefault("en", {})["pdf_catalog"] = top_pdf
        del m["pdf_catalog"]
        log.append(f"pdf_catalog: moved top-level -> diller.en.pdf_catalog")
    elif not top_pdf and not en_pdf:
        log.append("pdf_catalog: absent everywhere — skip")

    # ── 7. type: add if missing ─────────────────────────────────────────────
    if "type" not in m:
        m["type"] = "machine"
        log.append("type: added 'machine'")
    else:
        log.append(f"type: already '{m['type']}' — skip")

    # ── 8. related_products: remove ────────────────────────────────────────
    if "related_products" in m:
        rp = m.pop("related_products")
        log.append(f"related_products: removed ({len(rp)} items)")

    # ── 9. Empty cleanup (per language) ────────────────────────────────────
    for lang, lang_data in list(m.get("diller", {}).items()):
        if not isinstance(lang_data, dict):
            continue
        for key in ("description", "pdf_catalog"):
            if key in lang_data and lang_data[key] == "":
                del lang_data[key]
                log.append(f"diller.{lang}.{key}: empty string removed")
        for key in ("images",):
            if key in lang_data and lang_data[key] == []:
                del lang_data[key]
                log.append(f"diller.{lang}.{key}: empty array removed")
        for key in ("specs",):
            if key in lang_data:
                v = lang_data[key]
                if not v or (isinstance(v, dict) and all(not vv for vv in v.values())):
                    del lang_data[key]
                    log.append(f"diller.{lang}.{key}: empty removed")
        for key in ("technical_data",):
            if key in lang_data and not lang_data[key]:
                del lang_data[key]
                log.append(f"diller.{lang}.{key}: empty removed")

    return m, log


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def unified_diff(before: dict, after: dict) -> str:
    a = json.dumps(before, ensure_ascii=False, indent=2).splitlines(keepends=True)
    b = json.dumps(after,  ensure_ascii=False, indent=2).splitlines(keepends=True)
    return "".join(difflib.unified_diff(a, b, fromfile="before", tofile="after"))


def find_machine(fragment: str) -> Path | None:
    """Partial slug match. Returns Path or prints error."""
    all_files = sorted(MACHINES_DIR.glob("*.json"))
    exact = [f for f in all_files if f.stem == fragment]
    if exact:
        return exact[0]
    partial = [f for f in all_files if fragment in f.stem]
    if len(partial) == 1:
        return partial[0]
    if len(partial) > 1:
        print(f"ERROR: '{fragment}' matches {len(partial)} files:")
        for p in partial:
            print(f"  {p.stem}")
        return None
    # No match — show nearest
    print(f"ERROR: No machine file matching '{fragment}'")
    # Suggest files containing any word from fragment
    words = fragment.replace("-", " ").replace("_", " ").split()
    suggestions = [f for f in all_files if any(w in f.stem for w in words)]
    if suggestions:
        print(f"Possible matches (by word):")
        for s in suggestions[:8]:
            data = load_json(s)
            name = data.get("diller", {}).get("en", {}).get("name", "—")
            print(f"  {s.stem}  ({name})")
    return None


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def build_report(results: list[dict]) -> str:
    now      = datetime.now().strftime("%Y-%m-%d %H:%M")
    changed  = [r for r in results if r["changed"]]
    anomalies = _anomalies

    # ── Pre-compute analytical sections ───────────────────────────────────

    # 1. Multi-subcategory machines
    multi_sc = []
    for r in results:
        sc = r["before"].get("subcategory", [])
        if isinstance(sc, list) and len(sc) > 1:
            multi_sc.append((r["slug"], sc))

    # 2. Empty cleanup per machine (log lines containing "empty" or "removed")
    cleanup_map = {}
    for r in results:
        cleaned = [l for l in r["log"] if "empty" in l.lower() or
                   ("removed" in l.lower() and "related_products" not in l)]
        if cleaned:
            cleanup_map[r["slug"]] = cleaned

    # 3. Spec key coverage per machine
    SPEC_KEYS = ("GENERAL FEATURES", "CAPACITIES", "SUPPLIED EQUIPMENT")
    spec_coverage = {}  # slug -> set of present keys (from BEFORE migration)
    for r in results:
        top = r["before"].get("specs") or {}
        present = set()
        if "FEATURED FEATURES" in top or "GENERAL FEATURES" in top:
            present.add("GENERAL FEATURES")
        if "CAPACITIES" in top or "CAPACITY" in top:
            present.add("CAPACITIES")
        if "SUPPLIED EQUIPMENT" in top:
            present.add("SUPPLIED EQUIPMENT")
        missing = [k for k in SPEC_KEYS if k not in present]
        if missing:
            spec_coverage[r["slug"]] = {"present": sorted(present), "missing": missing}

    # 4. Unexpected spec keys
    unexpected_map = {}
    for r in results:
        top = r["before"].get("specs") or {}
        known = {"TECHNICAL DATA", "FEATURED FEATURES", "GENERAL FEATURES",
                 "CAPACITIES", "CAPACITY", "SUPPLIED EQUIPMENT"}
        extra = [k for k in top if k not in known]
        if extra:
            unexpected_map[r["slug"]] = extra

    # ── Build markdown ────────────────────────────────────────────────────
    L = []  # lines accumulator

    L.append("# Gocmaksan Schema Migration — Dry-Run Report\n\n")
    L.append(f"**Tarih:** {now}  \n")
    L.append(f"**Toplam makine:** {len(results)}  \n")
    L.append(f"**Degisecek makine:** {len(changed)} / {len(results)}  \n")
    L.append(f"**Anomali:** {len(anomalies)}  \n\n")

    # ── Section A: Multi-subcategory ──────────────────────────────────────
    L.append("## A. Coklu Subcategory'li Makineler\n\n")
    if multi_sc:
        L.append(f"Toplam: **{len(multi_sc)} makine** subcategory array'i 2+ eleman iceriyor "
                 f"(array KORUNUYOR, degistirilmiyor).\n\n")
        # Group by combination
        combos: dict[str, list[str]] = {}
        for slug, sc in multi_sc:
            key = " + ".join(sc)
            combos.setdefault(key, []).append(slug)
        L.append("| Kombinasyon | Makine |\n")
        L.append("|---|---|\n")
        for combo, slugs in sorted(combos.items()):
            L.append(f"| `{combo}` | {', '.join(f'`{s}`' for s in slugs)} |\n")
    else:
        L.append("Tum makinelerde subcategory tek eleman veya eksik.\n")
    L.append("\n")

    # ── Section B: Empty cleanup ──────────────────────────────────────────
    L.append("## B. Empty Cleanup ile Kaldirilan Key'ler\n\n")
    if cleanup_map:
        L.append(f"**{len(cleanup_map)} makinede** empty cleanup tetiklendi:\n\n")
        L.append("| Makine | Kaldirilan |\n")
        L.append("|---|---|\n")
        for slug, lines_ in sorted(cleanup_map.items()):
            L.append(f"| `{slug}` | {'; '.join(lines_)} |\n")
    else:
        L.append("Hicbir makinede empty cleanup tetiklenmedi.\n")
    L.append("\n")

    # ── Section C: Spec key coverage ─────────────────────────────────────
    L.append("## C. Spec Key Kapsamı (GENERAL FEATURES / CAPACITIES / SUPPLIED EQUIPMENT)\n\n")
    if spec_coverage:
        L.append(f"**{len(spec_coverage)} makinede** en az 1 spec key eksik:\n\n")
        L.append("| Makine | Mevcut | Eksik |\n")
        L.append("|---|---|---|\n")
        for slug, info in sorted(spec_coverage.items()):
            present_str = ", ".join(f"`{k}`" for k in info["present"]) or "—"
            missing_str = ", ".join(f"`{k}`" for k in info["missing"])
            L.append(f"| `{slug}` | {present_str} | {missing_str} |\n")
    else:
        L.append("Tum makinelerde 3 spec key de mevcut.\n")
    L.append("\n")

    # ── Section D: Unexpected spec keys ──────────────────────────────────
    L.append("## D. Beklenmedik Spec Key'ler\n\n")
    if unexpected_map:
        L.append(f"**{len(unexpected_map)} makinede** beklenmeden spec key bulundu:\n\n")
        for slug, keys in sorted(unexpected_map.items()):
            L.append(f"- `{slug}`: {keys}\n")
    else:
        L.append("Hicbir makinede beklenmedik spec key yok. Temiz.\n")
    L.append("\n")

    # ── Section E: Anomalies ──────────────────────────────────────────────
    if anomalies:
        L.append("## E. Anomaliler\n\n")
        for a in anomalies:
            L.append(f"- `{a['slug']}`: {a['issue']}\n")
        L.append("\n")

    # ── Section F: Per-machine detail table ──────────────────────────────
    L.append("## F. Makine Bazinda Ozet\n\n")
    L.append("| Makine | Log satiri | Degisti? | Subcat | Spec keys |\n")
    L.append("|---|---|---|---|---|\n")
    for r in results:
        sc = r["before"].get("subcategory", "—")
        sc_str = str(sc) if isinstance(sc, list) else f'"{sc}"'
        after_specs = (r["after"].get("diller", {}).get("en", {}).get("specs") or {})
        spec_keys_str = ", ".join(after_specs.keys()) if after_specs else "—"
        changed_mark = "YES" if r["changed"] else "no"
        L.append(f"| `{r['slug']}` | {len(r['log'])} | {changed_mark} | {sc_str} | {spec_keys_str} |\n")

    return "".join(L)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Göçmaksan -> Yılmaz schema migration"
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Write changes (default: dry-run)"
    )
    parser.add_argument(
        "--single", metavar="SLUG_FRAGMENT",
        help="Process single machine matching this slug fragment"
    )
    parser.add_argument(
        "--report-out", metavar="PATH",
        help="Write dry-run report to this file (markdown)"
    )
    args = parser.parse_args()

    dry_run = not args.apply

    # Collect target files
    if args.single:
        path = find_machine(args.single)
        if not path:
            sys.exit(1)
        print(f"Matched: {path.name}\n")
        target_files = [path]
    else:
        target_files = sorted(MACHINES_DIR.glob("*.json"))

    if not target_files:
        print("ERROR: No .json files found in", MACHINES_DIR)
        sys.exit(1)

    # Backup (apply + full-run only)
    if args.apply and not args.single:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = MACHINES_DIR / f"_pre_migration_backup_{ts}"
        backup_dir.mkdir()
        for f in target_files:
            shutil.copy2(f, backup_dir / f.name)
        print(f"[OK] Backup: {backup_dir.relative_to(REPO_ROOT)}\n")

    # Process all files
    results = []
    for path in target_files:
        before = load_json(path)
        after, log = migrate_machine(before)
        diff = unified_diff(before, after)
        results.append({
            "slug":    before["slug"],
            "path":    path,
            "before":  before,
            "after":   after,
            "log":     log,
            "diff":    diff,
            "changed": bool(diff),
        })

    # ── Single-machine output ──────────────────────────────────────────────
    if args.single:
        r = results[0]
        print("MIGRATION LOG:")
        for line in r["log"]:
            prefix = "  [!]" if line.startswith("WARN") else "  [+]"
            print(f"{prefix} {line}")
        print("\n" + ("-" * 72))
        print("DIFF (before -> after):")
        print("-" * 72)
        if r["diff"]:
            print(r["diff"])
        else:
            print("  (no changes — machine already migrated)")
        if dry_run:
            print("\n[DRY-RUN] No files written. Pass --apply to commit changes.")
        return

    # ── Multi-machine output ───────────────────────────────────────────────
    report = build_report(results)

    if args.report_out:
        out = Path(args.report_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        print(f"Report -> {out}")
    else:
        print(report)

    if dry_run:
        changed_count = sum(1 for r in results if r["changed"])
        print(f"\n[DRY-RUN] {changed_count}/{len(results)} files would be written.")
        print("Pass --apply to execute.\n")
        return

    # ── Apply ──────────────────────────────────────────────────────────────
    written = 0
    for r in results:
        if r["changed"]:
            save_json(r["path"], r["after"])
            print(f"  WROTE {r['path'].name}")
            written += 1

    print(f"\n[OK] Applied: {written}/{len(results)} files written.")

    # Rebuild aggregate JSON
    if SYNC_SCRIPT.exists():
        print(f"\nRunning {SYNC_SCRIPT.name} ...")
        result = subprocess.run(
            [sys.executable, str(SYNC_SCRIPT)],
            capture_output=True, text=True
        )
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0:
            print("SYNC ERROR:", result.stderr)
            sys.exit(1)
        print("[OK] Aggregate JSON rebuilt.")
    else:
        print(f"\nWARN: sync script not found at {SYNC_SCRIPT}")
        print("Run manually: py tools/sync_machines_to_json.py")


if __name__ == "__main__":
    main()
