#!/usr/bin/env python3
"""
tools/translate_yilmaz_bg.py

Translate Yilmaz machine pages from English -> Bulgarian (BG) via Gemini.
Targets only machines where diller.bg is missing or name/description is empty.

KAYNAK : src/data/machines/yilmaz/<slug>.json  diller.en fields
HEDEF  : ayni dosya -- diller.bg inject (name, description, specs)
API    : Gemini REST  gemini-2.5-flash  response_mime_type=application/json

Phase 1 ile zaten doldurulan makineler otomatik atlanir (BG.name/description dolu).

Siniflandirma:
  translate-full    : EN description >= min_chars -> tam ceviri
  translate-partial : EN desc < min_chars AMA (name var VEYA specs dolu) -> name+specs cevir, desc=""
  skip-empty        : EN name bos VE desc < min_chars VE specs tamamen bos -> atla

Kullanim:
    python tools/translate_yilmaz_bg.py              # dry-run (varsayilan)
    python tools/translate_yilmaz_bg.py --dry-run    # ilk 3 makineyi cevir, dosya yazma
    python tools/translate_yilmaz_bg.py --apply      # tumunu cevir, backup + yaz
    python tools/translate_yilmaz_bg.py --apply --min-chars 50

Gereksinimler:
    pip install requests
    GEMINI_API_KEY  ->  .env dosyasi (repo root) veya ortam degiskeni
"""

import argparse
import json
import os
import sys
import time
import urllib3
from datetime import datetime
from pathlib import Path

import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -- Sabitler ------------------------------------------------------------------
REPO_ROOT   = Path(__file__).resolve().parent.parent
YILMAZ_DIR  = REPO_ROOT / "src" / "data" / "machines" / "yilmaz"
REPORT_PATH = REPO_ROOT / "TRANSLATE_YILMAZ_BG_REPORT_2026-05-23.md"

MODEL_NAME = "gemini-2.5-flash"

GEMINI_URL = (
    "https://generativelanguage.googleapis.com"
    f"/v1beta/models/{MODEL_NAME}:generateContent?key={{key}}"
)
RATE_LIMIT_SECS   = 4
DRY_RUN_SAMPLE    = 3
DEFAULT_MIN_CHARS = 100
GLOSSARY_MAX      = 8

# BG specs key eslemesi  (EN canonical -> BG Kiril)
SPECS_MAP = {
    "STANDARD ACCESSORIES" : "STANDARTNI AKSESOARI",   # placeholder -- replaced below
    "OPTIONAL ACCESSORIES" : "OPTSIONALNI AKSESOARI",
    "GENERAL FEATURES"     : "OBSHTI HARAKTERISTIKI",
}
# Kiril degerleri (JSON icin dogrudan kullan)
SPECS_MAP = {
    "STANDARD ACCESSORIES" : "СТАНДАРТНИ АКСЕСОАРИ",
    "OPTIONAL ACCESSORIES" : "ОПЦИОНАЛНИ АКСЕСОАРИ",
    "GENERAL FEATURES"     : "ОБЩИ ХАРАКТЕРИСТИКИ",
}
BG_SPECS_KEYS = list(SPECS_MAP.values())   # СТАНДАРТНИ АКСЕСОАРИ, ОПЦИОНАЛНИ АКСЕСОАРИ, ОБЩИ ХАРАКТЕРИСТИКИ

# -- .env yukleyici ------------------------------------------------------------
_env = REPO_ROOT / ".env"
if _env.exists():
    for _line in _env.read_text(encoding="utf-8").splitlines():
        if _line.startswith("GEMINI_API_KEY="):
            os.environ.setdefault("GEMINI_API_KEY", _line.split("=", 1)[1].strip())

