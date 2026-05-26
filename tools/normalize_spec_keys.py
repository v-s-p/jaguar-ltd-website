#!/usr/bin/env python3
"""
normalize_spec_keys.py
======================
Normalizes spec block key names to snake_case across all Yilmaz + GMS machine JSON files.

Usage:
  python tools/normalize_spec_keys.py                   # dry-run (all)
  python tools/normalize_spec_keys.py --apply           # write changes
  python tools/normalize_spec_keys.py --single pim-6508 # dry-run one machine
  python tools/normalize_spec_keys.py --single pim-6508 --apply
  python tools/normalize_spec_keys.py --report-out _audit/NORMALIZE_DRYRUN_REPORT.md
"""

import sys
import io
import json
import shutil
import argparse
import datetime
from pathlib import Path

# UTF-8 stdout for Cyrillic content on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)

REPO_ROOT = Path(__file__).parent.parent
YILMAZ_DIR  = REPO_ROOT / "src" / "data" / "machines" / "yilmaz"
GMS_DIR     = REPO_ROOT / "src" / "data" / "machines" / "gocmaksan"
SYNC_SCRIPT = REPO_ROOT / "scripts" / "sync_machines_to_json.py"

# ---------------------------------------------------------------------------
# Key mapping: old key -> snake_case key
# ---------------------------------------------------------------------------
KEY_MAP: dict[str, str] = {
    # EN (Yilmaz + GMS)
    "STANDARD ACCESSORIES":  "standard_accessories",
    "OPTIONAL ACCESSORIES":  "optional_accessories",
    "GENERAL FEATURES":      "general_features",
    "SUPPLIED EQUIPMENT":    "supplied_equipment",
    "CAPACITIES":            "capacities",
    # Yilmaz BG Cyrillic
    "СТАНДАРТНИ АКСЕСОАРИ":  "standard_accessories",
    "ОПЦИОНАЛНИ АКСЕСОАРИ":  "optional_accessories",
    "ОБЩИ ХАРАКТЕРИСТИКИ":   "general_features",
    # Yilmaz RU Cyrillic
    "СТАНДАРТНЫЕ АКСЕССУАРЫ":  "standard_accessories",
    "ДОПОЛНИТЕЛЬНЫЕ АКСЕССУАРЫ": "optional_accessories",
    "ОБЩИЕ ХАРАКТЕРИСТИКИ":    "general_features",
}

SNAKE_CASE_KEYS = set(KEY_MAP.values())  # already-normalized keys -> skip


def is_already_normalized(key: str) -> bool:
    return key in SNAKE_CASE_KEYS


def normalize_specs(specs: dict) -> tuple[dict, list[str], list[str]]:
    """Return (new_specs, renames, anomalies).

    renames:   list of "OLD -> new" strings
    anomalies: list of keys not in KEY_MAP and not already snake_case
    """
    new_specs: dict = {}
    renames: list[str] = []
    anomalies: list[str] = []

    for key, value in specs.items():
        if is_already_normalized(key):
            new_specs[key] = value  # already correct
        elif key in KEY_MAP:
            new_key = KEY_MAP[key]
            new_specs[new_key] = value
            renames.append(f"{key!r} -> {new_key!r}")
        else:
            # unknown key — preserve as-is, flag as anomaly
            new_specs[key] = value
            anomalies.append(repr(key))

    return new_specs, renames, anomalies


def process_machine(data: dict) -> tuple[dict, list[str]]:
    """Apply normalization to all diller.{lang}.specs.

    Returns (modified_data, log_lines).
    """
    log: list[str] = []
    changed = False

    diller = data.get("diller", {})
    if not isinstance(diller, dict):
        return data, log

    for lang in ("en", "bg", "ru"):
        lang_data = diller.get(lang)
        if not isinstance(lang_data, dict):
            continue
        specs = lang_data.get("specs")
        if not isinstance(specs, dict) or not specs:
            continue

        new_specs, renames, anomalies = normalize_specs(specs)

        if renames:
            changed = True
            for r in renames:
                log.append(f"  [{lang}] {r}")
            lang_data["specs"] = new_specs

        for a in anomalies:
            log.append(f"  [{lang}] ANOMALY: unknown key {a} — kept as-is")

    if not changed and not any("ANOMALY" in l for l in log):
        log.append("  (no changes needed)")

    return data, log


