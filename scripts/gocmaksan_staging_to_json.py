from __future__ import annotations

import argparse
import copy
import difflib
import hashlib
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "src" / "data" / "gocmaksan.json"
STAGING_DIR = PROJECT_ROOT / "pdf_extraction" / "gocmaksan" / "text"
PDF_IMAGE_DIR = PROJECT_ROOT / "pdf_extraction" / "gocmaksan" / "images"
PUBLIC_IMAGE_DIR = PROJECT_ROOT / "public" / "images" / "gocmaksan"

TARGET_SPEC_KEYS = ("TECHNICAL DATA", "FEATURED FEATURES", "CAPACITIES")
CAPACITY_LABELS = ("45 kg/mm2", "65 kg/mm2", "85 kg/mm2")
EMPTY_MARKERS = {"", "(none)", "none", "no local pdf available; web pdf lookup deferred to later phase."}
MIN_IMAGE_BYTES = 5 * 1024
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

TECHNICAL_PAIR_KEYS = (
    "Single Strand Processing Wire Diameter",
    "Double Strand Processing Wire Diameter",
    "Bending Type",
    "Bending Capacity",
    "Driving System",
    "Driving Motor Power",
    "Driving Speed",
    "Bending Motor Power",
    "Bending Speed",
    "Cutting Motor Power",
    "Length Tolerance",
    "Bending Tolerance",
    "Compressor Needed",
    "Working Pressure (Bar)",
    "Voltage",
    "Driving Gearbox",
    "Control Panel Type",
    "Machine Dimensions",
    "Machine Weight",
    "Decoiler Weight",
    "Language",
    "HS Code",
    "Bending motor",
    "Bending Motor",
    "Roller Motor",
    "Supporting Roller Motor",
    "Weight",
)

TURKISH_FEATURE_MAP = {
    "planet reduktor": "Planetary reducer system",
    "dijital kumanda ekrani opsiyonu": "Digital control panel option",
    "kolay tasinir": "Easy to carry",
    "ozel etriye basligi": "Special stirrup bending pin",
    "tasima kolayligi": "Easy to handle",
    "portatif cozumler": "Portable solutions",
    "hidrolik sistem": "Hydraulic system",
    "ayarlanabilir bicak destegi": "Adjustable blade support",
    "dusuk bakim maliyetleri": "Low maintenance costs",
    "uzun omurlu kullanim": "Long-lasting use",
    "guclendirilmis celik govde": "Reinforced steel body",
    "mekanik sistem": "Mechanical system",
    "yuksek kesim performansi": "High cutting performance",
    "el ve ayakla kontrol kabiliyeti": "Foot pedal and arm control",
    "manuel ve otomatik kontrol opsiyonu": "Manual and automatic control option",
}

FEATURE_NORMALIZATION = {
    "planetery reducer system": "Planetary reducer system",
    "program saving option": "Program saving option",
    "digital control options": "Digital control panel option",
    "220 v / 380v options": "220 V / 380 V options",
    "easy to carry": "Easy to carry",
    "easy to handle": "Easy to handle",
    "portable solution on construction site": "Portable solution on construction site",
    "hydraulic system": "Hydraulic system",
    "adjustable blade friendly": "Adjustable blade support",
    "adjustable blade stopper": "Adjustable blade support",
    "easy maintenance": "Easy maintenance",
    "long lasting": "Long-lasting use",
    "mechanical system": "Mechanical system",
    "high cutting performance": "High cutting performance",
    "foot pedal and arm control": "Foot pedal and arm control",
    "can be controlled manual and automatic": "Manual and automatic control",
}