# -- Sabit terminoloji blogugu -------------------------------------------------
TERMINOLOGY_BLOCK = (
    "YILMAZ BG TERMINOLOGY (use these EXACT translations):\n"
    '- "up-cutting saw machine" -> "ОТРЕЗНА МАШИНА С ДОЛНО ПОДАВАНЕ"\n'
    '- "miter saw machine" / "mitre saw machine" -> "ОТРЕЗНА МАШИНА С ЪГЛОВА НАСТРОЙКА"\n'
    '- "double head" -> "ДВУГЛАВА"\n'
    '- "single head" -> "ЕДНОГЛАВА"\n'
    '- "machining center" / "processing center" -> "ЦЕНТЪР ЗА ОБРАБОТКА"\n'
    '- "copy router" -> "КОПИРНА ФРЕЗА"\n'
    '- "corner cleaning machine" -> "МАШИНА ЗА ПОЧИСТВАНЕ НА ЪГЛИ"\n'
    '- "corner crimping machine" -> "МАШИНА ЗА ЗАГЛАЖДАНЕ НА ЪГЛИ"\n'
    '- "welding machine" -> "МАШИНА ЗА ЗАВАРЯВАНЕ"\n'
    '- "end milling machine" -> "МАШИНА ЗА ТОРЦОВО ФРЕЗОВАНЕ"\n'
    '- "automatic" -> "АВТОМАТИЧНА"\n'
    '- "semi-automatic" -> "ПОЛУАВТОМАТИЧНА"\n'
    '- "manual" -> "РЪЧНА"\n'
    "\n"
    "CRITICAL RULE - MODEL CODES STAY LATIN:\n"
    "Model codes (AIM, ACK, DC, KD, CPM, CRM, CNC, FR, GAS, MCA, MK, MKN, NSM, PIM, PWB, PYE, RS, RYK, "
    "SCM, SDT, SK, SKN, SM, ST, TK, VCE, VK, WGM, CCL, CA, DKN, HDL, HP, GPT, GT, PC, PT, RT, VP, WAS, "
    "WB, KP, KY, CDC, CK, DK, NCR, SNM) MUST remain in LATIN alphabet - NEVER transliterate to Cyrillic.\n"
    "\n"
    "Examples:\n"
    'CORRECT:   "AIM 3410 - CENTRE ZA OBRABOTKA NA ALUMINIIEVI PROFILI"\n'
    'INCORRECT: "AIM 3410 - ..." with Cyrillic A-I-M\n'
    'CORRECT:   "ACK 550 - OTREZNA MASHINA S DOLNO PODAVANE"\n'
    "INCORRECT: Cyrillic transliteration of ACK\n"
    "\n"
    "This rule applies in name AND description AND every specs item."
)

# -- Prompt template: FULL (has description) -----------------------------------
PROMPT_TEMPLATE_FULL = """\
{terminology_block}

REFERENCE TRANSLATIONS (existing site BG, match this style exactly):
{glossary_examples}

---
Translate this Yilmaz machine product page from English to Bulgarian.
Output STRICT JSON, no markdown fences, this exact shape:
{{
  "name": "<machine model in UPPERCASE Bulgarian Cyrillic, keep model codes/numbers as-is>",
  "description": "<full Bulgarian paragraph, preserve technical accuracy>",
  "specs": {{
    "СТАНДАРТНИ АКСЕСОАРИ": ["<item 1 in Bulgarian>", "<item 2>", ...],
    "ОПЦИОНАЛНИ АКСЕСОАРИ": ["<item 1>", ...],
    "ОБЩИ ХАРАКТЕРИСТИКИ":  ["<item 1>", ...]
  }}
}}

Rules:
- Keep technical terms (CNC, PVC, kW, RPM, mm, bar, Hz, VAC, etc.) and model codes as-is
- Translate every list item separately, preserve count and order exactly
- If a specs key is missing or empty in source, output it as empty array []
- name MUST be UPPERCASE Cyrillic (model numbers/codes stay in LATIN)
- Output only the JSON object, nothing else

EN SOURCE:
NAME: {en_name}
DESCRIPTION: {en_description}
STANDARD ACCESSORIES: {standard_accessories}
OPTIONAL ACCESSORIES: {optional_accessories}
GENERAL FEATURES: {general_features}
"""