def collect_files(single: str | None) -> list[Path]:
    files: list[Path] = []
    for d in (YILMAZ_DIR, GMS_DIR):
        for p in sorted(d.glob("*.json")):
            if p.stem.startswith("_") or p.suffix != ".json":
                continue
            # skip .bak files (they have .json.bak extension but glob *.json won't catch them)
            files.append(p)

    if single:
        fragment = single.lower()
        matches = [f for f in files if fragment in f.stem.lower()]
        if not matches:
            print(f"[!] No file found matching '{single}'. Available slugs:")
            for f in files[:10]:
                print(f"    {f.stem}")
            sys.exit(1)
        return matches

    return files


def make_backup(files: list[Path]) -> Path:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    for f in files:
        brand_dir = f.parent
        backup_dir = brand_dir / f"_pre_normalize_backup_{ts}"
        backup_dir.mkdir(exist_ok=True)
        shutil.copy2(f, backup_dir / f.name)
    # return last backup_dir (all files share same timestamp)
    brand_dir = files[0].parent
    return brand_dir.parent / f"_pre_normalize_backup_{ts}"  # conceptual ref


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize spec keys to snake_case")
    parser.add_argument("--apply", action="store_true", help="Write changes to disk")
    parser.add_argument("--single", metavar="SLUG", help="Process only matching slug(s)")
    parser.add_argument("--report-out", metavar="PATH", help="Write report to file")
    args = parser.parse_args()

    dry_run = not args.apply
    mode = "DRY-RUN" if dry_run else "APPLY"
    print(f"=== normalize_spec_keys.py [{mode}] ===\n")

    files = collect_files(args.single)
    print(f"Files to process: {len(files)}\n")

    results: list[dict] = []  # {slug, path, changed, renames_count, log, anomalies}

    for path in files:
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception as e:
            print(f"[!] Cannot read {path.name}: {e}")
            continue

        slug = data.get("slug", path.stem)
        new_data, log = process_machine(data)

        renames_count = sum(1 for l in log if "->" in l)
        anomaly_count = sum(1 for l in log if "ANOMALY" in l)
        changed = renames_count > 0

        results.append({
            "slug": slug,
            "path": path,
            "brand": "yilmaz" if YILMAZ_DIR in path.parents else "gocmaksan",
            "changed": changed,
            "renames": renames_count,
            "anomalies": anomaly_count,
            "log": log,
            "data": new_data,
        })

        status = "[*]" if changed else "[ ]"
        anom_tag = f" +{anomaly_count} ANOMALY" if anomaly_count else ""
        print(f"{status} {slug}{anom_tag}")
        if changed or anomaly_count:
            for line in log:
                print(line)

    # Summary
    total_changed = sum(1 for r in results if r["changed"])
    total_renames = sum(r["renames"] for r in results)
    total_anomalies = sum(r["anomalies"] for r in results)
    print(f"\n{'='*60}")
    print(f"Summary: {len(results)} files, {total_changed} with changes")
    print(f"  Total renames: {total_renames}")
    print(f"  Total anomalies: {total_anomalies}")

    if dry_run:
        print("\n[DRY-RUN] No files written. Pass --apply to apply.")
    else:
        # Backup
        changed_files = [r["path"] for r in results if r["changed"]]
        if changed_files:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            yilmaz_changed = [r for r in results if r["changed"] and r["brand"] == "yilmaz"]
            gms_changed    = [r for r in results if r["changed"] and r["brand"] == "gocmaksan"]
            for brand, brand_dir, brand_results in [
                ("yilmaz",     YILMAZ_DIR, yilmaz_changed),
                ("gocmaksan",  GMS_DIR,    gms_changed),
            ]:
                if not brand_results:
                    continue
                backup_dir = brand_dir / f"_pre_normalize_backup_{ts}"
                backup_dir.mkdir(exist_ok=True)
                for r in brand_results:
                    shutil.copy2(r["path"], backup_dir / r["path"].name)
                print(f"[OK] Backup: {backup_dir}")

            # Write
            for r in results:
                if not r["changed"]:
                    continue
                with open(r["path"], "w", encoding="utf-8") as fh:
                    json.dump(r["data"], fh, ensure_ascii=False, indent=2)
                    fh.write("\n")
            print(f"[OK] Wrote {total_changed} files.")

            # Sync aggregate JSONs
            if SYNC_SCRIPT.exists():
                import subprocess
                print("\n[*] Running sync_machines_to_json.py ...")
                result = subprocess.run(
                    [sys.executable, str(SYNC_SCRIPT)],
                    capture_output=True, text=True, cwd=str(REPO_ROOT)
                )
                if result.returncode == 0:
                    print("[OK] Sync complete.")
                else:
                    print(f"[!] Sync exited {result.returncode}:\n{result.stderr[:500]}")
            else:
                print(f"[!] Sync script not found at {SYNC_SCRIPT} — run manually.")
        else:
            print("[OK] No files needed changes.")

    # Report file
    if args.report_out:
        report_path = REPO_ROOT / args.report_out
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines = build_report(results, mode, total_changed, total_renames, total_anomalies)
        with open(report_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        print(f"\n[OK] Report written: {report_path}")


def build_report(results: list[dict], mode: str, total_changed: int, total_renames: int, total_anomalies: int) -> list[str]:
    lines: list[str] = []
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines.append(f"# Spec Key Normalize — {mode} Report")
    lines.append(f"_Generated: {now}_\n")
    lines.append(f"**Files scanned:** {len(results)}  |  **Changed:** {total_changed}  |  **Total renames:** {total_renames}  |  **Anomalies:** {total_anomalies}\n")

    # A: machines with changes
    changed = [r for r in results if r["changed"]]
    lines.append(f"## A — Changed Machines ({len(changed)})\n")
    if changed:
        lines.append("| Slug | Brand | Renames | Details |")
        lines.append("|------|-------|---------|---------|")
        for r in changed:
            detail = "; ".join(l.strip() for l in r["log"] if "->" in l)
            lines.append(f"| `{r['slug']}` | {r['brand']} | {r['renames']} | {detail} |")
    else:
        lines.append("_None_")

    # B: anomalies
    anomalies = [r for r in results if r["anomalies"] > 0]
    lines.append(f"\n## B — Anomalies ({len(anomalies)} machines)\n")
    if anomalies:
        for r in anomalies:
            lines.append(f"- `{r['slug']}` ({r['brand']})")
            for l in r["log"]:
                if "ANOMALY" in l:
                    lines.append(f"  - {l.strip()}")
    else:
        lines.append("_None — all spec keys are either in the mapping or already snake_case._")

    # C: unchanged (summary count only)
    unchanged_count = len(results) - len(changed)
    lines.append(f"\n## C — Unchanged ({unchanged_count} machines)\n")
    lines.append(f"These machines either have no specs or all spec keys are already snake_case.\n")

    # D: per-machine table
    lines.append("## D — Full Machine Table\n")
    lines.append("| Slug | Brand | Changed | Renames | Anomalies |")
    lines.append("|------|-------|---------|---------|-----------|")
    for r in results:
        lines.append(f"| `{r['slug']}` | {r['brand']} | {'yes' if r['changed'] else 'no'} | {r['renames']} | {r['anomalies']} |")

    return lines


if __name__ == "__main__":
    main()
