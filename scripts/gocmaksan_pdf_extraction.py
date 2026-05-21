from __future__ import annotations

import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import fitz
import pdfplumber


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "src" / "data" / "gocmaksan.json"
CATALOG_DIR = PROJECT_ROOT / "public" / "catalogs" / "gocmaksan"
OUTPUT_ROOT = PROJECT_ROOT / "pdf_extraction"
GOC_ROOT = OUTPUT_ROOT / "gocmaksan"
YILMAZ_ROOT = OUTPUT_ROOT / "yilmaz"

GOC_TEXT_DIR = GOC_ROOT / "text"
GOC_IMAGE_DIR = GOC_ROOT / "images"
GOC_MANIFEST_DIR = GOC_ROOT / "manifests"
YILMAZ_TEXT_DIR = YILMAZ_ROOT / "text"
YILMAZ_IMAGE_DIR = YILMAZ_ROOT / "images"
YILMAZ_MANIFEST_DIR = YILMAZ_ROOT / "manifests"

SECTION_ALIASES = {
    "FEATURED FEATURES": "featured_features",
    "FEATURES": "featured_features",
    "GENERAL FEATURES": "general_features",
    "TECHNICAL DATA": "technical_data",
    "TECHNICAL SPECIFICATIONS": "technical_data",
    "SPECIFICATIONS": "technical_data",
    "CAPACITIES": "capacities",
    "CUTTING CAPACITIES": "capacities",
    "BENDING CAPACITIES": "capacities",
    "APPARATUS SUPPLIED WITH THE MACHINE": "apparatus",
    "STANDARD ACCESSORIES": "apparatus",
    "OPTIONAL ACCESSORIES": "apparatus",
}
SECTION_ORDER = [
    "featured_features",
    "general_features",
    "technical_data",
    "capacities",
    "apparatus",
]


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def slug_to_tokens(slug: str) -> set[str]:
    tokens = set(re.findall(r"[a-z0-9]+", slug.lower()))
    return {t for t in tokens if t not in {"gocmaksan", "gms", "makinasi", "makinalari", "eng"}}


