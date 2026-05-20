from __future__ import annotations

import argparse
import copy
import difflib
import json
import re
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "src" / "data" / "gocmaksan.json"


FEATURES: dict[str, list[str]] = {
    "standard_bending": [
        "Bending to the right and left",
        "Mechanical and electrical automation",
        "Bending at any angle",
        "Planetary reducer system",
        "Save up to 9 bending programs",
        "Digital control panel option",
    ],
    "portable_bending": [
        "Easy to carry",
        "Fixed center pin",
        "220 V / 380 V voltage options",
        "Digital control panel option",
        "Stirrup bending capability",
        "Programmable bending function",
    ],
    "portable_cutting": [
        "Portable construction-site design",
        "Easy to carry",
        "Hydraulic cutting system",
        "220 V / 380 V voltage options",
        "Digital control panel option",
        "Quick maintenance and spare parts access",
    ],
    "hydraulic_cutting": [
        "Hydraulic system",
        "Adjustable blade support",
        "Low maintenance costs",
        "Long-lasting use",
        "Reinforced steel body",
        "Quiet, safe, and environmentally friendly operation",
    ],
    "mechanical_cutting": [
        "Mechanical system",
        "High cutting performance",
        "Fast cutting cycle",
        "Foot pedal and arm control",
    ],
    "shear_cutting": [
        "Double-acting hydraulic system",
        "High cutting performance",
        "Manual and automatic control",
        "Hand and foot control",
        "Low energy consumption",
        "Durable steel body",
    ],
    "mesh_bending": [
        "Hydraulic system",
        "Mechanical system",
        "3 meter working length",
        "6 meter option",
        "45, 90, and 135 degree bending angles",
        "Cut in 7 seconds",
    ],
    "mesh_cutting": [
        "Mechanical system",
        "3 meter working length",
        "Cut in 7 seconds",
        "Portable wire mesh sliding table",
    ],
    "spiral_bending": [
        "Mechanical power transmission system",
        "Adjustable spiral range",
        "Suitable for bored pile and tunnel construction",
        "Precise and fast spiral bending",
    ],
    "axis_spiral": [
        "Spiral bending up to 50 mm",
        "Flat steel bending support",
        "Powered bending rollers",
        "Supporting bending conveyor",
    ],
    "stirrup_bending": [
        "Automatic repeat without changing angle",
        "Fixed hub",
        "Easy fixing",
        "Powerful reducer speed",
        "Patented daisy-pattern center hole",
        "Programmable bending function",
    ],
    "automatic_stirrup": [
        "Touchscreen control panel",
        "Intelligent software",
        "Pneumatic safety door",
        "Emergency stop system",
        "Foot pedal assistance",
        "Ergonomic machine access",
        "Decoiler supplied with the machine",
    ],
    "matrix_cutting_line": [
        "Servo-controlled cutting line",
        "Barcode reader option",
        "Remote control support",
        "Collecting bins",
        "Steel factory production workflow",
    ],
    "synclone_bending_line": [
        "Servo-controlled bending line",
        "Hydraulic and pneumatic systems",
        "Remote control support",
        "Collecting bins",
        "Steel factory production workflow",
    ],
    "combined_cut_bend": [
        "Combined cutting and bending operation",
        "Compact construction-site design",
        "Easy operation",
        "Practical maintenance access",
    ],
    "brick_cutting": [
        "Precise and fast cutting",
        "Wet and dry cutting modes",
        "Foldable legs for easy transport",
        "Labor and material savings",
    ],
    "power_trowel": [
        "Excellent results on concrete surfaces",
        "Economical low-fuel operation",
        "Ergonomic and safe design",
        "Quick blade adjustment",
    ],
    "compactor": [
        "Compact light-construction design",
        "Easy operation",
        "Durable compaction plate",
        "Suitable for site preparation work",
    ],
    "roller": [
        "Hydrostatic drive system",
        "Compact and portable construction",
        "Easy ergonomic operation",
        "Efficient surface compaction",
    ],
}


def clean_name(name: str) -> str:
    fixes = {
        "ConstructIon Steel Keys": "Construction Steel Keys",
        "Low Stool ScIssors": "Low Stool Scissors",
        "MATRIX 55": "Matrix 55",
        "MATIX 55S": "Matrix 55S",
        "MAX 40": "Max 40",
        "SYNCLONE 45S": "Synclone 45S",
    }
    return fixes.get(name, name)


