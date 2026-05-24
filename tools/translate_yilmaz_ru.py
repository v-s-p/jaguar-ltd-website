#!/usr/bin/env python3
"""
tools/translate_yilmaz_ru.py

Translate Yilmaz machine diller.ru.name Turkish -> Russian via Gemini 2.5-flash.
SADECE diller.ru.name degistirilir -- diger hic bir alan dokunulmaz.

KAYNAK : src/data/machines/yilmaz/<slug>.json  diller.ru.name (Turkce - yedekten)
HEDEF  : ayni dosya -- diller.ru.name Rusca ile guncellendi
API    : Gemini REST  gemini-2.5-flash  response_mime_type=application/json

Siniflandirma:
  translate      -- TR karakter (C,G,I,S,U,O varyantlari) VEYA TR anahtar kelime
  skip-cyrillic  -- Zaten Kiril, ceviri gerekmiyor

Atomiklik (apply modunda):
  Phase 1: Tum makineler icin Gemini call (memory'de topla)
  Phase 2: Validate (model kodu Latin kontrolu)
  Phase 3: Batch write (once backup, sonra hepsi)
  Phase 4: sync_machines_to_json.py hook

Kullanim:
    python tools/translate_yilmaz_ru.py              # dry-run (varsayilan)
    python tools/translate_yilmaz_ru.py --dry-run    # 5 sample, dosya yazma yok
    python tools/translate_yilmaz_ru.py --apply      # tumunu cevir, yaz, sync

Gereksinimler:
    pip install requests
    GEMINI_API_KEY -> .env (repo root) veya ortam degiskeni
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib3
from datetime import datetime
from pathlib import Path

import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------
REPO_ROOT   = Path(__file__).resolve().parent.parent
YILMAZ_DIR  = REPO_ROOT / "src" / "data" / "machines" / "yilmaz"
REPORT_PATH = REPO_ROOT / "TRANSLATE_YILMAZ_RU_NAME_REPORT_2026-05-23.md"
SYNC_SCRIPT = REPO_ROOT / "scripts" / "sync_machines_to_json.py"

MODEL_NAME      = "gemini-2.5-flash"
GEMINI_URL      = (
    "https://generativelanguage.googleapis.com"
    f"/v1beta/models/{MODEL_NAME}:generateContent?key={{key}}"
)
RATE_LIMIT_SECS = 4
DRY_RUN_SAMPLE  = 5

# Bilinen Latin model kodlari (Kiril'e donusmemeli)
LATIN_MODEL_CODES = frozenset({
    "ACK", "AIM", "DC", "KD", "CPM", "CRM", "SNM", "PIM", "CK", "SM",
    "VCE", "ALM", "MEM", "CNC", "FR", "GAS", "MCA", "MK", "MKN", "NSM",
    "PWB", "PYE", "RS", "RYK", "SCM", "SDT", "SK", "SKN", "ST", "TK",
    "VK", "WGM", "CCL", "CA", "DKN", "HDL", "HP", "GPT", "GT", "PC",
    "PT", "RT", "VP", "WAS", "WB", "KP", "KY", "CDC", "DK", "NCR",
})

# Kiril buyuk harf guard (ilk 8 karakter)
_UPPER_CYR_RE = re.compile(r"[А-ЯЁ]{2,}")

# Turkce karakter tespiti
_TR_CHARS_RE = re.compile(r"[ÇĞİŞÜÖçğışüö]")
_TR_KEYWORDS = frozenset({
    "MAKINESI", "ISLEME", "MERKEZI", "KESME", "ALTTAN", "CIKMA",
    "PROFIL", "KOSE", "KOPYA", "FREZE", "KAYNAK", "CIFT", "TEK",
    "DORT", "ALUMINYUM", "TORCE", "VIDALAMA", "KUCUK", "BUYUK",
    "PRES", "MAKINA", "ROBOT", "YUZEY", "KOPUK", "KAPI", "PENCERE",
    "AGAC", "GUCLENDIRME", "AYNA", "ICIN", "VIDA", "ARACI", "SISTEMI",
})

# Kiril varlik tespiti
_CYRILLIC_RE = re.compile(r"[а-яёА-ЯЁ]")

# ---------------------------------------------------------------------------
# .env yukleyici
# ---------------------------------------------------------------------------
_env_path = REPO_ROOT / ".env"
if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        if _line.startswith("GEMINI_API_KEY="):
            os.environ.setdefault("GEMINI_API_KEY", _line.split("=", 1)[1].strip())

# ---------------------------------------------------------------------------
# Few-shot ornekleri (prompt'a gomulu)
# ---------------------------------------------------------------------------
FEW_SHOT_BLOCK = """\
REFERENCE TRANSLATIONS (3 confirmed examples — match this style exactly):

