#!/usr/bin/env python3
"""
tools/inject_yilmaz_from_yedek.py

Inject from yilmaz_yedek.json into individual Yilmaz machine JSON files:
  - diller.ru : FULL inject for all 88 machines (name, description, specs, technical_data)
  - diller.en.description : inject only where current is empty or < MIN_DESC_CHARS

KAYNAK : C:/Users/Kenan/Desktop/AI/_ARSIV_Jaguar-ltd_20260515/src/data/yilmaz_yedek.json
HEDEF  : src/data/machines/yilmaz/<slug>.json

Modes:
  --dry-run  (default) : build + validate + 3 samples + report, no writes
  --apply              : backup + write atomically + report

YASAKLAR: diller.bg'ye dokunma, resimler/katalog inject etme, git commit/push.
"""

import argparse, json, re, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT    = Path(__file__).resolve().parent.parent
YEDEK_PATH   = Path(r"C:\Users\Kenan\Desktop\AI\_ARSIV_Jaguar-ltd_20260515\src\data\yilmaz_yedek.json")
YILMAZ_DIR   = REPO_ROOT / "src" / "data" / "machines" / "yilmaz"
REPORT_PATH  = REPO_ROOT / "INJECT_YEDEK_REPORT_2026-05-23.md"
MIN_DESC_CHARS = 100

# ── piktogramlar TR key --> technical_data EN key ─────────────────────────────
PIKTOGRAM_KEY_MAP = {
    "elektrik"          : "Power",
    "matkap_donus_hizi" : "Drill Rotation Speed",
    "donus_hizi"        : "Saw Rotation Speed",
    "cap"               : "Saw Diameter",
    "debi"              : "Flow Rate",
    "basinc"            : "Pressure",
    "boyutlar"          : "Dimensions (cm)",
    "urun_agirligi"     : "Weight",
    # additional common keys found in yilmaz machines
    "kesme_hizi"        : "Cutting Speed",
    "motor_gucu"        : "Motor Power",
    "devir"             : "Rotation Speed",
    "voltaj"            : "Voltage",
    "frekans"           : "Frequency",
    "hava_tuketimi"     : "Air Consumption",
    "kesim_acisi"       : "Cutting Angle",
    "min_kesim_acisi"   : "Min Cutting Angle",
    "max_kesim_acisi"   : "Max Cutting Angle",
    "is_uzunlugu"       : "Working Length",
    "kapasite"          : "Capacity",
    "pnomatik_basinc"   : "Pneumatic Pressure",
    "kesim_kapasitesi"  : "Cutting Capacity",
    "mil_hizi"          : "Spindle Speed",
    "tabla_boyutu"      : "Table Dimensions",
    "min_profil_boyu"   : "Min Profile Length",
    "max_profil_boyu"   : "Max Profile Length",
    "step_motor"        : "Step Motor",
    "kesici_sayisi"     : "Number of Cutters",
    "kaynak_gucu"       : "Welding Power",
    "sicaklik"          : "Temperature",
    "piston_kuvveti"    : "Piston Force",
    "profil_genisligi"  : "Profile Width",
    "profil_yuksekligi" : "Profile Height",
    "freze_alani"       : "Milling Area",
    "kose_pres"         : "Corner Press Force",
    "profil"            : "Profile",
}

# ── EN ozellik_gruplari key normalization (typo fix in yedek) ─────────────────
EN_SPEC_KEY_MAP = {
    "STANDART ACCESORIES" : "STANDARD ACCESSORIES",
    "STANDART ACCESSORIES": "STANDARD ACCESSORIES",
    "OPTIONAL ACCESORIES" : "OPTIONAL ACCESSORIES",
    "OPTIONAL ACCESSORIES": "OPTIONAL ACCESSORIES",
    "GENERAL FEATURES"    : "GENERAL FEATURES",
    "STANDARD ACCESORIES" : "STANDARD ACCESSORIES",
    "STANDARD ACCESSORIES": "STANDARD ACCESSORIES",
}