def family_key(machine: dict[str, Any]) -> str:
    slug = machine["slug"]
    name = clean_name(machine["diller"]["en"].get("name", ""))
    categories = set(machine.get("categories", []))
    subcategory = set(machine.get("subcategory", []))

    if slug.startswith("gms-b-") or slug.startswith("gms-bs-"):
        return "standard_bending"
    if slug.startswith("gms-bt-") or slug.startswith("gms-mg-"):
        return "portable_bending"
    if slug == "gms-power-24-gocmaksan-portatif-insaat-demiri-kesme-makinasi":
        return "portable_cutting"
    if slug.startswith("gms-h-"):
        return "hydraulic_cutting"
    if slug.startswith("gms-m-"):
        return "mechanical_cutting"
    if slug.startswith("gms-sh-"):
        return "shear_cutting"
    if slug.startswith("gms-hb-"):
        return "mesh_bending"
    if slug.startswith("gms-mh-"):
        return "mesh_cutting"
    if slug.startswith("gms-sx-"):
        return "spiral_bending"
    if slug.startswith("gms-axis-"):
        return "axis_spiral"
    if slug.startswith("gms-sl-"):
        return "stirrup_bending"
    if slug.startswith("gms-sls-"):
        return "automatic_stirrup"
    if slug.startswith("gms-matrix-"):
        return "matrix_cutting_line"
    if slug.startswith("gms-synclone-"):
        return "synclone_bending_line"
    if slug.startswith("gms-max-"):
        return "combined_cut_bend"
    if slug.startswith("gms-bcz-"):
        return "brick_cutting"
    if slug == "gms-perdah-makinasi" or name == "Power Trowel":
        return "power_trowel"
    if slug == "gms-kompaktor":
        return "compactor"
    if slug.startswith("gms-rl-"):
        return "roller"
    if "Hand Tools" in categories or "Hand Tools" in subcategory:
        return "hand_tool"
    return "generic"


def description_for(machine: dict[str, Any], key: str) -> str:
    name = clean_name(machine["diller"]["en"].get("name", "Gocmaksan machine"))
    templates = {
        "standard_bending": f"{name} is a rebar bending machine for construction-site steel processing.",
        "portable_bending": f"{name} is a portable rebar bending machine for construction-site steel processing.",
        "portable_cutting": f"{name} is a portable hydraulic rebar cutting machine for construction-site use.",
        "hydraulic_cutting": f"{name} is a hydraulic rebar cutting machine for construction-site steel processing.",
        "mechanical_cutting": f"{name} is a mechanical rebar cutting machine for construction-site steel processing.",
        "shear_cutting": f"{name} is a hydraulic rebar cutting machine for high-capacity construction-site steel processing.",
        "mesh_bending": f"{name} is a mesh bending and cutting machine for steel factory applications.",
        "mesh_cutting": f"{name} is a mesh cutting machine for steel factory applications.",
        "spiral_bending": f"{name} is a spiral rebar bending machine for construction-site steel processing.",
        "axis_spiral": f"{name} is a spiral bending machine for steel factory and heavy rebar applications.",
        "stirrup_bending": f"{name} is a stirrup bending machine for fast and repeatable rebar shaping.",
        "automatic_stirrup": f"{name} is an automatic stirrup bending machine for steel factory production.",
        "matrix_cutting_line": f"{name} is a rebar cutting line for steel factory production workflows.",
        "synclone_bending_line": f"{name} is a rebar bending line for steel factory production workflows.",
        "combined_cut_bend": f"{name} is a combined rebar cutting and bending machine for construction-site use.",
        "brick_cutting": f"{name} is a brick and block cutting machine for light construction work.",
        "power_trowel": f"{name} is a power trowel for finishing concrete surfaces.",
        "compactor": f"{name} is a compactor for light construction site preparation.",
        "roller": f"{name} is a double-drum roller for light construction compaction work.",
        "hand_tool": f"{name} is a hand tool for construction-site rebar work.",
        "generic": f"{name} is a Gocmaksan machine for construction and steel processing applications.",
    }
    return templates[key]


def features_for(machine: dict[str, Any], key: str) -> list[str] | None:
    if key == "hand_tool":
        return None
    return FEATURES.get(key, [])


def normalize_names(machine: dict[str, Any]) -> None:
    en = machine.setdefault("diller", {}).setdefault("en", {})
    en["name"] = clean_name(en.get("name", ""))