TR: "ACK 420 S ALTTAN CIKMA KESME MAKINESI"
RU: "ACK 420 S Отрезная машина с нижней подачей"

TR: "DC 421 CIFT KAFA KESME MAKINESI"
RU: "DC 421 Двухголовая отрезная машина"

TR: "AIM 4420 ALUMINYUM PROFIL ISLEME MERKEZI"
RU: "AIM 4420 Центр обработки алюминиевых профилей"
"""

# ---------------------------------------------------------------------------
# Glossary (TR -> RU terim eslestirmesi)
# ---------------------------------------------------------------------------
GLOSSARY_TR_RU = {
    "alttan cikma":     "с нижней подачей",
    "kesme makinesi":   "отрезная машина",
    "cift kafa":        "двухголовая",
    "tek kafa":         "одноголовая",
    "dort kafa":        "четырёхголовая",
    "isleme merkezi":   "центр обработки",
    "aluminyum profil": "алюминиевый профиль",
    "kose temizleme":   "зачистка углов",
    "kose pres":        "угловой пресс",
    "kaynak makinesi":  "сварочная машина",
    "kopya freze":      "копировально-фрезерный станок",
    "torcefreze":       "торцефрезерный станок",
}

def build_glossary_block() -> str:
    lines = ["TERM GLOSSARY (Turkish -> Russian):"]
    for tr, ru in GLOSSARY_TR_RU.items():
        lines.append(f'  "{tr}" -> "{ru}"')
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------
PROMPT_TEMPLATE = """\
{few_shot_block}

{glossary_block}

RULES:
1. Keep model codes STRICTLY LATIN — NEVER transliterate to Cyrillic:
   ACK, AIM, DC, KD, CPM, CRM, SNM, PIM, CK, SM, VCE, ALM, MEM, CNC, WGM
   CORRECT: "ACK 420 S Отрезная машина"
   WRONG:   "АСК 420 S Отрезная машина"  (Cyrillic ACK = FORBIDDEN)

2. Use Russian sentence case:
   - Model code + number: exactly as-is (e.g. "DC 421" stays "DC 421")
   - Russian words: first word uppercase, rest lowercase
   - CORRECT: "ACK 420 S Отрезная машина с нижней подачей"
   - WRONG:   "ACK 420 S ОТРЕЗНАЯ МАШИНА С НИЖНЕЙ ПОДАЧЕЙ"

3. Use terminology from the Russian description and English name below —
   they describe the same machine and give context for correct Russian terminology.

4. If the source name is just a model code with no descriptive words, derive
   the Russian machine type from the English name hint and description context.

5. Output format: JSON object with single key "name"
   Example: {{"name": "ACK 420 S Отрезная машина с нижней подачей"}}
   No commentary, no explanation, no markdown fences.

CONTEXT — existing data for this exact machine:
English name (hint): {en_name}
Russian description:
---
{ru_description}
---