def md5sum(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_dirs() -> None:
    for path in [
        GOC_TEXT_DIR,
        GOC_IMAGE_DIR,
        GOC_MANIFEST_DIR,
        YILMAZ_TEXT_DIR,
        YILMAZ_IMAGE_DIR,
        YILMAZ_MANIFEST_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def touch_gitkeep(path: Path) -> None:
    file = path / ".gitkeep"
    if not file.exists():
        file.write_text("", encoding="utf-8")


def reset_output_area() -> None:
    for child in GOC_TEXT_DIR.glob("*.md"):
        child.unlink()
    for child in GOC_MANIFEST_DIR.glob("*"):
        if child.is_file():
            child.unlink()
    for child in GOC_IMAGE_DIR.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    for path in [YILMAZ_TEXT_DIR, YILMAZ_IMAGE_DIR, YILMAZ_MANIFEST_DIR]:
        for child in path.iterdir():
            if child.is_file() and child.name != ".gitkeep":
                child.unlink()
            elif child.is_dir():
                shutil.rmtree(child)
    for path in [YILMAZ_TEXT_DIR, YILMAZ_IMAGE_DIR, YILMAZ_MANIFEST_DIR]:
        touch_gitkeep(path)


def load_machines() -> list[dict[str, Any]]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


@dataclass
class ParsedPdf:
    title_candidates: list[str]
    preface_lines: list[str]
    sections: dict[str, list[str]]
    detected_headings: list[str]
    template_note: str
    image_entries: list[dict[str, Any]]


def extract_title_candidates(lines: list[str]) -> list[str]:
    candidates: list[str] = []
    for line in lines[:15]:
        if len(line) < 4 or len(line) > 120:
            continue
        if line not in candidates:
            candidates.append(line)
        if len(candidates) == 6:
            break
    return candidates


def detect_heading(line: str) -> str | None:
    upper = clean_text(line).upper()
    if upper in SECTION_ALIASES:
        return SECTION_ALIASES[upper]
    return None


def parse_pdf_text(pdf_path: Path) -> tuple[list[str], dict[str, list[str]], list[str]]:
    lines: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for raw in text.splitlines():
                line = clean_text(raw)
                if line:
                    lines.append(line)

    sections = {key: [] for key in SECTION_ORDER}
    preface: list[str] = []
    headings_seen: list[str] = []
    current: str | None = None

    for line in lines:
        heading = detect_heading(line)
        if heading:
            current = heading
            headings_seen.append(line)
            continue
        if current is None:
            preface.append(line)
        else:
            sections[current].append(line)

    return preface, sections, headings_seen


def classify_template(headings: list[str], sections: dict[str, list[str]], preface: list[str]) -> str:
    upper_headings = {clean_text(x).upper() for x in headings}
    if "FEATURED FEATURES" in upper_headings:
        return "classic-featured"
    if sections["featured_features"] and not upper_headings:
        return "feature-stack-no-heading"
    if preface and not sections["featured_features"]:
        return "preface-before-sections"
    return "unknown"


def extract_images(pdf_path: Path) -> list[dict[str, Any]]:
    doc = fitz.open(pdf_path)
    images: list[dict[str, Any]] = []
    fallback_needed = True

    try:
        for page_index in range(doc.page_count):
            page = doc.load_page(page_index)
            page_images = page.get_images(full=True)
            local_found = 0
            for image_index, info in enumerate(page_images, start=1):
                xref = info[0]
                extracted = doc.extract_image(xref)
                image_bytes = extracted.get("image", b"")
                ext = extracted.get("ext", "png")
                if len(image_bytes) < 1024:
                    continue
                local_found += 1
                fallback_needed = False
                images.append(
                    {
                        "page": page_index + 1,
                        "image_index": image_index,
                        "ext": ext,
                        "bytes": image_bytes,
                        "mode": "embedded",
                    }
                )
            if local_found == 0:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                rendered = pix.tobytes("png")
                if len(rendered) >= 1024:
                    images.append(
                        {
                            "page": page_index + 1,
                            "image_index": 1,
                            "ext": "png",
                            "bytes": rendered,
                            "mode": "rendered-page",
                        }
                    )
        return images
    finally:
        doc.close()


def parse_family_pdf(pdf_path: Path) -> ParsedPdf:
    preface, sections, headings = parse_pdf_text(pdf_path)
    title_candidates = extract_title_candidates(preface or sum(sections.values(), []))
    template_note = classify_template(headings, sections, preface)
    image_entries = extract_images(pdf_path)
    return ParsedPdf(
        title_candidates=title_candidates,
        preface_lines=preface[:120],
        sections={k: v[:240] for k, v in sections.items()},
        detected_headings=headings,
        template_note=template_note,
        image_entries=image_entries,
    )


def resolve_local_pdf(machine: dict[str, Any]) -> Path | None:
    pdf_catalog = machine.get("pdf_catalog") or ""
    if pdf_catalog:
        mapped = PROJECT_ROOT / "public" / pdf_catalog.lstrip("/")
        if mapped.exists():
            return mapped

    slug_pdf = CATALOG_DIR / f"{machine['slug']}.pdf"
    if slug_pdf.exists():
        return slug_pdf
    return None


def build_family_groups(machines: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    families: dict[str, dict[str, Any]] = {}
    missing_slugs: list[str] = []
    for machine in machines:
        slug = machine["slug"]
        local_pdf = resolve_local_pdf(machine)
        if not local_pdf:
            missing_slugs.append(slug)
            continue
        family_hash = md5sum(local_pdf)
        entry = families.setdefault(
            family_hash,
            {
                "family_hash": family_hash,
                "local_pdf": local_pdf,
                "source_pdfs": [],
                "slugs": [],
                "machine_names": [],
            },
        )
        entry["source_pdfs"].append(local_pdf.name)
        entry["slugs"].append(slug)
        name = machine.get("diller", {}).get("en", {}).get("name") or slug
        entry["machine_names"].append(name)
    for entry in families.values():
        entry["source_pdfs"] = sorted(set(entry["source_pdfs"]))
        entry["slugs"] = sorted(entry["slugs"])
        entry["machine_names"] = sorted(set(entry["machine_names"]))
    return families, sorted(missing_slugs)


def write_machine_markdown(
    slug: str,
    family: dict[str, Any] | None,
    parsed: ParsedPdf | None,
    machine: dict[str, Any],
    missing_reason: str | None = None,
) -> None:
    out = GOC_TEXT_DIR / f"{slug}.md"
    lines: list[str] = [f"# {slug}", ""]

    if not family or not parsed:
        lines += [
            f"- source PDF: none",
            f"- family hash: none",
            f"- recommendation: unresolved",
            "",
            "## ambiguity notes",
            f"- {missing_reason or 'No local PDF mapped for this slug.'}",
        ]
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    family_shared = len(family["slugs"]) > 1
    recommendation = "family-shared" if family_shared else "machine-specific"
    ambiguity_notes: list[str] = []
    if family_shared:
        ambiguity_notes.append(
            f"Shared PDF family covers {len(family['slugs'])} slugs: {', '.join(family['slugs'])}."
        )
    slug_tokens = slug_to_tokens(slug)
    joined_preface = " ".join(parsed.preface_lines).lower()
    if slug_tokens and not any(token in joined_preface for token in slug_tokens):
        ambiguity_notes.append("Slug tokens are not clearly stated in intro text; do not treat text as unique description.")
        if recommendation == "machine-specific":
            recommendation = "unresolved"
    if not parsed.preface_lines:
        ambiguity_notes.append("No free-form preface text found before recognized PDF sections.")
    if any(img["mode"] == "rendered-page" for img in parsed.image_entries):
        ambiguity_notes.append("At least one page image came from full-page render fallback.")

    lines += [
        f"- source PDF: `{family['local_pdf'].name}`",
        f"- family hash: `{family['family_hash']}`",
        f"- shared family: `{'yes' if family_shared else 'no'}`",
        f"- template note: `{parsed.template_note}`",
        f"- recommendation: `{recommendation}`",
        "",
        "## title candidates",
    ]
    lines += [f"- {item}" for item in parsed.title_candidates] or ["- (none)"]
    lines += ["", "## raw intro/body text"]
    lines += [f"- {item}" for item in parsed.preface_lines] or ["- (none)"]
    lines += ["", "## detected technical tables"]
    lines += [f"- {item}" for item in parsed.sections["technical_data"]] or ["- (none)"]
    lines += ["", "## capacities / apparatus / feature bullets"]
    merged = (
        parsed.sections["featured_features"]
        + parsed.sections["general_features"]
        + parsed.sections["capacities"]
        + parsed.sections["apparatus"]
    )
    lines += [f"- {item}" for item in merged] or ["- (none)"]
    lines += ["", "## ambiguity notes"]
    lines += [f"- {item}" for item in ambiguity_notes] or ["- none"]
    lines += ["", "## machine context"]
    lines += [f"- en name: {machine.get('diller', {}).get('en', {}).get('name') or '(empty)'}"]
    lines += [f"- categories: {', '.join(machine.get('categories') or []) or '(empty)'}"]
    lines += [f"- subcategory: {machine.get('subcategory') or '(empty)'}"]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_images_for_slug(slug: str, parsed: ParsedPdf | None) -> int:
    target = GOC_IMAGE_DIR / slug
    target.mkdir(parents=True, exist_ok=True)
    if not parsed:
        return 0
    saved = 0
    for entry in parsed.image_entries:
        filename = f"{slug}_catalog_page-{entry['page']:02d}_img-{entry['image_index']:02d}.png"
        out = target / filename
        out.write_bytes(entry["bytes"])
        if out.stat().st_size > 0:
            saved += 1
    return saved


def write_family_manifests(families: dict[str, dict[str, Any]], parsed_map: dict[str, ParsedPdf]) -> None:
    summary_lines = [
        "# Gocmaksan PDF Families",
        "",
        f"- total local PDF files: {len(list(CATALOG_DIR.glob('*.pdf')))}",
        f"- unique family PDFs: {len(families)}",
        "",
    ]
    for index, (family_hash, family) in enumerate(sorted(families.items()), start=1):
        parsed = parsed_map[family_hash]
        short_hash = family_hash[:12]
        payload = {
            "family_id": short_hash,
            "family_hash": family_hash,
            "source_pdfs": family["source_pdfs"],
            "linked_slugs": family["slugs"],
            "machine_names": family["machine_names"],
            "template_note": parsed.template_note,
            "detected_headings": parsed.detected_headings,
            "extraction_status": {
                "text": "ok",
                "images": "ok" if parsed.image_entries else "empty",
                "markdown_slugs": len(family["slugs"]),
            },
        }
        (GOC_MANIFEST_DIR / f"family_{short_hash}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        summary_lines += [
            f"## Family {index} `{short_hash}`",
            f"- source PDFs: {', '.join(family['source_pdfs'])}",
            f"- linked slugs: {', '.join(family['slugs'])}",
            f"- template note: {parsed.template_note}",
            f"- extraction status: text=ok, images={'ok' if parsed.image_entries else 'empty'}",
            "",
        ]
    (GOC_MANIFEST_DIR / "families_index.md").write_text("\n".join(summary_lines), encoding="utf-8")


def write_missing_pdfs(missing_slugs: list[str], machines: list[dict[str, Any]]) -> None:
    by_slug = {m["slug"]: m for m in machines}
    lines = [
        "# Missing Gocmaksan PDFs",
        "",
        f"- missing count: {len(missing_slugs)}",
        "",
    ]
    for slug in missing_slugs:
        machine = by_slug[slug]
        lines += [
            f"## {slug}",
            f"- en name: {machine.get('diller', {}).get('en', {}).get('name') or '(empty)'}",
            f"- categories: {', '.join(machine.get('categories') or []) or '(empty)'}",
            f"- subcategory: {machine.get('subcategory') or '(empty)'}",
            "- next step: check product page for direct PDF link only",
            "",
        ]
    (GOC_MANIFEST_DIR / "missing_pdfs.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    reset_output_area()
    machines = load_machines()
    families, missing_slugs = build_family_groups(machines)
    parsed_map: dict[str, ParsedPdf] = {}

    for family_hash, family in sorted(families.items()):
        parsed_map[family_hash] = parse_family_pdf(family["local_pdf"])

    by_slug = {m["slug"]: m for m in machines}
    saved_image_counts: dict[str, int] = {}

    for family_hash, family in families.items():
        parsed = parsed_map[family_hash]
        for slug in family["slugs"]:
            write_machine_markdown(slug, family, parsed, by_slug[slug])
            saved_image_counts[slug] = write_images_for_slug(slug, parsed)

    for slug in missing_slugs:
        write_machine_markdown(
            slug,
            family=None,
            parsed=None,
            machine=by_slug[slug],
            missing_reason="No local PDF available; web PDF lookup deferred to later phase.",
        )
        (GOC_IMAGE_DIR / slug).mkdir(parents=True, exist_ok=True)
        saved_image_counts[slug] = 0

    write_family_manifests(families, parsed_map)
    write_missing_pdfs(missing_slugs, machines)

    summary = {
        "machines_total": len(machines),
        "local_pdf_files": len(list(CATALOG_DIR.glob('*.pdf'))),
        "family_pdfs": len(families),
        "missing_pdfs": len(missing_slugs),
        "markdown_files": len(list(GOC_TEXT_DIR.glob('*.md'))),
        "image_dirs": len([p for p in GOC_IMAGE_DIR.iterdir() if p.is_dir()]),
        "image_files": sum(len(list(p.glob('*.png'))) for p in GOC_IMAGE_DIR.iterdir() if p.is_dir()),
    }
    (GOC_MANIFEST_DIR / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