# ── RU ozellik_gruplari key normalization (Karar B: full Cyrillic) ─────────────
RU_SPEC_KEY_MAP = {
    "STANDARTNI AKSESOARI"       : "СТАНДАРТНЫЕ АКСЕССУАРЫ",   # BG leak
    "СТАНДАРТНЫЕ АКСЕССУАРЫ"     : "СТАНДАРТНЫЕ АКСЕССУАРЫ",
    "ДОПОЛНИТЕЛЬНЫЕ АКСЕССУАРЫ"  : "ДОПОЛНИТЕЛЬНЫЕ АКСЕССУАРЫ",
    "GENERAL FEATURES"           : "ОБЩИЕ ХАРАКТЕРИСТИКИ",
    "ОБЩИЕ ХАРАКТЕРИСТИКИ"       : "ОБЩИЕ ХАРАКТЕРИСТИКИ",
    "STANDARD ACCESSORIES"       : "СТАНДАРТНЫЕ АКСЕССУАРЫ",
    "STANDART ACCESORIES"        : "СТАНДАРТНЫЕ АКСЕССУАРЫ",
    "OPTIONAL ACCESSORIES"       : "ДОПОЛНИТЕЛЬНЫЕ АКСЕССУАРЫ",
    "OPTIONAL ACCESORIES"        : "ДОПОЛНИТЕЛЬНЫЕ АКСЕССУАРЫ",
}

# Expected RU spec key order
RU_SPEC_KEYS_ORDERED = [
    "СТАНДАРТНЫЕ АКСЕССУАРЫ",
    "ДОПОЛНИТЕЛЬНЫЕ АКСЕССУАРЫ",
    "ОБЩИЕ ХАРАКТЕРИСТИКИ",
]


# ── Slug / model-code matching ────────────────────────────────────────────────

def model_code(slug: str) -> str:
    """
    Extract base model code from slug.
    'aim-7510-aluminyum-...' -> 'aim-7510'
    'ack-420-s-alttan-...'  -> 'ack-420'
    'kd-350-p-...'          -> 'kd-350'
    """
    parts = slug.lower().split("-")
    for i, p in enumerate(parts):
        if any(c.isdigit() for c in p):
            return "-".join(parts[: i + 1])
    return "-".join(parts[:2]) if len(parts) >= 2 else parts[0]


def model_variant(slug: str):
    """
    Return (base_code, variant_suffix) for disambiguation.
    'kd-350-p-miter-saw'     -> ('kd-350', 'p')
    'aim-7510-aluminium-...' -> ('aim-7510', '')
    """
    parts = slug.lower().split("-")
    for i, p in enumerate(parts):
        if any(c.isdigit() for c in p):
            base = "-".join(parts[: i + 1])
            nxt  = parts[i + 1] if i + 1 < len(parts) else ""
            variant = nxt if (nxt and len(nxt) <= 3 and nxt.isalpha()) else ""
            return base, variant
    return "-".join(parts[:2]), ""


def build_yedek_index(yedek_list: list):
    """
    Build two lookup dicts from yedek list:
      by_cv  : {(code, variant) : machine}
      by_code: {code : [machine, ...]}
    """
    by_cv   = {}
    by_code = defaultdict(list)
    for m in yedek_list:
        code, variant = model_variant(m["slug"])
        by_cv[(code, variant)] = m   # last wins for duplicates
        by_code[code].append(m)
    return by_cv, dict(by_code)


def find_yedek(current_slug: str, by_cv: dict, by_code: dict):
    """
    Returns (yedek_machine | None, match_type).
    match_type: 'exact' | 'code-variant' | 'code-only' | 'ambiguous' | 'no-match'
    """
    code, variant = model_variant(current_slug)

    if (code, variant) in by_cv:
        return by_cv[(code, variant)], "exact"

    if (code, "") in by_cv:
        return by_cv[(code, "")], "code-only"

    candidates = by_code.get(code, [])
    if len(candidates) == 1:
        return candidates[0], "code-only"
    if len(candidates) > 1:
        return candidates[0], "ambiguous"

    return None, "no-match"


# ── Data extraction helpers ───────────────────────────────────────────────────

def extract_og_items(val) -> list:
    """Extract item list from an ozellik_gruplari group value."""
    if isinstance(val, list):
        return [str(v) for v in val]
    if isinstance(val, dict):
        for v in val.values():
            if isinstance(v, list):
                return [str(i) for i in v]
        return [str(v) for v in val.values() if v]
    return []


def build_specs(og_dict: dict, key_map: dict) -> dict:
    """Convert ozellik_gruplari to specs dict with normalized keys."""
    if not og_dict:
        return {}
    result = {}
    for k, v in og_dict.items():
        normalized = key_map.get(k, k)
        result[normalized] = extract_og_items(v)
    return result