# -- Prompt template: PARTIAL (no description, only name + specs) --------------
PROMPT_TEMPLATE_PARTIAL = """\
{terminology_block}

REFERENCE TRANSLATIONS (existing site BG, match this style exactly):
{glossary_examples}

---
Translate this Yilmaz machine product page from English to Bulgarian.
IMPORTANT: This machine has NO English description available. You MUST set "description" to empty string "".
Output STRICT JSON, no markdown fences, this exact shape:
{{
  "name": "<machine model in UPPERCASE Bulgarian Cyrillic, keep model codes/numbers as-is>",
  "description": "",
  "specs": {{
    "СТАНДАРТНИ АКСЕСОАРИ": ["<item 1 in Bulgarian>", "<item 2>", ...],
    "ОПЦИОНАЛНИ АКСЕСОАРИ": ["<item 1>", ...],
    "ОБЩИ ХАРАКТЕРИСТИКИ":  ["<item 1>", ...]
  }}
}}

Rules:
- Keep technical terms (CNC, PVC, kW, RPM, mm, bar, Hz, VAC, etc.) and model codes as-is
- Translate every list item separately, preserve count and order exactly
- If a specs key is missing or empty in source, output it as empty array []
- name MUST be UPPERCASE Cyrillic (model numbers/codes stay in LATIN)
- description MUST be empty string "" -- do NOT invent a description
- Output only the JSON object, nothing else

EN SOURCE:
NAME: {en_name}
STANDARD ACCESSORIES: {standard_accessories}
OPTIONAL ACCESSORIES: {optional_accessories}
GENERAL FEATURES: {general_features}
"""


# -- Yardimci fonksiyonlar -----------------------------------------------------

