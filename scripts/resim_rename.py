#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rename Yilmaz image files to {slug}_{index}.{ext} and update yilmaz.json paths.
"""

from __future__ import annotations

import json
import re
import sys
import uuid
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
JSON_PATH = PROJECT_ROOT / "src" / "data" / "yilmaz.json"
IMG_DIR = PROJECT_ROOT / "public" / "images" / "yilmaz"
LOG_PATH = SCRIPT_DIR / "resim_rename_log.txt"

EN_KEYWORDS = (
    "machine",
    "center",
    "cutting",
    "router",
    "welding",
    "trolley",
    "conveyor",
    "press",
    "miter",
)
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"}


def natural_sort_key(text: str) -> list[object]:
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", text.lower())]


def trailing_number(name: str) -> int:
    match = re.search(r"(\d+)(?=\.[^.]+$)", name)
    return int(match.group(1)) if match else 10**9


def is_en_named(filename: str) -> bool:
    lowered = filename.lower()
    return any(keyword in lowered for keyword in EN_KEYWORDS)


def slug_prefix_candidates(slug: str) -> list[str]:
    parts = slug.lower().split("-")
    candidates: list[str] = []

    # Full slug and progressively shorter prefixes.
    for size in range(len(parts), 1, -1):
        candidates.append("-".join(parts[:size]))

    # Model-code-like prefixes such as ack-420-s or aim-7510.
    model_parts: list[str] = []
    for index, part in enumerate(parts):
        model_parts.append(part)
        if any(ch.isdigit() for ch in part):
            if index + 1 < len(parts) and len(parts[index + 1]) <= 3 and parts[index + 1].isalpha():
                model_parts.append(parts[index + 1])
            break
    if len(model_parts) >= 2:
        candidates.insert(0, "-".join(model_parts))

    seen: set[str] = set()
    unique = [candidate for candidate in candidates if not (candidate in seen or seen.add(candidate))]
    return sorted(unique, key=lambda item: (-len(item), item))


def best_slug_match(filename: str, slugs: list[str], candidates_by_slug: dict[str, list[str]]) -> tuple[str | None, str | None]:
    lowered = filename.lower()
    best_slug: str | None = None
    best_prefix: str | None = None

    for slug in slugs:
        for prefix in candidates_by_slug[slug]:
            if lowered.startswith(prefix):
                if best_prefix is None or len(prefix) > len(best_prefix):
                    best_slug = slug
                    best_prefix = prefix
                break

    return best_slug, best_prefix


def sorted_files(files: list[Path]) -> list[Path]:
    return sorted(
        files,
        key=lambda path: (
            0 if is_en_named(path.name) else 1,
            trailing_number(path.name),
            natural_sort_key(path.name),
        ),
    )


def main() -> int:
    if not JSON_PATH.exists():
        print(f"JSON not found: {JSON_PATH}")
        return 1
    if not IMG_DIR.exists():
        print(f"Image directory not found: {IMG_DIR}")
        return 1

    data = json.loads(JSON_PATH.read_text(encoding="utf-8-sig"))
    slug_to_machine = {machine["slug"]: machine for machine in data}
    slugs = list(slug_to_machine.keys())
    candidates_by_slug = {slug: slug_prefix_candidates(slug) for slug in slugs}

    matched_files: dict[str, list[Path]] = {slug: [] for slug in slugs}
    unmatched_files: list[str] = []

    for file_path in sorted(IMG_DIR.iterdir(), key=lambda item: natural_sort_key(item.name)):
        if not file_path.is_file() or file_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        slug, _prefix = best_slug_match(file_path.name, slugs, candidates_by_slug)
        if slug is None:
            unmatched_files.append(file_path.name)
            continue
        matched_files[slug].append(file_path)

    rename_plan: list[tuple[Path, Path]] = []
    updated_machine_count = 0
    renamed_file_count = 0
    missing_machine_images: list[str] = []
    duplicate_target_names: list[str] = []
    seen_targets: set[str] = set()
    log_lines: list[str] = []

    for machine in data:
        slug = machine["slug"]
        files = sorted_files(matched_files.get(slug, []))
        image_paths = [f"/images/yilmaz/{slug}_{index}{file_path.suffix.lower()}" for index, file_path in enumerate(files, start=1)]

        if files:
            updated_machine_count += 1
        else:
            missing_machine_images.append(slug)

        for language_data in machine.get("diller", {}).values():
            if "images" in language_data:
                language_data["images"] = image_paths

        log_lines.append(f"[{slug}] {len(files)} file(s)")

        for index, file_path in enumerate(files, start=1):
            target = IMG_DIR / f"{slug}_{index}{file_path.suffix.lower()}"
            if target.name in seen_targets:
                duplicate_target_names.append(target.name)
            seen_targets.add(target.name)
            if file_path.name != target.name:
                rename_plan.append((file_path, target))
                renamed_file_count += 1
            log_lines.append(f"{file_path.name} -> {target.name}")

    if duplicate_target_names:
        print("Duplicate target names detected:")
        for name in duplicate_target_names:
            print(name)
        return 1

    temp_plan: list[tuple[Path, Path]] = []
    for source, target in rename_plan:
        temp_name = f"__renaming__{uuid.uuid4().hex}{source.suffix.lower()}"
        temp_path = IMG_DIR / temp_name
        source.rename(temp_path)
        temp_plan.append((temp_path, target))

    for temp_path, target in temp_plan:
        temp_path.rename(target)

    JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary_lines = [
        f"total_files_in_dir={sum(1 for path in IMG_DIR.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS)}",
        f"renamed_files={renamed_file_count}",
        f"updated_machines={updated_machine_count}",
        f"unmatched_files={len(unmatched_files)}",
        f"machines_without_images={len(missing_machine_images)}",
        "",
    ]
    if unmatched_files:
        summary_lines.append("[unmatched_files]")
        summary_lines.extend(unmatched_files)
        summary_lines.append("")
    if missing_machine_images:
        summary_lines.append("[machines_without_images]")
        summary_lines.extend(missing_machine_images)
        summary_lines.append("")
    summary_lines.append("[rename_map]")
    summary_lines.extend(log_lines)

    LOG_PATH.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"renamed_files={renamed_file_count}")
    print(f"updated_machines={updated_machine_count}")
    print(f"unmatched_files={len(unmatched_files)}")
    print(f"machines_without_images={len(missing_machine_images)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