def build_technical_data(pik_dict) -> dict:
    """Convert piktogramlar {tr_key: value} to {en_key: value}."""
    if not pik_dict or not isinstance(pik_dict, dict):
        return {}
    result = {}
    for k, v in pik_dict.items():
        en_key = PIKTOGRAM_KEY_MAP.get(k, k)   # unknown keys pass through as-is
        result[en_key] = str(v) if v is not None else ""
    return result


def build_ru_diller(yedek_m: dict) -> dict:
    """Build complete diller.ru object from a yedek machine."""
    ru = (yedek_m.get("diller") or {}).get("ru") or {}
    en = (yedek_m.get("diller") or {}).get("en") or {}   # piktogramlar source

    isim     = (ru.get("isim") or "").strip()
    aciklama = (ru.get("aciklama") or "").strip()
    og       = ru.get("ozellik_gruplari") or {}
    # piktogramlar values are language-neutral; prefer EN source, fallback RU
    pik = en.get("piktogramlar") or ru.get("piktogramlar") or {}

    specs = build_specs(og, RU_SPEC_KEY_MAP)
    # Ensure ordered output with standard RU keys
    ordered_specs = {}
    for k in RU_SPEC_KEYS_ORDERED:
        if k in specs:
            ordered_specs[k] = specs[k]
    # append any extra keys not in ordered list
    for k, v in specs.items():
        if k not in ordered_specs:
            ordered_specs[k] = v

    tech = build_technical_data(pik)

    result = {
        "name"        : isim,
        "description" : aciklama,
        "specs"       : ordered_specs,
    }
    if tech:
        result["technical_data"] = tech
    return result


def get_en_aciklama(yedek_m: dict) -> str:
    """Return EN aciklama from yedek machine."""
    en = (yedek_m.get("diller") or {}).get("en") or {}
    return (en.get("aciklama") or "").strip()


# ── Machine / file helpers ────────────────────────────────────────────────────

def detect_le(raw: bytes) -> str:
    return "\r\n" if b"\r\n" in raw else "\n"


def has_trailing_nl(raw: bytes) -> bool:
    return raw.endswith(b"\n")


def alloc_bak(path: Path):
    for suffix in [".bak"] + [f".bak.{i}" for i in range(2, 6)]:
        cand = Path(str(path) + suffix)
        if not cand.exists():
            return cand
    return None


def to_bytes(data: dict, le: str, trailing: bool) -> bytes:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if le == "\r\n":
        text = text.replace("\n", "\r\n")
    text = text.rstrip("\r\n")
    if trailing:
        text += le
    return text.encode("utf-8")


def inject_ru_and_en(machine: dict, new_ru: dict, new_en_desc: str | None) -> dict:
    """
    Build modified machine dict:
    - Replace/insert diller.ru with new_ru
    - If new_en_desc is not None, update diller.en.description
    - diller.bg and all other fields: UNTOUCHED
    """
    old_diller = dict(machine.get("diller") or {})

    # Preserve field order, update en if needed
    new_diller = {}
    for k, v in old_diller.items():
        if k == "en" and new_en_desc is not None:
            en_copy = dict(v) if isinstance(v, dict) else {}
            en_copy["description"] = new_en_desc
            new_diller["en"] = en_copy
        elif k == "ru":
            new_diller["ru"] = new_ru   # replace existing (shouldn't exist, but defensive)
        else:
            new_diller[k] = v

    # Insert ru after en if not already placed
    if "ru" not in new_diller:
        rebuilt = {}
        placed  = False
        for k, v in new_diller.items():
            rebuilt[k] = v
            if k == "en" and not placed:
                rebuilt["ru"] = new_ru
                placed = True
        if not placed:
            rebuilt["ru"] = new_ru
        new_diller = rebuilt

    result = {}
    for k, v in machine.items():
        result[k] = new_diller if k == "diller" else v
    return result


# ── Validation ────────────────────────────────────────────────────────────────

def validate_ru(ru: dict) -> list:
    """Return list of validation errors. Empty = OK."""
    errs = []
    if not isinstance(ru.get("name"), str):
        errs.append("ru.name not str")
    if not isinstance(ru.get("description"), str):
        errs.append("ru.description not str")
    specs = ru.get("specs")
    if not isinstance(specs, dict):
        errs.append("ru.specs not dict")
    return errs