def load_env_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        print(
            "ERROR: GEMINI_API_KEY bulunamadi.\n"
            "  .env dosyasina GEMINI_API_KEY=... ekleyin.",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


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


def is_bg_missing(machine: dict) -> bool:
    bg   = (machine.get("diller") or {}).get("bg") or {}
    name = (bg.get("name") or "").strip()
    desc = (bg.get("description") or "").strip()
    return not name or not desc


def has_specs_content(en_specs: dict) -> bool:
    """True if at least one spec key has non-empty list."""
    for v in en_specs.values():
        if isinstance(v, list) and len(v) > 0:
            return True
    return False


def classify_target(machine: dict, min_chars: int) -> str:
    """
    Returns one of:
      'translate-full'    -- EN description >= min_chars
      'translate-partial' -- desc < min_chars BUT (name exists OR specs dolu)
      'skip-empty'        -- EN name bos VE desc < min_chars VE specs tamamen bos
    """
    en      = (machine.get("diller") or {}).get("en") or {}
    en_name = (en.get("name") or "").strip()
    en_desc = (en.get("description") or "").strip()
    en_specs = en.get("specs") or {}

    if len(en_desc) >= min_chars:
        return "translate-full"

    # desc yetersiz -- name veya specs kontrolu
    if en_name or has_specs_content(en_specs):
        return "translate-partial"

    return "skip-empty"


def build_glossary(max_examples: int = GLOSSARY_MAX) -> str:
    examples = []
    for fpath in sorted(YILMAZ_DIR.glob("*.json")):
        if ".bak" in fpath.name:
            continue
        try:
            machine = json.loads(fpath.read_bytes().decode("utf-8"))
        except Exception:
            continue
        diller  = machine.get("diller") or {}
        en_name = ((diller.get("en") or {}).get("name") or "").strip()
        bg_name = ((diller.get("bg") or {}).get("name") or "").strip()
        if en_name and bg_name:
            examples.append((en_name, bg_name))
        if len(examples) >= max_examples:
            break
    if not examples:
        return "(no reference translations available yet)"
    lines = []
    for en, bg in examples:
        lines.append(f'EN: "{en}"')
        lines.append(f'BG: "{bg}"')
    return "\n".join(lines)


def build_prompt(machine: dict, glossary_str: str, partial: bool) -> str:
    en       = (machine.get("diller") or {}).get("en") or {}
    en_specs = en.get("specs") or {}

    std  = json.dumps(en_specs.get("STANDARD ACCESSORIES") or [], ensure_ascii=False)
    opt  = json.dumps(en_specs.get("OPTIONAL ACCESSORIES") or [], ensure_ascii=False)
    feat = json.dumps(en_specs.get("GENERAL FEATURES") or [], ensure_ascii=False)

    if partial:
        return PROMPT_TEMPLATE_PARTIAL.format(
            terminology_block    = TERMINOLOGY_BLOCK,
            glossary_examples    = glossary_str,
            en_name              = (en.get("name") or "").strip(),
            standard_accessories = std,
            optional_accessories = opt,
            general_features     = feat,
        )
    else:
        return PROMPT_TEMPLATE_FULL.format(
            terminology_block    = TERMINOLOGY_BLOCK,
            glossary_examples    = glossary_str,
            en_name              = (en.get("name") or "").strip(),
            en_description       = (en.get("description") or "").strip(),
            standard_accessories = std,
            optional_accessories = opt,
            general_features     = feat,
        )


def call_gemini(prompt: str, api_key: str) -> dict:
    url     = GEMINI_URL.format(key=api_key)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "response_mime_type": "application/json",
        },
    }
    resp = requests.post(url, json=payload, timeout=90, verify=False)
    body = resp.json()

    if "error" in body:
        raise RuntimeError(f"Gemini API error: {body['error'].get('message', body['error'])}")
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")

    raw_text = body["candidates"][0]["content"]["parts"][0]["text"].strip()
    if raw_text.startswith("```"):
        lines    = raw_text.splitlines()
        raw_text = "\n".join(l for l in lines if not l.startswith("```")).strip()

    return json.loads(raw_text)


def validate_response(data: dict, partial: bool = False) -> list:
    errs = []
    if not isinstance(data.get("name"), str) or not data["name"].strip():
        errs.append("name bos veya string degil")
    desc = data.get("description")
    if not isinstance(desc, str):
        errs.append("description string degil")
    elif not partial and not desc.strip():
        errs.append("description bos (full modda izin verilmez)")
    specs = data.get("specs")
    if not isinstance(specs, dict):
        errs.append("specs dict degil")
        return errs
    for k in BG_SPECS_KEYS:
        if k not in specs:
            errs.append(f"specs missing key: {k!r}")
        elif not isinstance(specs[k], list):
            errs.append(f"specs[{k!r}] list degil")
    return errs


def inject_bg(machine: dict, new_bg: dict) -> dict:
    old_diller = dict(machine.get("diller") or {})
    new_diller: dict = {}
    placed = False
    for key, val in old_diller.items():
        if key == "bg":
            new_diller["bg"] = new_bg
            placed = True
        else:
            new_diller[key] = val
            if key == "en" and not placed and "bg" not in old_diller:
                new_diller["bg"] = new_bg
                placed = True
    if not placed:
        new_diller["bg"] = new_bg
    result = {}
    for k, v in machine.items():
        result[k] = new_diller if k == "diller" else v
    return result


def to_bytes(data: dict, le: str, trailing: bool) -> bytes:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if le == "\r\n":
        text = text.replace("\n", "\r\n")
    text = text.rstrip("\r\n")
    if trailing:
        text += le
    return text.encode("utf-8")


# -- Rapor yardimcisi ----------------------------------------------------------