def sanitize(data: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    updated = copy.deepcopy(data)
    stats = {
        "descriptions_changed": 0,
        "features_changed": 0,
        "names_changed": 0,
        "feature_keys_removed": 0,
    }

    for machine in updated:
        before_name = machine.get("diller", {}).get("en", {}).get("name", "")
        normalize_names(machine)
        if machine.get("diller", {}).get("en", {}).get("name", "") != before_name:
            stats["names_changed"] += 1

        key = family_key(machine)
        en = machine.setdefault("diller", {}).setdefault("en", {})
        new_description = description_for(machine, key)
        if en.get("description", "") != new_description:
            en["description"] = new_description
            stats["descriptions_changed"] += 1

        specs = machine.setdefault("specs", {})
        new_features = features_for(machine, key)
        if new_features is None:
            if "FEATURED FEATURES" in specs:
                specs.pop("FEATURED FEATURES", None)
                stats["feature_keys_removed"] += 1
            continue

        if specs.get("FEATURED FEATURES") != new_features:
            specs["FEATURED FEATURES"] = new_features
            stats["features_changed"] += 1

    return updated, stats


def compact(machine: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": machine.get("diller", {}).get("en", {}).get("name", ""),
        "description": machine.get("diller", {}).get("en", {}).get("description", ""),
        "FEATURED FEATURES": machine.get("specs", {}).get("FEATURED FEATURES", []),
    }


def diff_for(before: dict[str, Any], after: dict[str, Any]) -> str:
    left = json.dumps(compact(before), ensure_ascii=False, indent=2).splitlines()
    right = json.dumps(compact(after), ensure_ascii=False, indent=2).splitlines()
    return "\n".join(difflib.unified_diff(left, right, fromfile="before", tofile="after", lineterm=""))


def suspicious_counts(data: list[dict[str, Any]]) -> dict[str, int]:
    tr_re = re.compile(r"[ğĞıİşŞüÜöÖçÇ]")
    bad_re = re.compile(
        r"S I N C E|PORTAT|TEKN|TECHNICAL SPECIFICATIONS|CAPACTIES|model-specific PDF data|www\\.|\\bØ\\b",
        re.I,
    )
    bad_desc = 0
    bad_features = 0
    for machine in data:
        desc = machine.get("diller", {}).get("en", {}).get("description", "")
        if tr_re.search(desc) or bad_re.search(desc) or desc.isupper() or desc.islower():
            bad_desc += 1
        for feature in machine.get("specs", {}).get("FEATURED FEATURES", []) or []:
            text = str(feature)
            if tr_re.search(text) or bad_re.search(text) or "Ø" in text or text == "S I N C E":
                bad_features += 1
                break
    return {"suspicious_descriptions": bad_desc, "suspicious_feature_lists": bad_features}


def main() -> int:
    parser = argparse.ArgumentParser(description="Clean Gocmaksan English descriptions and featured features.")
    parser.add_argument("--apply", action="store_true", help="Write cleaned data to src/data/gocmaksan.json.")
    args = parser.parse_args()

    original = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    updated, stats = sanitize(original)

    examples = [
        "gms-h-38-s-gocmaksan-insaat-demiri-kesme-makinasi",
        "gms-power-24-gocmaksan-portatif-insaat-demiri-kesme-makinasi",
        "gms-b-45x1-gocmaksan-insaat-demiri-bukme-makinasi",
        "gms-hb-12x6-gocmaksan-hasir-demir-bukme-makinasi",
        "gms-sls-12-gocmaksan-otomatik-etriye-bukme-makinasi",
    ]
    by_slug_before = {machine["slug"]: machine for machine in original}
    by_slug_after = {machine["slug"]: machine for machine in updated}

    print("=== Gocmaksan English copy cleanup ===")
    print(f"mode: {'apply' if args.apply else 'dry-run'}")
    print(f"machine count: {len(original)}")
    print(f"descriptions changed: {stats['descriptions_changed']}")
    print(f"feature lists changed: {stats['features_changed']}")
    print(f"feature keys removed: {stats['feature_keys_removed']}")
    print(f"names changed: {stats['names_changed']}")
    print(f"before suspicious: {suspicious_counts(original)}")
    print(f"after suspicious: {suspicious_counts(updated)}")
    print()
    print("Example diffs:")
    for slug in examples:
        print(f"--- {slug} ---")
        print(diff_for(by_slug_before[slug], by_slug_after[slug]) or "(no change)")

    if args.apply:
        DATA_PATH.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\nWrote {DATA_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