# ── Report writer ─────────────────────────────────────────────────────────────

def write_report(
    mode: str,
    results: list,
    sample_outputs: list,
    unknown_pik_keys: dict,
    spec_rename_count: int,
    elapsed: float,
):
    ts    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = len(results)

    ru_ok        = [r for r in results if r["status"] in ("written", "would-write") and r["ru_injected"]]
    en_partial   = [r for r in results if r["en_desc_injected"]]
    mismatches   = [r for r in results if r["match_type"] == "no-match"]
    ambiguous    = [r for r in results if r["match_type"] == "ambiguous"]
    errors       = [r for r in results if r["status"] == "error"]
    yedek_only   = [r for r in results if r.get("yedek_only")]

    L = []
    L.append("# Yedek Inject Raporu")
    L.append("")
    L.append(f"**Tarih:** {ts}  ")
    L.append(f"**Mod:** `{mode}`  ")
    L.append(f"**Kaynak:** `yilmaz_yedek.json` (90 makine)  ")
    L.append(f"**Hedef:** `src/data/machines/yilmaz/` (88 makine)  ")
    L.append(f"**Süre:** {elapsed:.1f}s")
    L.append("")
    L.append("## Özet")
    L.append("")
    L.append("| Metrik | Değer |")
    L.append("|---|---|")
    L.append(f"| Hedef makine | {total} |")
    L.append(f"| RU inject {'yapılacak' if mode=='dry-run' else 'yapıldı'} | **{len(ru_ok)}** |")
    L.append(f"| EN description inject {'yapılacak' if mode=='dry-run' else 'yapıldı'} | **{len(en_partial)}** |")
    L.append(f"| Mismatch (yedekte yok) | {len(mismatches)} |")
    L.append(f"| Ambiguous match | {len(ambiguous)} |")
    L.append(f"| Hata | {len(errors)} |")
    L.append(f"| Spec key rename ('STANDART ACCESORIES' vb.) | {spec_rename_count} dosyada |")
    if mode == "apply":
        written = sum(1 for r in results if r["status"] == "written")
        L.append(f"| Yazılan dosya | **{written}** |")
        L.append(f"| Backup (.bak) | {written} |")
        if len(errors) == 0:
            L.append("| **DURUM** | ✅ **TAMAMLANDI** |")
        else:
            L.append(f"| **DURUM** | ⚠️ **{len(errors)} hata ile tamamlandı** |")
    else:
        L.append("| **DURUM** | ℹ️ **DRY-RUN — dosya yazılmadı** |")

    # ── Samples ───────────────────────────────────────────────────────────────
    if sample_outputs:
        L.append("")
        L.append("## Örnek Çıktılar (Dry-run Samples)")
        for s in sample_outputs:
            L.append("")
            L.append(f"### `{s['slug']}` — {s['label']}")
            L.append("")
            L.append("```json")
            L.append(json.dumps(s["output"], ensure_ascii=False, indent=2))
            L.append("```")

    # ── EN partial inject list ────────────────────────────────────────────────
    if en_partial:
        L.append("")
        L.append("## EN Description Inject Listesi (Partial Makineler)")
        L.append("")
        L.append("| Slug | Önce (chr) | Sonra (chr) | Kaynak |")
        L.append("|---|---|---|---|")
        for r in en_partial:
            L.append(
                f"| `{r['slug']}` | {r['en_desc_before']} chr "
                f"| {r['en_desc_after']} chr | yedek EN aciklama |"
            )

    # ── Spec key rename summary ───────────────────────────────────────────────
    L.append("")
    L.append("## Spec Key Rename Özeti")
    L.append("")
    L.append("| Yedek key | → | Normalize edilen key | Adet |")
    L.append("|---|---|---|---|")
    L.append("| `STANDART ACCESORIES` | → | `STANDARD ACCESSORIES` | (bkz. sayı yukarıda) |")
    L.append("| `OPTIONAL ACCESORIES` | → | `OPTIONAL ACCESSORIES` | |")
    L.append("| RU `GENERAL FEATURES` | → | `ОБЩИЕ ХАРАКТЕРИСТИКИ` | (Karar B) |")

    # ── Technical_data rename summary ─────────────────────────────────────────
    L.append("")
    L.append("## Technical_data Key Dönüşümü (piktogramlar → technical_data)")
    L.append("")
    L.append("| TR key (yedek) | → | EN key (inject) |")
    L.append("|---|---|---|")
    for tr, en in PIKTOGRAM_KEY_MAP.items():
        L.append(f"| `{tr}` | → | `{en}` |")
    if unknown_pik_keys:
        L.append("")
        L.append("**Bilinmeyen piktogram key'leri (as-is bırakıldı):**")
        for k, slugs in sorted(unknown_pik_keys.items()):
            L.append(f"- `{k}` — {len(slugs)} makinede: {', '.join(slugs[:5])}")

    # ── Mismatch ──────────────────────────────────────────────────────────────
    if mismatches:
        L.append("")
        L.append("## Mismatch — Yedekte Karşılığı Olmayan Current Makineler")
        L.append("")
        for r in mismatches:
            L.append(f"- `{r['slug']}` (model_code=`{r['model_code']}`)")
        L.append("")
        L.append("> Bu makineler için RU inject yapılamaz. Gemini RU çevirisi gerekiyor.")

    if ambiguous:
        L.append("")
        L.append("## Ambiguous Match (İlk Aday Seçildi)")
        L.append("")
        L.append("| Current slug | Seçilen yedek slug |")
        L.append("|---|---|")
        for r in ambiguous:
            L.append(f"| `{r['slug']}` | `{r['yedek_slug']}` |")

    # ── Yedek-only ────────────────────────────────────────────────────────────
    if yedek_only:
        L.append("")
        L.append("## Yedek-only (Current'ta Yok — Ignore Edildi)")
        L.append("")
        for slug in yedek_only:
            L.append(f"- `{slug}`")

    # ── Full detay tablosu ────────────────────────────────────────────────────
    L.append("")
    L.append("## Makine Detay Tablosu")
    L.append("")
    status_order = {"error": 0, "no-match": 1, "written": 2, "would-write": 3}
    L.append("| # | Slug | Match | RU | EN partial | Bytes | Not |")
    L.append("|---|---|---|---|---|---|---|")
    for i, r in enumerate(
        sorted(results, key=lambda x: (status_order.get(x["status"], 9), x["slug"])), 1
    ):
        ru_tag  = "✅" if r["ru_injected"] else "—"
        en_tag  = f"+{r['en_desc_after'] - r['en_desc_before']}chr" if r["en_desc_injected"] else "—"
        bytes_s = f"{r['bytes_before']}→{r['bytes_after']}" if r["bytes_after"] else str(r["bytes_before"])
        L.append(
            f"| {i} | `{r['slug']}` | {r['match_type']} "
            f"| {ru_tag} | {en_tag} | {bytes_s} | {r['msg']} |"
        )

    L.append("")
    L.append("---")
    L.append(f"*Generated by `tools/inject_yilmaz_from_yedek.py` — {ts}*")
    L.append("")
    REPORT_PATH.write_text("\n".join(L), encoding="utf-8")
    print(f"[inject_yilmaz] Rapor -> {REPORT_PATH.name}")