def write_report(
    mode: str,
    targets: list,
    api_calls: int,
    elapsed: float,
    sample_outputs: list,
    glossary_count: int,
):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Sayimlar
    skip_empty_c       = sum(1 for r in targets if r["status"] == "skip-empty")
    err_c              = sum(1 for r in targets if r["status"] == "error")
    written_full_c     = sum(1 for r in targets if r["status"] == "written-full")
    written_partial_c  = sum(1 for r in targets if r["status"] == "written-partial")
    wt_full_c          = sum(1 for r in targets if r["status"] == "would-translate-full")
    wt_partial_c       = sum(1 for r in targets if r["status"] == "would-translate-partial")
    sample_full_c      = sum(1 for r in targets if r["status"] == "sample-full")
    sample_partial_c   = sum(1 for r in targets if r["status"] == "sample-partial")
    total              = len(targets)

    L = []
    L.append("# Yilmaz BG Taze Tercume Raporu")
    L.append("")
    L.append(f"**Tarih:** {ts}  ")
    L.append(f"**Mod:** `{mode}`  ")
    L.append(f"**Model:** `{MODEL_NAME}`  ")
    L.append(f"**Rate limit:** {RATE_LIMIT_SECS}s / call  ")
    L.append(f"**Glossary ornekleri:** {glossary_count} adet")
    L.append("")
    L.append("## Ozet")
    L.append("")
    L.append("| Metrik | Deger |")
    L.append("|---|---|")
    L.append(f"| Tespit edilen hedef | {total} |")
    L.append(f"| API call sayisi | {api_calls} |")
    L.append(f"| Toplam sure | {elapsed:.1f}s |")
    if mode == "dry-run":
        L.append(f"| Sample full ({DRY_RUN_SAMPLE} max) | {sample_full_c} |")
        L.append(f"| Sample partial ({DRY_RUN_SAMPLE} max) | {sample_partial_c} |")
        L.append(f"| Would-translate-full | {wt_full_c} |")
        L.append(f"| Would-translate-partial | {wt_partial_c} |")
    else:
        L.append(f"| Yazilan (full) | {written_full_c} |")
        L.append(f"| Yazilan (partial) | {written_partial_c} |")
        L.append(f"| Hatali | {err_c} |")
    L.append(f"| skip-empty (icerik yok) | {skip_empty_c} |")
    if mode == "apply":
        total_written = written_full_c + written_partial_c
        if err_c == 0:
            L.append(f"| **DURUM** | OK **TAMAMLANDI ({total_written} yazildi)** |")
        else:
            L.append(f"| **DURUM** | WARN **{total_written} yazildi, {err_c} hata** |")
    else:
        L.append("| **DURUM** | INFO **DRY-RUN -- dosya yazilmadi** |")

    if mode == "dry-run" and sample_outputs:
        L.append("")
        L.append("## Ornek Ceviriler (Ilk 3 -- Kalite Kontrolu)")
        for s in sample_outputs:
            tag = "(PARTIAL)" if s.get("partial") else "(FULL)"
            L.append("")
            L.append(f"### `{s['slug']}` {tag}")
            L.append("")
            L.append("```json")
            L.append(json.dumps(s["output"], ensure_ascii=False, indent=2))
            L.append("```")

    L.append("")
    L.append("## Makine Detay Tablosu")
    L.append("")
    prio = {
        "error": 0, "skip-empty": 1,
        "sample-partial": 2, "sample-full": 3,
        "would-translate-partial": 4, "would-translate-full": 5,
        "written-partial": 2, "written-full": 3,
    }
    if mode == "apply":
        L.append("| # | Slug | Sonuc | Bytes Once->Sonra | Not |")
        L.append("|---|---|---|---|---|")
        for i, r in enumerate(
            sorted(targets, key=lambda x: (prio.get(x["status"], 9), x["slug"])), 1
        ):
            ba = f"{r['bytes_before']} -> {r['bytes_after']}" if r["bytes_after"] else str(r["bytes_before"])
            L.append(f"| {i} | `{r['slug']}` | **{r['status']}** | {ba} | {r['msg']} |")
    else:
        L.append("| # | Slug | Sinif | Sonuc | EN desc | Not |")
        L.append("|---|---|---|---|---|---|")
        for i, r in enumerate(
            sorted(targets, key=lambda x: (prio.get(x["status"], 9), x["slug"])), 1
        ):
            L.append(
                f"| {i} | `{r['slug']}` | {r['classification']} | **{r['status']}** "
                f"| {r.get('en_desc_len', '--')} | {r['msg']} |"
            )

    L.append("")
    L.append("---")
    L.append(f"*Generated by `tools/translate_yilmaz_bg.py` -- {ts}*")
    L.append("")

    REPORT_PATH.write_text("\n".join(L), encoding="utf-8")
    print(f"[translate_yilmaz_bg] Rapor -> {REPORT_PATH.name}")