DESCRIPTION_TEMPLATES = {
    "REBAR BENDING MACHINES": "{name} is a rebar bending machine with model-specific PDF data for technical specifications, bending capacities, and site-oriented rebar processing.",
    "REBAR CUTTING MACHINES": "{name} is a rebar cutting machine with model-specific PDF data for technical specifications, cutting capacities, and construction-site steel processing.",
    "PORTABLE REBAR BENDING": "{name} is a portable rebar bending machine with model-specific PDF data for compact site use, technical specifications, and bending capacities.",
    "PORTABLE CUTTING": "{name} is a portable cutting and bending machine with model-specific PDF data for compact site use, technical specifications, and capacities.",
    "MESH BENDING": "{name} is a mesh bending and cutting machine with model-specific PDF data for steel factory use, hydraulic operation, and bending or cutting capacities.",
    "SPIRAL BENDING": "{name} is a spiral bending machine with model-specific PDF data for spiral rebar production, technical specifications, and bending capacities.",
    "STIRRUP BENDING": "{name} is a stirrup bending machine with model-specific PDF data for fast, precise stirrup production, technical details, and processing capacities.",
    "LIGHT CONSTRUCTION": "{name} is a light construction machine with PDF-sourced staging data for model-specific features and technical information.",
}


@dataclass
class StagingDoc:
    slug: str
    sections: dict[str, list[str]]
    metadata: dict[str, str]
    en_name: str = ""
    categories: list[str] = field(default_factory=list)
    subcategory: list[str] = field(default_factory=list)


@dataclass
class ParsedStaging:
    slug: str
    description: str = ""
    technical_data: dict[str, str] = field(default_factory=dict)
    featured_features: list[str] = field(default_factory=list)
    capacities: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class ImageMergeReport:
    added: int = 0
    duplicates_skipped: int = 0
    size_skipped: int = 0
    missing_slug_dirs: int = 0
    appended_by_slug: dict[str, list[str]] = field(default_factory=dict)


def clean_text(value: str) -> str:
    value = (value or "").replace("\u00a0", " ")
    value = value.replace("\u2044", "/")
    return re.sub(r"\s+", " ", value).strip()


def file_md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def strip_bullet(value: str) -> str:
    value = clean_text(value)
    return re.sub(r"^\s*[-*]\s*", "", value).strip()


def ascii_key(value: str) -> str:
    replacements = {
        "\u0131": "i",
        "\u0130": "i",
        "\u015f": "s",
        "\u015e": "s",
        "\u011f": "g",
        "\u011e": "g",
        "\u00fc": "u",
        "\u00dc": "u",
        "\u00f6": "o",
        "\u00d6": "o",
        "\u00e7": "c",
        "\u00c7": "c",
    }
    lowered = value.lower()
    for src, dst in replacements.items():
        lowered = lowered.replace(src, dst)
    return re.sub(r"\s+", " ", lowered).strip()