Now produce the Russian name for this machine.
Source name (Turkish or bare model code): "{tr_name}"
"""

# ---------------------------------------------------------------------------
# Yardimci fonksiyonlar
# ---------------------------------------------------------------------------

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


def classify_name(name: str) -> str:
    """
    'translate'     -- TR karakter veya TR anahtar kelime bulundu
    'skip-cyrillic' -- Zaten Kiril iceriyor, ceviri gereksiz
    'translate'     -- Sadece model kodu/sayi, betimleyici kelime yok
                       (Gemini'ye gonder, duzgun bir RU name uretsin)
    """
    upper = name.upper()

    # TR karakter var mi?
    if _TR_CHARS_RE.search(name):
        return "translate"

    # TR anahtar kelime var mi?
    for kw in _TR_KEYWORDS:
        if kw in upper:
            return "translate"

    # Kiril var mi? (zaten cevrilmis)
    if _CYRILLIC_RE.search(name):
        return "skip-cyrillic"

    # Sadece model kodu + sayi (ornk "AIM 4420") -> gene de cevir
    return "translate"


def _is_garbage_name(name: str) -> bool:
    """HTML tag veya ham URL iceriyorsa garbage sayilir."""
    return "<" in name or "http://" in name or "https://" in name


def get_source_name(machine: dict) -> str:
    """
    diller.ru.name -> diller.tr.name -> diller.en.name fallback.
    HTML/URL garbage degerler atlanir (yedekten gelen bozuk veri).
    """
    diller = machine.get("diller") or {}
    for lang in ("ru", "tr", "en"):
        name = ((diller.get(lang) or {}).get("name") or "").strip()
        if name and not _is_garbage_name(name):
            return name
    return ""


def get_ru_description(machine: dict) -> str:
    diller = machine.get("diller") or {}
    return ((diller.get("ru") or {}).get("description") or "").strip()


def get_en_name(machine: dict) -> str:
    diller = machine.get("diller") or {}
    return ((diller.get("en") or {}).get("name") or "").strip()


def check_model_code_latin(ru_name: str) -> str | None:
    """
    Ilk 8 karakterde 2+ buyuk Kiril harf varsa FLAG dondur.
    Gemini'nin AIM -> AIM yerine AИМ yazmasini yakalar.
    """
    prefix = ru_name[:8]
    m = _UPPER_CYR_RE.search(prefix)
    if m:
        return (
            f"Cyrillic model code detected in prefix '{prefix}' "
            f"(match: '{m.group()}') — check if '{ru_name.split()[0]}' should stay Latin"
        )
    return None


def call_gemini(prompt: str, api_key: str) -> str:
    """Gemini'yi cagir, RU name'i string olarak dondur."""
    url = GEMINI_URL.format(key=api_key)
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
        raise RuntimeError(
            f"Gemini API error: {body['error'].get('message', body['error'])}"
        )
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")

    raw_text = body["candidates"][0]["content"]["parts"][0]["text"].strip()

    # Markdown fence temizle
    if raw_text.startswith("```"):
        lines    = raw_text.splitlines()
        raw_text = "\n".join(l for l in lines if not l.startswith("```")).strip()

    # JSON parse
    parsed = json.loads(raw_text)
    name   = (parsed.get("name") or "").strip()
    return name


def inject_ru_name(machine: dict, new_name: str) -> dict:
    """SADECE diller.ru.name'i guncelle, her sey korunur."""
    result = {}
    for k, v in machine.items():
        if k != "diller":
            result[k] = v
            continue
        new_diller = {}
        for lang, lang_data in (v or {}).items():
            if lang == "ru":
                new_ru = dict(lang_data or {})
                new_ru["name"] = new_name
                new_diller["ru"] = new_ru
            else:
                new_diller[lang] = lang_data
        result["diller"] = new_diller
    return result


def to_bytes(data: dict, le: str, trailing: bool) -> bytes:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if le == "\r\n":
        text = text.replace("\n", "\r\n")
    text = text.rstrip("\r\n")
    if trailing:
        text += le
    return text.encode("utf-8")


# ---------------------------------------------------------------------------
# Rapor yazici
# ---------------------------------------------------------------------------

def write_report(
    mode: str,
    results: list,
    api_calls: int,
    elapsed: float,
    sample_outputs: list,
    sync_output: str,
):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    translate_c     = sum(1 for r in results if r["cls"] == "translate")
    skip_cyrillic_c = sum(1 for r in results if r["cls"] == "skip-cyrillic")
    written_c       = sum(1 for r in results if r["status"] == "written")
    error_c         = sum(1 for r in results if r["status"] == "error")
    flag_c          = sum(1 for r in results if r.get("flag"))
    sampled_c       = sum(1 for r in results if r["status"] == "sample")
    would_c         = sum(1 for r in results if r["status"] == "would-translate")

    L = []
    L.append("# Yilmaz RU Name Ceviri Raporu")
    L.append("")
    L.append(f"**Tarih:** {ts}  ")
    L.append(f"**Mod:** `{mode}`  ")
    L.append(f"**Model:** `{MODEL_NAME}`  ")
    L.append(f"**Rate limit:** {RATE_LIMIT_SECS}s / call  ")
    L.append("")
    L.append("## Ozet")
    L.append("")
    L.append("| Metrik | Deger |")
    L.append("|---|---|")
    L.append(f"| Toplam makine | {len(results)} |")
    L.append(f"| Ceviri hedefi | {translate_c} |")
    L.append(f"| Skip (zaten Kiril) | {skip_cyrillic_c} |")
    L.append(f"| API call sayisi | {api_calls} |")
    L.append(f"| Toplam sure | {elapsed:.1f}s |")
    if mode == "dry-run":
        L.append(f"| Sample (cevrildi, yazilmadi) | {sampled_c} |")
        L.append(f"| Would-translate (kalan) | {would_c} |")
        L.append(f"| Model kodu flag | {flag_c} |")
        L.append(f"| Hata | {error_c} |")
        L.append("| **DURUM** | INFO **DRY-RUN — dosya yazilmadi** |")
    else:
        L.append(f"| Yazilan | {written_c} |")
        L.append(f"| Model kodu flag | {flag_c} |")
        L.append(f"| Hata | {error_c} |")
        if error_c == 0 and flag_c == 0:
            L.append(f"| **DURUM** | OK **TAMAMLANDI ({written_c} yazildi, 0 flag)** |")
        elif error_c == 0:
            L.append(
                f"| **DURUM** | WARN **{written_c} yazildi, {flag_c} flag — kontrol et** |"
            )
        else:
            L.append(
                f"| **DURUM** | ERROR **{written_c} yazildi, {error_c} hata, {flag_c} flag** |"
            )

    # Sample ciktilar (dry-run)
    if sample_outputs:
        L.append("")
        L.append(f"## Ornek Ceviriler (ilk {DRY_RUN_SAMPLE} — kalite kontrol)")
        L.append("")
        for s in sample_outputs:
            flag_str = f"  \n  - ⚠️ FLAG: {s['flag']}" if s.get("flag") else ""
            L.append(f"### `{s['slug']}`")
            L.append(f"- **TR:** `{s['old']}`")
            L.append(f"- **RU:** `{s['new']}`{flag_str}")
            L.append("")

    # Model kodu flag listesi
    flagged = [r for r in results if r.get("flag")]
    if flagged:
        L.append("")
        L.append("## Model Kodu Flag Listesi")
        L.append("")
        L.append("Bu makinelerin ilk 8 karakterinde buyuk Kiril bulundu — RU name'i elle dogrula:")
        L.append("")
        for r in flagged:
            L.append(f"- `{r['slug']}`: `{r.get('new_name', '')}` — {r['flag']}")

    # Hata listesi
    errors = [r for r in results if r["status"] == "error"]
    if errors:
        L.append("")
        L.append("## Hata Listesi")
        L.append("")
        for r in errors:
            L.append(f"- `{r['slug']}`: {r['msg']}")

    # Skip listesi
    skips = [r for r in results if r["cls"] == "skip-cyrillic"]
    if skips:
        L.append("")
        L.append("## Skip Listesi (zaten Kiril)")
        L.append("")
        for r in skips:
            L.append(f"- `{r['slug']}`: `{r.get('old_name', '')}`")

    # Tam makine tablosu
    L.append("")
    L.append("## Makine Tablosu (eski -> yeni name)")
    L.append("")
    L.append("| # | Slug | Eski (TR) | Yeni (RU) | Durum |")
    L.append("|---|---|---|---|---|")
    for i, r in enumerate(results, 1):
        old  = (r.get("old_name") or "—")[:55]
        new  = (r.get("new_name") or "—")[:55]
        flag = " ⚠️" if r.get("flag") else ""
        L.append(
            f"| {i} | `{r['slug']}` | {old} | {new} | **{r['status']}**{flag} |"
        )

    # Sync hook ciktisi
    if sync_output:
        L.append("")
        L.append("## Sync Hook Ciktisi")
        L.append("")
        L.append("```")
        L.append(sync_output)
        L.append("```")

    L.append("")
    L.append("---")
    L.append(f"*Generated by `tools/translate_yilmaz_ru.py` — {ts}*")
    L.append("")

    REPORT_PATH.write_text("\n".join(L), encoding="utf-8")
    print(f"[translate_yilmaz_ru] Rapor -> {REPORT_PATH.name}")


# ---------------------------------------------------------------------------
# Ana akis
# ---------------------------------------------------------------------------

def run(mode: str) -> int:
    print(f"[translate_yilmaz_ru] === mode={mode} | model={MODEL_NAME} ===")
    api_key        = load_env_key()
    t_start        = time.time()
    api_calls      = 0
    glossary_block = build_glossary_block()

    # ------------------------------------------------------------------ #
    # 1. Tara: tum makineleri yukle + siniflandir
    # ------------------------------------------------------------------ #
    all_files = sorted(f for f in YILMAZ_DIR.glob("*.json") if ".bak" not in f.name)
    results   = []

    for fpath in all_files:
        raw = fpath.read_bytes()
        try:
            machine = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            results.append({
                "slug": fpath.stem, "cls": "error", "status": "error",
                "old_name": "", "new_name": "",
                "msg": f"JSON parse: {exc}", "flag": None,
                "raw": raw, "path": fpath, "machine": None,
            })
            continue

        slug     = machine.get("slug") or fpath.stem
        src_name = get_source_name(machine)
        cls      = classify_name(src_name)

        results.append({
            "slug"    : slug,
            "cls"     : cls,
            "status"  : "pending",
            "old_name": src_name,
            "new_name": "",
            "msg"     : "",
            "flag"    : None,
            "raw"     : raw,
            "path"    : fpath,
            "machine" : machine,
        })

    translate_c = sum(1 for r in results if r["cls"] == "translate")
    skip_c      = sum(1 for r in results if r["cls"] == "skip-cyrillic")
    print(
        f"[translate_yilmaz_ru] Toplam: {len(results)} | "
        f"ceviri hedefi: {translate_c} | skip-cyrillic: {skip_c}"
    )

    # ------------------------------------------------------------------ #
    # 2. Gemini calls — dry-run: ilk 5 | apply: tumunu topla (atomik)
    # ------------------------------------------------------------------ #
    sample_outputs = []
    sample_done    = 0

    for idx, r in enumerate(results):
        if r["cls"] != "translate":
            r["status"]   = "skip-cyrillic" if r["cls"] == "skip-cyrillic" else "skip-other"
            r["new_name"] = r["old_name"]
            continue

        # dry-run sadece DRY_RUN_SAMPLE kadar cagri yapar
        if mode == "dry-run" and sample_done >= DRY_RUN_SAMPLE:
            r["status"] = "would-translate"
            r["msg"]    = "dry-run: would be translated"
            continue

        machine  = r["machine"]
        slug     = r["slug"]
        src_name = r["old_name"]
        ru_desc  = get_ru_description(machine)
        en_name  = get_en_name(machine)

        prompt = PROMPT_TEMPLATE.format(
            few_shot_block = FEW_SHOT_BLOCK,
            glossary_block = glossary_block,
            en_name        = en_name or "(not available)",
            ru_description = ru_desc[:800] if ru_desc else "(no description available)",
            tr_name        = src_name,
        )

        print(
            f"[translate_yilmaz_ru] [{idx+1}/{len(results)}] "
            f"Translating: {src_name[:65]!r}"
        )

        try:
            t0           = time.time()
            ru_name      = call_gemini(prompt, api_key)
            elapsed_call = time.time() - t0
            api_calls   += 1
        except Exception as exc:
            r["status"] = "error"
            r["msg"]    = f"API error: {exc}"
            print(f"[translate_yilmaz_ru]   ERROR: {exc}", file=sys.stderr)
            time.sleep(RATE_LIMIT_SECS)
            continue

        if not ru_name.strip():
            r["status"] = "error"
            r["msg"]    = "Gemini empty response"
            print(f"[translate_yilmaz_ru]   ERROR: empty response", file=sys.stderr)
            time.sleep(RATE_LIMIT_SECS)
            continue

        # Model kodu Latin guard
        flag = check_model_code_latin(ru_name)
        r["new_name"] = ru_name
        r["flag"]     = flag

        if flag:
            print(f"[translate_yilmaz_ru]   FLAG: {flag}")

        print(
            f"[translate_yilmaz_ru]   {src_name[:40]!r} "
            f"-> {ru_name[:65]!r}  ({elapsed_call:.1f}s)"
        )

        if mode == "dry-run":
            r["status"] = "sample"
            r["msg"]    = f"call {elapsed_call:.1f}s"
            sample_outputs.append({
                "slug": slug, "old": src_name, "new": ru_name, "flag": flag,
            })
            sample_done += 1
        else:
            # apply: memory'e al, henuz yazma (Phase 3'te batch yazilacak)
            r["status"] = "ready"
            r["msg"]    = f"call {elapsed_call:.1f}s"

        time.sleep(RATE_LIMIT_SECS)

    # ------------------------------------------------------------------ #
    # 3. Apply — atomik batch write
    # ------------------------------------------------------------------ #
    sync_output = ""
    if mode == "apply":
        ready = [r for r in results if r["status"] == "ready"]
        print(f"\n[translate_yilmaz_ru] Batch write: {len(ready)} dosya...")

        # Phase A: once tum backup'lari olustur
        for r in ready:
            bak = alloc_bak(r["path"])
            if bak is None:
                r["status"] = "error"
                r["msg"]    = "backup slots exhausted"
                continue
            bak.write_bytes(r["raw"])
            r["_bak"] = bak

        # Phase B: yaz
        for r in ready:
            if r["status"] == "error":
                continue
            new_machine = inject_ru_name(r["machine"], r["new_name"])
            le          = detect_le(r["raw"])
            tnl         = has_trailing_nl(r["raw"])
            new_raw     = to_bytes(new_machine, le, tnl)
            r["path"].write_bytes(new_raw)
            r["status"]  = "written"
            r["msg"]    += f" | {len(r['raw'])} -> {len(new_raw)} bytes"
            print(
                f"[translate_yilmaz_ru]   WRITTEN  {r['slug']}"
                f"  {r['old_name'][:35]!r} -> {r['new_name'][:55]!r}"
            )

        written_c = sum(1 for r in results if r["status"] == "written")
        error_c   = sum(1 for r in results if r["status"] == "error")
        flag_c    = sum(1 for r in results if r.get("flag"))
        print(
            f"[translate_yilmaz_ru] written={written_c}  "
            f"errors={error_c}  flags={flag_c}"
        )

        # Phase C: sync hook
        print(f"[translate_yilmaz_ru] Running sync: {SYNC_SCRIPT.name}")
        try:
            proc = subprocess.run(
                [sys.executable, str(SYNC_SCRIPT)],
                capture_output=True, text=True, encoding="utf-8", check=True,
            )
            sync_output = proc.stdout.strip()
            print(f"[translate_yilmaz_ru] Sync OK: {sync_output}")
        except subprocess.CalledProcessError as exc:
            sync_output = f"HATA: {exc.stderr}"
            print(
                f"[translate_yilmaz_ru] Sync ERROR: {exc.stderr}", file=sys.stderr
            )

    # pending'de kalan varsa hata say
    for r in results:
        if r["status"] == "pending":
            r["status"] = "skip-other"

    elapsed  = time.time() - t_start
    error_c  = sum(1 for r in results if r["status"] == "error")
    flag_c   = sum(1 for r in results if r.get("flag"))

    print(
        f"[translate_yilmaz_ru] DONE  API calls={api_calls}  "
        f"elapsed={elapsed:.1f}s  flags={flag_c}  errors={error_c}"
    )

    write_report(mode, results, api_calls, elapsed, sample_outputs, sync_output)
    return 1 if (error_c > 0 or flag_c > 0) else 0


# ---------------------------------------------------------------------------
# Giris noktasi
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            f"Translate Yilmaz diller.ru.name Turkish -> Russian via {MODEL_NAME}. "
            f"SADECE diller.ru.name degistirilir."
        )
    )
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument(
        "--dry-run", action="store_true",
        help=f"Preview: {DRY_RUN_SAMPLE} sample Gemini calls, dosya yazma yok (varsayilan)",
    )
    grp.add_argument(
        "--apply", action="store_true",
        help="Tum makineleri cevir, atomik yaz, sync_machines_to_json.py calistir",
    )
    args = parser.parse_args()
    mode = "apply" if args.apply else "dry-run"
    sys.exit(run(mode))


if __name__ == "__main__":
    main()