# ── Ana akış ──────────────────────────────────────────────────────────────────

def run(mode: str) -> int:
    import time
    t_start = time.time()
    print(f"[inject_yilmaz] === mode={mode} ===")

    # 1. Load yedek
    print(f"[inject_yilmaz] Yedek yukleniyor: {YEDEK_PATH.name}")
    with open(YEDEK_PATH, encoding="utf-8") as f:
        yedek_list = json.load(f)
    by_cv, by_code = build_yedek_index(yedek_list)
    yedek_slugs = {m["slug"] for m in yedek_list}
    print(f"[inject_yilmaz] Yedek: {len(yedek_list)} makine, {len(by_code)} unique model kodu")

    # 2. Load current files
    current_files = []
    for fpath in sorted(YILMAZ_DIR.glob("*.json")):
        if ".bak" in fpath.name:
            continue
        raw = fpath.read_bytes()
        try:
            machine = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as e:
            print(f"[inject_yilmaz] SKIP (JSON error): {fpath.name} — {e}", file=sys.stderr)
            continue
        current_files.append((fpath, raw, machine))

    print(f"[inject_yilmaz] Current: {len(current_files)} makine")

    # Track yedek-only slugs
    current_codes = {model_code(fpath.stem) for fpath, _, _ in current_files}
    yedek_only = [
        m["slug"] for m in yedek_list
        if model_code(m["slug"]) not in current_codes
    ]

    # 3. Build phase: compute all modifications in memory
    results         = []
    sample_outputs  = []
    sample_ru_done  = False
    sample_en_done  = False
    sample_edge_done = False
    unknown_pik_keys: dict = defaultdict(list)   # key -> [slugs]
    spec_rename_count = 0

    builds = []   # (fpath, raw, new_machine, result_record)

    for fpath, raw, machine in current_files:
        slug = machine.get("slug") or fpath.stem
        cur_en = (machine.get("diller") or {}).get("en") or {}
        cur_en_desc = (cur_en.get("description") or "").strip()
        mc = model_code(slug)

        rec = {
            "slug"           : slug,
            "model_code"     : mc,
            "status"         : "pending",
            "match_type"     : "",
            "yedek_slug"     : "",
            "ru_injected"    : False,
            "en_desc_injected": False,
            "en_desc_before" : len(cur_en_desc),
            "en_desc_after"  : len(cur_en_desc),
            "bytes_before"   : len(raw),
            "bytes_after"    : 0,
            "msg"            : "",
        }

        # Find yedek match
        yedek_m, match_type = find_yedek(slug, by_cv, by_code)
        rec["match_type"] = match_type
        if yedek_m:
            rec["yedek_slug"] = yedek_m["slug"]

        if match_type == "no-match" or yedek_m is None:
            rec["status"] = "no-match"
            rec["msg"]    = "yedekte yok"
            results.append(rec)
            builds.append((fpath, raw, machine, rec, None, None))
            continue

        # Build RU diller
        new_ru = build_ru_diller(yedek_m)

        # Track unknown piktogramlar keys
        en_pik = (yedek_m.get("diller") or {}).get("en") or {}
        ru_pik = (yedek_m.get("diller") or {}).get("ru") or {}
        for pik_dict in [en_pik.get("piktogramlar"), ru_pik.get("piktogramlar")]:
            if pik_dict and isinstance(pik_dict, dict):
                for k in pik_dict:
                    if k not in PIKTOGRAM_KEY_MAP:
                        unknown_pik_keys[k].append(slug)

        # Track spec key renames
        yedek_en_og = ((yedek_m.get("diller") or {}).get("en") or {}).get("ozellik_gruplari") or {}
        had_rename = any(k in ("STANDART ACCESORIES", "OPTIONAL ACCESORIES", "STANDART ACCESSORIES")
                        for k in yedek_en_og)
        if had_rename:
            spec_rename_count += 1

        # Validate RU
        errs = validate_ru(new_ru)
        if errs:
            rec["status"] = "error"
            rec["msg"]    = "RU validate: " + "; ".join(errs)
            results.append(rec)
            builds.append((fpath, raw, machine, rec, None, None))
            continue

        rec["ru_injected"] = True

        # EN description: inject only if current < MIN_DESC_CHARS
        new_en_desc = None
        if len(cur_en_desc) < MIN_DESC_CHARS:
            yedek_en_aciklama = get_en_aciklama(yedek_m)
            if yedek_en_aciklama and len(yedek_en_aciklama) >= MIN_DESC_CHARS:
                new_en_desc = yedek_en_aciklama
                rec["en_desc_injected"] = True
                rec["en_desc_after"]    = len(new_en_desc)

        # Build modified machine (in memory only at this stage)
        new_machine = inject_ru_and_en(machine, new_ru, new_en_desc)

        # Determine status
        rec["status"] = "would-write" if mode == "dry-run" else "pending-write"

        # Compute projected byte size
        le  = detect_le(raw)
        tnl = has_trailing_nl(raw)
        new_raw = to_bytes(new_machine, le, tnl)
        rec["bytes_after"] = len(new_raw)

        if mode == "dry-run":
            rec["msg"] = f"ru={len(new_ru['description'])}chr desc | en_partial={'yes' if new_en_desc else 'no'}"

        # Sample collection for dry-run
        if mode == "dry-run":
            if not sample_ru_done and new_ru.get("description") and not new_en_desc:
                sample_outputs.append({
                    "slug"  : slug,
                    "label" : "RU full inject (description dolu)",
                    "output": {"diller.ru": new_ru},
                })
                sample_ru_done = True
            elif not sample_en_done and new_en_desc:
                sample_outputs.append({
                    "slug"  : slug,
                    "label" : "EN partial description inject",
                    "output": {
                        "diller.en.description (new)": new_en_desc[:300] + "..." if len(new_en_desc) > 300 else new_en_desc,
                        "diller.ru": new_ru,
                    },
                })
                sample_en_done = True
            elif not sample_edge_done and match_type == "ambiguous":
                sample_outputs.append({
                    "slug"  : slug,
                    "label" : f"Edge case — ambiguous match (yedek: {yedek_m['slug']})",
                    "output": {"diller.ru.name": new_ru.get("name"), "diller.ru.specs_keys": list(new_ru.get("specs", {}).keys())},
                })
                sample_edge_done = True

        results.append(rec)
        builds.append((fpath, raw, new_machine, rec, le, tnl))

    # Fallback: edge sample from any ambiguous, or just show specs of 3rd machine
    if mode == "dry-run" and len(sample_outputs) < 3:
        for fpath, raw, new_machine, rec, le, tnl in builds:
            if new_machine is not None and rec["ru_injected"] and len(sample_outputs) < 3:
                ru = (new_machine.get("diller") or {}).get("ru") or {}
                if ru and not any(s["slug"] == rec["slug"] for s in sample_outputs):
                    sample_outputs.append({
                        "slug"  : rec["slug"],
                        "label" : f"Ek sample ({rec['match_type']})",
                        "output": {"diller.ru.name": ru.get("name"),
                                   "diller.ru.description_len": len(ru.get("description", "")),
                                   "diller.ru.specs_keys": list(ru.get("specs", {}).keys()),
                                   "diller.ru.technical_data": ru.get("technical_data")},
                    })

    print(f"[inject_yilmaz] Build phase: {sum(1 for r in results if r['ru_injected'])} RU ready, "
          f"{sum(1 for r in results if r['en_desc_injected'])} EN partial ready, "
          f"{sum(1 for r in results if r['status'] == 'no-match')} no-match, "
          f"{sum(1 for r in results if r['status'] == 'error')} error")

    # 4. Write phase (apply only) — atomic: backups first, then writes
    if mode == "apply":
        backup_map = {}  # fpath -> bak_path

        # Allocate all backups first
        ok_builds = [(fp, raw, nm, rec, le, tnl) for fp, raw, nm, rec, le, tnl in builds
                     if rec["status"] == "pending-write"]

        for fpath, raw, new_machine, rec, le, tnl in ok_builds:
            bak = alloc_bak(fpath)
            if bak is None:
                rec["status"] = "error"
                rec["msg"]    = "backup slots exhausted"
                continue
            backup_map[fpath] = bak

        # Write backups
        for fpath, raw, new_machine, rec, le, tnl in ok_builds:
            if fpath not in backup_map:
                continue
            backup_map[fpath].write_bytes(raw)

        # Write modified files
        written = 0
        for fpath, raw, new_machine, rec, le, tnl in ok_builds:
            if fpath not in backup_map:
                continue
            try:
                new_raw = to_bytes(new_machine, le, tnl)
                fpath.write_bytes(new_raw)
                rec["status"]      = "written"
                rec["bytes_after"] = len(new_raw)
                rec["msg"]         = f"bak={backup_map[fpath].name}"
                written += 1
                print(f"[inject_yilmaz]   WRITTEN {fpath.name}  "
                      f"{rec['bytes_before']}→{rec['bytes_after']} bytes")
            except Exception as e:
                rec["status"] = "error"
                rec["msg"]    = f"write error: {e}"

        print(f"[inject_yilmaz] Apply done: {written} written")

    elapsed = time.time() - t_start
    print(f"[inject_yilmaz] elapsed={elapsed:.1f}s")

    # Attach yedek_only to results for report
    for r in results:
        r["yedek_only"] = False

    write_report(mode, results, sample_outputs, dict(unknown_pik_keys),
                 spec_rename_count, elapsed)

    err_count = sum(1 for r in results if r["status"] == "error")
    return 1 if err_count > 0 else 0


def main():
    parser = argparse.ArgumentParser(
        description="Inject RU (+ EN partial desc) from yilmaz_yedek into individual JSON files."
    )
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument("--dry-run", action="store_true",
                     help="Build + report + 3 samples, no file writes (default)")
    grp.add_argument("--apply", action="store_true",
                     help="Backup + write atomically + report")
    args = parser.parse_args()
    mode = "apply" if args.apply else "dry-run"
    sys.exit(run(mode))


if __name__ == "__main__":
    main()