def compact_model(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def seo_slug(value: str) -> str:
    value = ascii_key(value)
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "gocmaksan-machine"


def normalize_number(value: str) -> str:
    value = clean_text(value)
    return value.replace(",", ".")


def normalize_dimension(value: str) -> str:
    parts = [normalize_number(part) for part in re.split(r"\s*[x/]\s*", clean_text(value))]
    return " x ".join(part for part in parts if part)


def normalize_capacity_pair(value: str) -> str:
    match = re.search(r"\u00d8\s*([0-9]+)\s*x\s*([0-9]+)", value, flags=re.I)
    if not match:
        match = re.search(r"Ø\s*([0-9]+)\s*x\s*([0-9]+)", value, flags=re.I)
    if not match:
        return clean_text(value)
    return f"\u00d8 {match.group(1)}x{match.group(2)}"


def is_empty_list(lines: list[str]) -> bool:
    real = [strip_bullet(line).lower() for line in lines if strip_bullet(line)]
    return not real or all(line in EMPTY_MARKERS for line in real)


def parse_markdown(path: Path) -> StagingDoc:
    lines = path.read_text(encoding="utf-8").splitlines()
    slug = path.stem
    sections: dict[str, list[str]] = {}
    metadata: dict[str, str] = {}
    current: str | None = None

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("## "):
            current = line[3:].strip().lower()
            sections[current] = []
            continue
        if current:
            sections[current].append(line)
            continue
        if line.startswith("- ") and ":" in line:
            key, value = line[2:].split(":", 1)
            metadata[key.strip().lower()] = value.strip().strip("`")

    doc = StagingDoc(slug=slug, sections=sections, metadata=metadata)
    for line in sections.get("machine context", []):
        item = strip_bullet(line)
        if item.lower().startswith("en name:"):
            doc.en_name = item.split(":", 1)[1].strip()
        elif item.lower().startswith("categories:"):
            doc.categories = [part.strip() for part in item.split(":", 1)[1].split(",") if part.strip()]
        elif item.lower().startswith("subcategory:"):
            doc.subcategory = [part.strip(" []'\"") for part in item.split(":", 1)[1].split(",") if part.strip(" []'\"")]
    return doc


def section_items(doc: StagingDoc, section_name: str) -> list[str]:
    lines = doc.sections.get(section_name, [])
    if is_empty_list(lines):
        return []
    return [strip_bullet(line) for line in lines if strip_bullet(line) and strip_bullet(line).lower() not in EMPTY_MARKERS]


def raw_items(doc: StagingDoc) -> list[str]:
    return section_items(doc, "raw intro/body text")


def title_items(doc: StagingDoc) -> list[str]:
    return section_items(doc, "title candidates")


def model_variants(doc: StagingDoc, machine: dict[str, Any] | None = None) -> list[str]:
    values: list[str] = []
    if doc.en_name:
        values.append(doc.en_name)
    if machine:
        name = machine.get("diller", {}).get("en", {}).get("name", "")
        if name:
            values.append(name)
    slug_parts = re.sub(r"^gms-", "", doc.slug).split("-gocmaksan", 1)[0].split("-")
    if slug_parts:
        candidate = " ".join(part.upper() if re.search(r"\d", part) else part for part in slug_parts)
        values.append(candidate)
    expanded: list[str] = []
    for value in values:
        value = clean_text(value)
        if not value:
            continue
        expanded.append(value)
        expanded.append(value.upper())
        expanded.append(value.replace(" ", ""))
        expanded.append(value.replace("x", "X"))
        expanded.append(re.sub(r"\s+", " ", value.replace("-", " ")))
    seen: set[str] = set()
    result: list[str] = []
    for value in expanded:
        key = compact_model(value)
        if key and key not in seen:
            seen.add(key)
            result.append(value)
    return result


def contains_model(text: str, variants: list[str]) -> bool:
    compact = compact_model(text)
    for variant in variants:
        key = compact_model(variant)
        if key and key in compact:
            return True
    return False


def model_windows(lines: list[str], variants: list[str]) -> list[tuple[int, str]]:
    windows: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        if not contains_model(line, variants):
            continue
        start = max(0, index - 2)
        end = min(len(lines), index + 4)
        windows.append((index, " ".join(lines[start:end])))
    return windows


def score_model_window(text: str, variants: list[str]) -> int:
    score = 0
    if re.search(r"\d+\s*[x/]\s*\d+\s*[x/]\s*\d+", text):
        score += 5
    if "\u00d8" in text or "Ø" in text:
        score += 4
    if re.search(r"\b\d+(?:[,.]\d+)?\s+(?:380|220|50)\b", text):
        score += 2
    if re.search(r"\bmodel\b", text, flags=re.I):
        score -= 2
    if any(contains_model(text, [variant]) for variant in variants):
        score += 1
    return score


def best_model_window(lines: list[str], variants: list[str]) -> str:
    candidates = model_windows(lines, variants)
    if not candidates:
        return ""
    candidates.sort(key=lambda item: score_model_window(item[1], variants), reverse=True)
    return candidates[0][1]


def trim_before_model(text: str, variants: list[str]) -> str:
    best_pos: int | None = None
    best_len = 0
    for variant in variants:
        pattern = re.compile(re.escape(variant), flags=re.I)
        match = pattern.search(text)
        if match and (best_pos is None or match.start() < best_pos):
            best_pos = match.start()
            best_len = len(match.group(0))
    if best_pos is None:
        compact = compact_model(text)
        for variant in variants:
            key = compact_model(variant)
            pos = compact.find(key)
            if pos >= 0:
                return text
        return text
    return text[best_pos + best_len :].strip()


def parse_row_data(window: str, variants: list[str]) -> tuple[dict[str, str], list[str]]:
    row = trim_before_model(clean_text(window), variants)
    tech: dict[str, str] = {}
    capacities: list[str] = []

    dim_match = re.search(r"(\d+\s*[x/]\s*\d+\s*[x/]\s*\d+)", row)
    if dim_match:
        tech["W-L-H cm"] = normalize_dimension(dim_match.group(1))
        after_dim = row[dim_match.end() :]
        before_capacity = re.split(r"\u00d8|Ø", after_dim, maxsplit=1)[0]
        nums = re.findall(r"-|\d+(?:[,.]\d+)?(?:\s*/\s*\d+)?", before_capacity)
        nums = [normalize_number(num) for num in nums if num != "-"]
        if nums:
            if len(nums) >= 5 and re.search(r"Frequency|Frekans", window, flags=re.I):
                tech["Engine Power kW"] = nums[0]
                tech["Frequency Hz"] = nums[1]
                tech["Voltage V"] = nums[2]
                tech["Weight kg"] = nums[3]
                tech["Hydraulic Oil Tank Capacity lt"] = nums[4]
            elif len(nums) >= 4:
                tech["Engine Power kW"] = nums[0]
                tech["Voltage V"] = nums[1]
                tech["Weight kg"] = nums[2]
                tech["Hydraulic Oil Tank Capacity lt"] = nums[3]
            elif len(nums) >= 3:
                tech["Engine Power kW"] = nums[0]
                tech["Voltage V"] = nums[1]
                tech["Weight kg"] = nums[2]

    pairs = re.findall(r"(?:\u00d8|Ø)\s*\d+\s*x\s*\d+", row, flags=re.I)
    if pairs:
        normalized = [normalize_capacity_pair(pair) for pair in pairs]
    else:
        diameters = re.findall(r"(?:\u00d8|Ø)\s*\d+", row, flags=re.I)
        pieces = re.findall(r"x\s*\d+", row, flags=re.I)
        normalized = []
        if diameters and len(diameters) == len(pieces):
            for diameter, piece in zip(diameters, pieces):
                normalized.append(normalize_capacity_pair(f"{diameter} {piece}"))

    model_hint = compact_model(variants[0]) if variants else ""
    if model_hint.startswith(("hb", "mh")) and len(normalized) > 3:
        normalized = normalized[:3]

    if normalized:
        if len(normalized) >= 6:
            capacities = [
                f"{CAPACITY_LABELS[0]}: {normalized[0]}, {normalized[1]}",
                f"{CAPACITY_LABELS[1]}: {normalized[2]}, {normalized[3]}",
                f"{CAPACITY_LABELS[2]}: {normalized[4]}, {normalized[5]}",
            ]
        elif len(normalized) >= 3:
            capacities = [
                f"{CAPACITY_LABELS[0]}: {normalized[0]}",
                f"{CAPACITY_LABELS[1]}: {normalized[1]}",
                f"{CAPACITY_LABELS[2]}: {normalized[2]}",
            ]
        else:
            capacities = normalized

    return tech, capacities


def parse_key_value_technical(lines: list[str]) -> dict[str, str]:
    joined_lines = [clean_text(line) for line in lines if clean_text(line)]
    tech: dict[str, str] = {}
    for line in joined_lines:
        for key in sorted(TECHNICAL_PAIR_KEYS, key=len, reverse=True):
            if not line.lower().startswith(key.lower() + " "):
                continue
            value = line[len(key) :].strip()
            if value and value.lower() not in EMPTY_MARKERS:
                tech[key] = value
            break
    for index, line in enumerate(joined_lines):
        if line == "Machine Dimensions" and index + 1 < len(joined_lines):
            tech.setdefault("Machine Dimensions", joined_lines[index + 1])
        if line == "Bending Capacity":
            values = []
            for extra in joined_lines[max(0, index - 3) : index + 6]:
                if re.match(r"^\d+x\d+mm$", extra, flags=re.I):
                    values.append(extra)
            if values:
                tech.setdefault("Bending Capacity", " ".join(values))
    return tech


def parse_axis_capacities(lines: list[str]) -> list[str]:
    capacities: list[str] = []
    start = None
    for index, line in enumerate(lines):
        if "45 kg/mm" in line and "Piece" in line:
            start = index + 1
            break
    if start is None:
        return capacities
    for line in lines[start:]:
        if re.search(r"^(?:\u00d8|Ø)\s*\d+\s+\d+$", line) or re.search(r"^\d+\s*x\s*\d+\s+\d+$", line):
            bits = line.rsplit(" ", 1)
            capacities.append(f"{bits[0].strip()}: {bits[1].strip()}")
    return capacities


def parse_sls_capacities(lines: list[str]) -> list[str]:
    capacities: list[str] = []
    for index, line in enumerate(lines):
        if clean_text(line).lower() == "bending capacity":
            for extra in lines[max(0, index - 3) : index + 7]:
                item = clean_text(extra)
                if re.match(r"^\d+x\d+mm$", item, flags=re.I):
                    capacities.append(item)
            break
    return capacities


def translate_or_normalize_feature(item: str) -> str:
    item = clean_text(item).strip(" .")
    if not item:
        return ""
    key = ascii_key(item)
    if re.search(r"W\s*-\s*L\s*-\s*H|Motor Power|Weight|kg/mm|Diameter|TECHNICAL|SPECIFICATIONS", item, flags=re.I):
        return ""
    if "manuel ve otomatik kontrol opsiyonu" in key:
        return "Manual and automatic control option"
    if key in FEATURE_NORMALIZATION:
        return FEATURE_NORMALIZATION[key]
    if key in TURKISH_FEATURE_MAP:
        return TURKISH_FEATURE_MAP[key]
    if re.search(r"[\u0131\u0130\u015f\u015e\u011f\u011e\u00fc\u00dc\u00f6\u00d6\u00e7\u00c7]", item):
        return ""
    if re.search(r"\b\d+\s*$", item) and len(item) < 20:
        return ""
    if len(item) > 80 and not re.search(r"\b(system|option|control|capacity|hydraulic|mechanical|portable|easy|performance|bending|cutting|motor|design|panel|safety)\b", item, flags=re.I):
        return ""
    return item[0].upper() + item[1:] if item else ""


def extract_feature_candidates(lines: list[str]) -> list[str]:
    features: list[str] = []
    for line in lines:
        if "\u2022" in line:
            parts = [part.strip() for part in line.split("\u2022") if part.strip()]
            for part in parts:
                cleaned = re.sub(r"\b[A-Z]{1,3}\s*\d+[A-ZxX0-9]*\b.*$", "", part).strip()
                feature = translate_or_normalize_feature(cleaned)
                if feature:
                    features.append(feature)
        elif re.search(r"\b(Hydraulic|Mechanical System|Bending angles|Cut in|Easy to|Portable|Digital control|Pneumatic door|Foot pedal|emergency stop|ergonomic design)\b", line, flags=re.I):
            feature = translate_or_normalize_feature(line)
            if feature:
                features.append(feature)
    deduped: list[str] = []
    seen: set[str] = set()
    for feature in features:
        key = ascii_key(feature)
        if key and key not in seen:
            seen.add(key)
            deduped.append(feature)
    return deduped


def description_from_staging(doc: StagingDoc, raw: list[str], features: list[str], machine: dict[str, Any] | None) -> str:
    name = doc.en_name or (machine or {}).get("diller", {}).get("en", {}).get("name", "") or doc.slug
    prose: list[str] = []
    for index, line in enumerate(raw):
        item = clean_text(line)
        if len(item) < 60:
            continue
        if re.search(r"TECHNICAL|SPECIFICATIONS|CAPACTIES|www\.|info@|S I N C E|W\s*-\s*L\s*-\s*H|Motor Power|Weight|kg/mm|Diameter|Model", item, flags=re.I):
            continue
        if "\u00d8" in item or "Ø" in item:
            continue
        if re.search(r"\d+\s*[x/]\s*\d+\s*[x/]\s*\d+.*\b(?:220|380|50)\b", item):
            continue
        if re.search(r"[\u0131\u0130\u015f\u015e\u011f\u011e\u00fc\u00dc\u00f6\u00d6\u00e7\u00c7]", item):
            continue
        if not re.search(r"[.!?]$", item) and index + 1 < len(raw):
            next_item = clean_text(raw[index + 1])
            if next_item and not re.search(r"TECHNICAL|SPECIFICATIONS|www\.|info@|S I N C E", next_item, flags=re.I):
                item = clean_text(f"{item} {next_item}")
        prose.append(item)
    if prose:
        return prose[0]

    context = " ".join(title_items(doc) + raw[:12]).upper()
    for marker, template in DESCRIPTION_TEMPLATES.items():
        if marker in context:
            desc = template.format(name=name)
            if features:
                desc = desc.rstrip(".") + f", including {features[0].lower()}."
            return desc
    return ""


def parse_named_sections(doc: StagingDoc) -> tuple[dict[str, str], list[str], list[str]]:
    technical: dict[str, str] = {}
    features: list[str] = []
    capacities: list[str] = []

    technical_lines = section_items(doc, "detected technical tables")
    if technical_lines:
        technical = parse_key_value_technical(technical_lines)

    mixed_lines = section_items(doc, "capacities / apparatus / feature bullets")
    if mixed_lines:
        capacities = [line for line in mixed_lines if "\u00d8" in line or "Ø" in line or "kg/mm" in line]
        features = extract_feature_candidates(mixed_lines)
    return technical, features, capacities


def parse_raw_sections(doc: StagingDoc, machine: dict[str, Any] | None) -> tuple[dict[str, str], list[str], list[str], list[str]]:
    lines = raw_items(doc)
    variants = model_variants(doc, machine)
    notes: list[str] = []
    technical: dict[str, str] = {}
    capacities: list[str] = []

    if not lines:
        return technical, [], capacities, ["no raw text"]

    keyed = parse_key_value_technical(lines)
    if keyed:
        technical.update(keyed)

    if any((doc.en_name or "").upper().startswith(prefix) for prefix in ("SLS", "AXIS")):
        axis_caps = parse_axis_capacities(lines)
        if axis_caps:
            capacities = axis_caps
        sls_caps = parse_sls_capacities(lines)
        if sls_caps:
            capacities = sls_caps

    window = best_model_window(lines, variants)
    if window:
        row_tech, row_capacities = parse_row_data(window, variants)
        technical.update(row_tech)
        if row_capacities:
            capacities = row_capacities
    elif doc.metadata.get("recommendation") == "family-shared":
        notes.append("family-shared: model-specific row not found")

    features = extract_feature_candidates(lines)
    if doc.metadata.get("recommendation") == "family-shared" and features:
        notes.append("family-shared features")
    return technical, features, capacities, notes


def parse_staging(doc: StagingDoc, machine: dict[str, Any] | None) -> ParsedStaging:
    named_technical, named_features, named_capacities = parse_named_sections(doc)
    raw_technical, raw_features, raw_capacities, raw_notes = parse_raw_sections(doc, machine)

    technical = named_technical or raw_technical
    features = named_features or raw_features
    capacities = named_capacities or raw_capacities
    raw = raw_items(doc)
    description = description_from_staging(doc, raw, features, machine)

    parsed = ParsedStaging(
        slug=doc.slug,
        description=description,
        technical_data=technical,
        featured_features=features,
        capacities=capacities,
        notes=raw_notes,
    )
    if doc.metadata.get("source pdf", "").lower() == "none":
        parsed.notes.append("no PDF: existing JSON should be preserved")
    return parsed


def has_value(value: Any) -> bool:
    if isinstance(value, dict):
        return any(str(v).strip() for v in value.values())
    if isinstance(value, list):
        return any(str(v).strip() for v in value)
    if isinstance(value, str):
        return bool(value.strip())
    return bool(value)


def apply_parsed(machine: dict[str, Any], parsed: ParsedStaging) -> dict[str, Any]:
    updated = copy.deepcopy(machine)
    specs = updated.setdefault("specs", {})
    en = updated.setdefault("diller", {}).setdefault("en", {})

    if parsed.description and len(parsed.description) >= 60:
        en["description"] = parsed.description
    if has_value(parsed.technical_data):
        specs["TECHNICAL DATA"] = parsed.technical_data
    if has_value(parsed.featured_features):
        specs["FEATURED FEATURES"] = parsed.featured_features
    if has_value(parsed.capacities):
        specs["CAPACITIES"] = parsed.capacities
    return updated


def compact_for_diff(machine: dict[str, Any]) -> dict[str, Any]:
    return {
        "description": machine.get("diller", {}).get("en", {}).get("description", ""),
        "TECHNICAL DATA": machine.get("specs", {}).get("TECHNICAL DATA", {}),
        "FEATURED FEATURES": machine.get("specs", {}).get("FEATURED FEATURES", []),
        "CAPACITIES": machine.get("specs", {}).get("CAPACITIES", []),
    }


def diff_machine(before: dict[str, Any], after: dict[str, Any]) -> str:
    old = json.dumps(compact_for_diff(before), ensure_ascii=False, indent=2).splitlines()
    new = json.dumps(compact_for_diff(after), ensure_ascii=False, indent=2).splitlines()
    return "\n".join(difflib.unified_diff(old, new, fromfile="old", tofile="new", lineterm=""))


def load_data() -> list[dict[str, Any]]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def image_index_from_path(path: str) -> int:
    name = Path(path).stem
    match = re.search(r"_(\d+)$", name)
    return int(match.group(1)) if match else 0


def next_image_index(machine: dict[str, Any], base_slug: str) -> int:
    images = machine.get("diller", {}).get("en", {}).get("images", [])
    max_index = max([image_index_from_path(image) for image in images] or [0])
    for path in PUBLIC_IMAGE_DIR.glob(f"{base_slug}_*.*"):
        max_index = max(max_index, image_index_from_path(path.name))
    return max_index + 1


def existing_public_hashes() -> set[str]:
    hashes: set[str] = set()
    for path in PUBLIC_IMAGE_DIR.glob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            hashes.add(file_md5(path))
    return hashes


def unique_destination(base_slug: str, index: int, extension: str) -> tuple[Path, int]:
    while True:
        filename = f"{base_slug}_{index}{extension.lower()}"
        destination = PUBLIC_IMAGE_DIR / filename
        if not destination.exists():
            return destination, index
        index += 1


def merge_pdf_images(data: list[dict[str, Any]]) -> ImageMergeReport:
    PUBLIC_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    public_hashes = existing_public_hashes()
    report = ImageMergeReport()

    for machine in data:
        slug = machine["slug"]
        source_dir = PDF_IMAGE_DIR / slug
        if not source_dir.exists():
            report.missing_slug_dirs += 1
            continue

        en = machine.setdefault("diller", {}).setdefault("en", {})
        images = en.setdefault("images", [])
        machine_name = en.get("name") or slug
        base_slug = seo_slug(machine_name)
        next_index = next_image_index(machine, base_slug)

        for source in sorted(source_dir.iterdir()):
            if not source.is_file() or source.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            if source.stat().st_size < MIN_IMAGE_BYTES:
                report.size_skipped += 1
                continue
            digest = file_md5(source)
            if digest in public_hashes:
                report.duplicates_skipped += 1
                continue

            destination, used_index = unique_destination(base_slug, next_index, source.suffix)
            shutil.copy2(source, destination)
            public_hashes.add(digest)
            next_index = used_index + 1

            public_path = f"/images/gocmaksan/{destination.name}"
            if public_path not in images:
                images.append(public_path)
                report.appended_by_slug.setdefault(slug, []).append(public_path)
            report.added += 1

    return report


def build_image_report(data: list[dict[str, Any]], report: ImageMergeReport) -> str:
    image_counts = [
        len(machine.get("diller", {}).get("en", {}).get("images", []))
        for machine in data
    ]
    average = sum(image_counts) / len(image_counts) if image_counts else 0
    single_image_count = sum(1 for count in image_counts if count == 1)

    lines = [
        "",
        "=== Gocmaksan PDF image merge report ===",
        f"Toplam yeni resim eklenen: {report.added}",
        f"Duplicate atlanan: {report.duplicates_skipped}",
        f"Boyut filtresi ile atlanan: {report.size_skipped}",
        f"Makine başına ortalama resim sayısı: {average:.2f}",
        f"Hala tek resimli makine sayısı: {single_image_count}",
        f"Image source dir bulunmayan slug: {report.missing_slug_dirs}",
        "",
        "Yeni resim eklenen sluglar:",
    ]
    if report.appended_by_slug:
        for slug, paths in sorted(report.appended_by_slug.items()):
            lines.append(f"- {slug}: {len(paths)}")
    else:
        lines.append("- none")
    return "\n".join(lines)


def build_report(original: list[dict[str, Any]], updated: list[dict[str, Any]], parsed_by_slug: dict[str, ParsedStaging], examples: list[str]) -> str:
    report_lines: list[str] = []
    changed_by_slug = {machine["slug"]: machine for machine in updated}

    desc_count = 0
    technical_count = 0
    features_count = 0
    capacities_count = 0
    empty_slugs: list[str] = []
    note_lines: list[str] = []

    for machine in original:
        slug = machine["slug"]
        parsed = parsed_by_slug.get(slug)
        if not parsed:
            empty_slugs.append(slug)
            continue
        if has_value(parsed.description):
            desc_count += 1
        if has_value(parsed.technical_data):
            technical_count += 1
        if has_value(parsed.featured_features):
            features_count += 1
        if has_value(parsed.capacities):
            capacities_count += 1
        if not any(
            [
                has_value(parsed.description),
                has_value(parsed.technical_data),
                has_value(parsed.featured_features),
                has_value(parsed.capacities),
            ]
        ):
            empty_slugs.append(slug)
        if parsed.notes:
            note_lines.append(f"- {slug}: {'; '.join(parsed.notes)}")

    report_lines.append("=== Gocmaksan PDF staging dry-run ===")
    report_lines.append(f"Staging markdown count: {len(parsed_by_slug)}")
    report_lines.append(f"JSON machine count: {len(original)}")
    report_lines.append(f"description filled from staging: {desc_count}/47")
    report_lines.append(f"TECHNICAL DATA filled from staging: {technical_count}/47")
    report_lines.append(f"FEATURED FEATURES filled from staging: {features_count}/47")
    report_lines.append(f"CAPACITIES filled from staging: {capacities_count}/47")
    report_lines.append("")
    report_lines.append("Still empty from staging:")
    if empty_slugs:
        report_lines.extend(f"- {slug}" for slug in empty_slugs)
    else:
        report_lines.append("- none")
    report_lines.append("")
    report_lines.append("Parser notes:")
    report_lines.extend(note_lines[:40] if note_lines else ["- none"])
    if len(note_lines) > 40:
        report_lines.append(f"- ... {len(note_lines) - 40} more notes")
    report_lines.append("")
    report_lines.append("Example diffs:")
    for slug in examples:
        before = next((machine for machine in original if machine["slug"] == slug), None)
        after = changed_by_slug.get(slug)
        if not before or not after:
            continue
        report_lines.append(f"--- {slug} ---")
        machine_diff = diff_machine(before, after)
        report_lines.append(machine_diff if machine_diff else "(no change)")
    return "\n".join(report_lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Merge Gocmaksan PDF staging markdown into gocmaksan.json.")
    parser.add_argument("--dry-run", action="store_true", help="Print report without writing JSON.")
    parser.add_argument("--merge-images", action="store_true", help="Append non-duplicate PDF extraction images to product galleries.")
    args = parser.parse_args()

    data = load_data()
    machines_by_slug = {machine["slug"]: machine for machine in data}
    parsed_by_slug: dict[str, ParsedStaging] = {}
    updated = copy.deepcopy(data)

    for path in sorted(STAGING_DIR.glob("*.md")):
        doc = parse_markdown(path)
        machine = machines_by_slug.get(doc.slug)
        parsed_by_slug[doc.slug] = parse_staging(doc, machine)

    for index, machine in enumerate(updated):
        parsed = parsed_by_slug.get(machine["slug"])
        if parsed:
            updated[index] = apply_parsed(machine, parsed)

    examples = [
        "gms-b-45x1-gocmaksan-insaat-demiri-bukme-makinasi",
        "gms-hb-12x6-gocmaksan-hasir-demir-bukme-makinasi",
        "gms-sls-12-gocmaksan-otomatik-etriye-bukme-makinasi",
    ]
    print(build_report(data, updated, parsed_by_slug, examples))

    image_report: ImageMergeReport | None = None
    if args.merge_images and not args.dry_run:
        image_report = merge_pdf_images(updated)
        print(build_image_report(updated, image_report))

    if not args.dry_run:
        DATA_PATH.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"\nWrote {DATA_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