# -- Ana akis ------------------------------------------------------------------

def run(mode: str, min_chars: int) -> int:
    print(f"[translate_yilmaz_bg] === mode={mode} | min_chars={min_chars} ===")
    api_key = load_env_key()
    t_start = time.time()
    api_calls = 0

    # 0. Glossary
    glossary_str   = build_glossary(GLOSSARY_MAX)
    glossary_count = glossary_str.count('EN: "')
    print(f"[translate_yilmaz_bg] Glossary: {glossary_count} ornek yuklendi")

    # 1. BG eksik makineleri tara + siniflandir
    all_files = sorted(YILMAZ_DIR.glob("*.json"))
    targets   = []

    for fpath in all_files:
        if fpath.suffix != ".json" or ".bak" in fpath.name:
            continue
        raw = fpath.read_bytes()
        try:
            machine = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            continue

        slug = machine.get("slug") or fpath.stem
        if not is_bg_missing(machine):
            continue

        en      = (machine.get("diller") or {}).get("en") or {}
        en_desc = (en.get("description") or "").strip()
        cls     = classify_target(machine, min_chars)

        targets.append({
            "slug"          : slug,
            "path"          : fpath,
            "raw"           : raw,
            "machine"       : machine,
            "en_desc_len"   : len(en_desc),
            "classification": cls,
            "status"        : "pending",
            "msg"           : "",
            "bytes_before"  : len(raw),
            "bytes_after"   : 0,
            "bg_json"       : None,
        })

    # Sayimlar goster
    full_c    = sum(1 for r in targets if r["classification"] == "translate-full")
    partial_c = sum(1 for r in targets if r["classification"] == "translate-partial")
    skip_c    = sum(1 for r in targets if r["classification"] == "skip-empty")
    print(f"[translate_yilmaz_bg] BG eksik: {len(targets)}  "
          f"(full={full_c}, partial={partial_c}, skip-empty={skip_c})")

    sample_outputs = []
    sample_done    = 0

    for idx, r in enumerate(targets):
        slug    = r["slug"]
        machine = r["machine"]
        cls     = r["classification"]

        # skip-empty
        if cls == "skip-empty":
            r["status"] = "skip-empty"
            r["msg"]    = "EN name+desc+specs tamamen bos"
            print(f"[translate_yilmaz_bg] [{idx+1}/{len(targets)}] SKIP-EMPTY  {slug}")
            continue

        is_partial = (cls == "translate-partial")

        # dry-run: sadece ilk DRY_RUN_SAMPLE'i gercekten cevir
        if mode == "dry-run" and sample_done >= DRY_RUN_SAMPLE:
            r["status"] = f"would-translate-{cls.split('-')[1]}"  # would-translate-full / partial
            r["msg"]    = "dry-run: would be translated"
            continue

        # API cagrisi
        print(f"[translate_yilmaz_bg] [{idx+1}/{len(targets)}] "
              f"Translating ({cls}) {slug} ...")
        prompt = build_prompt(machine, glossary_str, partial=is_partial)

        try:
            t0           = time.time()
            result       = call_gemini(prompt, api_key)
            elapsed_call = time.time() - t0
            api_calls   += 1
        except Exception as exc:
            r["status"] = "error"
            r["msg"]    = f"API error: {exc}"
            print(f"[translate_yilmaz_bg]   ERROR {exc}", file=sys.stderr)
            time.sleep(RATE_LIMIT_SECS)
            continue

        errs = validate_response(result, partial=is_partial)
        if errs:
            r["status"] = "error"
            r["msg"]    = "Validation: " + "; ".join(errs)
            print(f"[translate_yilmaz_bg]   VALIDATE FAIL: {errs}", file=sys.stderr)
            time.sleep(RATE_LIMIT_SECS)
            continue

        # partial modda description her zaman ""
        clean_desc = "" if is_partial else result["description"].strip()
        clean_specs = {k: result["specs"].get(k, []) for k in BG_SPECS_KEYS}
        new_bg = {
            "name"       : result["name"].strip(),
            "description": clean_desc,
            "specs"      : clean_specs,
        }

        suffix = "partial" if is_partial else "full"

        # dry-run sample
        if mode == "dry-run":
            r["status"]  = f"sample-{suffix}"
            r["msg"]     = f"API call {elapsed_call:.1f}s"
            r["bg_json"] = new_bg
            sample_outputs.append({"slug": slug, "output": new_bg, "partial": is_partial})
            sample_done += 1
            print(f"[translate_yilmaz_bg]   SAMPLE-{suffix.upper()} OK  name={new_bg['name'][:50]!r}")
            time.sleep(RATE_LIMIT_SECS)
            continue

        # apply: backup + yaz
        bak = alloc_bak(r["path"])
        if bak is None:
            r["status"] = "error"
            r["msg"]    = "backup slots exhausted"
            time.sleep(RATE_LIMIT_SECS)
            continue

        bak.write_bytes(r["raw"])
        new_machine = inject_bg(machine, new_bg)
        le      = detect_le(r["raw"])
        tnl     = has_trailing_nl(r["raw"])
        new_raw = to_bytes(new_machine, le, tnl)

        r["path"].write_bytes(new_raw)
        r["status"]      = f"written-{suffix}"
        r["msg"]         = f"name={new_bg['name'][:35]!r}"
        r["bytes_after"] = len(new_raw)
        r["bg_json"]     = new_bg

        print(f"[translate_yilmaz_bg]   WRITTEN-{suffix.upper()}  "
              f"{r['bytes_before']} -> {len(new_raw)} bytes")
        time.sleep(RATE_LIMIT_SECS)

    elapsed = time.time() - t_start

    written_c = sum(1 for r in targets if r["status"].startswith("written"))
    err_c     = sum(1 for r in targets if r["status"] == "error")
    skip_c2   = sum(1 for r in targets if r["status"] == "skip-empty")
    print(f"[translate_yilmaz_bg] API calls={api_calls}  elapsed={elapsed:.1f}s")
    print(f"[translate_yilmaz_bg] written={written_c}  errors={err_c}  skip-empty={skip_c2}")

    write_report(mode, targets, api_calls, elapsed, sample_outputs, glossary_count)
    return 1 if err_c > 0 else 0


def main():
    parser = argparse.ArgumentParser(
        description="Translate Yilmaz machines English -> Bulgarian via Gemini."
    )
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument("--dry-run", action="store_true",
                     help="Preview + 3 sample translations, no writes (default)")
    grp.add_argument("--apply", action="store_true",
                     help="Translate all targets and write files")
    parser.add_argument(
        "--min-chars", type=int, default=DEFAULT_MIN_CHARS,
        help=f"Min EN description length for full translate (default {DEFAULT_MIN_CHARS})",
    )
    args = parser.parse_args()
    mode = "apply" if args.apply else "dry-run"
    sys.exit(run(mode, args.min_chars))


if __name__ == "__main__":
    main()
