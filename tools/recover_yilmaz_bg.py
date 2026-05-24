#!/usr/bin/env python3
"""
tools/recover_yilmaz_bg.py

Recover Yılmaz BG translations from git commit d6b5cc8 into individual machine files.

KAYNAK : git show d6b5cc8:src/data/machines.json  (74-makine aggregate)
HEDEF  : src/data/machines/yilmaz/<slug>.json      (88 individual dosya)
KAPSAM : 42 makine (43 BG-dolu makineden alm-6510 hariç — individual dosyası yok)

INJECT EDİLEN ALANLAR:
  diller.bg.name          — doğrudan kopyalanır
  diller.bg.description   — doğrudan kopyalanır
  diller.bg.specs         — 3 Kiril key korunur (RENAME YOK), ТЕХНИЧЕСКИ ДАННИ DROP edilir

KORUNAN ALANLAR:
  diller.en, diller.ru, top-level field'lar (slug, brand, categories, type, vb.)

Kullanım:
  python tools/recover_yilmaz_bg.py           # dry-run (varsayılan)
  python tools/recover_yilmaz_bg.py --dry-run
  python tools/recover_yilmaz_bg.py --apply
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ── Sabitler ──────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_COMMIT = "d6b5cc8"
SOURCE_PATH = "src/data/machines.json"
TARGET_DIR = REPO_ROOT / "src" / "data" / "machines" / "yilmaz"
REPORT_PATH = REPO_ROOT / "RECOVERY_APPLY_REPORT_2026-05-23.md"

# Kaynak'ta BG dolu ama hedef dosyası mevcut değil → inject edilemez
EXCLUDED_SLUGS = {"alm-6510-aluminyum-profil-isleme-ve-kesme-merkezi"}

# Ghost: diller.bg key'i var ama tamamen boş — gerçek içerikle replace edilecek
GHOST_SLUGS = {"vce-3500", "vce-4000"}

# BG specs: bu 3 Kiril key olduğu gibi korunur
SPECS_KEEP = [
    "СТАНДАРТНИ АКСЕСОАРИ",
    "ОПЦИОНАЛНИ АКСЕСОАРИ",
    "ОБЩИ ХАРАКТЕРИСТИКИ",
]
# Bu key her zaman boş {} — DROP
SPECS_DROP = "ТЕХНИЧЕСКИ ДАННИ"


# ── Yardımcı fonksiyonlar ──────────────────────────────────────────────────────

def load_source() -> list:
    """git show ile d6b5cc8:machines.json'u oku, parse et."""
    result = subprocess.run(
        ["git", "show", f"{SOURCE_COMMIT}:{SOURCE_PATH}"],
        capture_output=True,
        cwd=str(REPO_ROOT),
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git show failed (exit {result.returncode}): "
            + result.stderr.decode("utf-8", errors="replace").strip()
        )
    return json.loads(result.stdout.decode("utf-8"))


def detect_le(raw: bytes) -> str:
    """CRLF veya LF tespit et."""
    return "\r\n" if b"\r\n" in raw else "\n"


def has_trailing_nl(raw: bytes) -> bool:
    return raw.endswith(b"\n")


def alloc_bak(path: Path):
    """
    .bak, .bak.2 … .bak.5 dene; boş slot bulunca Path döner.
    Tümü doluysa None döner → abort.
    """
    for suffix in [".bak"] + [f".bak.{i}" for i in range(2, 6)]:
        candidate = Path(str(path) + suffix)
        if not candidate.exists():
            return candidate
    return None


def build_bg(src_bg: dict) -> dict:
    """
    d6b5cc8 kaynak BG objesinden temiz diller.bg yap.
    3 Kiril spec key'i korur, ТЕХНИЧЕСКИ ДАННИ drop eder.
    Her 3 key mutlaka var (eksikse [] ile doldurulur).
    """
    src_specs = src_bg.get("specs") or {}
    new_specs = {}
    for key in SPECS_KEEP:
        val = src_specs.get(key)
        new_specs[key] = list(val) if isinstance(val, list) else []

    return {
        "name": src_bg.get("name") or "",
        "description": src_bg.get("description") or "",
        "specs": new_specs,
    }


def validate_bg(bg: dict) -> list:
    """Hata listesi döner. Boş liste = geçerli."""
    errs = []
    if not isinstance(bg.get("name"), str):
        errs.append("name must be str")
    if not isinstance(bg.get("description"), str):
        errs.append("description must be str")
    specs = bg.get("specs")
    if not isinstance(specs, dict):
        errs.append("specs must be dict")
        return errs
    if len(specs) != 3:
        errs.append(f"specs must have exactly 3 keys, got {len(specs)}")
    for k in SPECS_KEEP:
        if k not in specs:
            errs.append(f"specs missing key: {k!r}")
        elif not isinstance(specs[k], list):
            errs.append(f"specs[{k!r}] must be list")
    return errs


def inject_bg(machine: dict, new_bg: dict) -> dict:
    """
    Mevcut machine dict'ine diller.bg inject et.
    - diller.bg zaten varsa: aynı pozisyonda replace et.
    - Yoksa: diller.en'den hemen sonra ekle.
    - Diğer tüm field'lar (en, ru, top-level) dokunulmaz.
    """
    old_diller = dict(machine.get("diller") or {})
    new_diller: dict = {}
    bg_placed = False

    for key, val in old_diller.items():
        if key == "bg":
            new_diller["bg"] = new_bg
            bg_placed = True
        else:
            new_diller[key] = val
            # bg yoksa en'den sonra ekle
            if key == "en" and not bg_placed and "bg" not in old_diller:
                new_diller["bg"] = new_bg
                bg_placed = True

    if not bg_placed:
        new_diller["bg"] = new_bg

    # Machine'i yeniden oluştur — field sırası korunur
    result = {}
    for k, v in machine.items():
        result[k] = new_diller if k == "diller" else v
    return result


def to_bytes(data: dict, le: str, trailing: bool) -> bytes:
    """JSON serialize; line ending ve trailing newline'ı orijinale göre ayarla."""
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if le == "\r\n":
        text = text.replace("\n", "\r\n")
    # Trailing newline normalize
    text = text.rstrip("\r\n")
    if trailing:
        text += le
    return text.encode("utf-8")


# ── Rapor ─────────────────────────────────────────────────────────────────────

def write_report(mode: str, records: list, abort: bool,
                 written: int, bak_count: int, byte_delta: int):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ok_c = sum(1 for r in records if r["status"] in ("will-write", "written"))
    err_c = sum(1 for r in records if r["status"] == "error")
    skip_c = sum(1 for r in records if r["status"] in ("skip", "excluded"))

    L = []
    L.append("# Yılmaz BG Recovery — Apply Report")
    L.append("")
    L.append(f"**Tarih:** {ts}  ")
    L.append(f"**Mod:** `{mode}`  ")
    L.append(f"**Kaynak:** `{SOURCE_COMMIT}:{SOURCE_PATH}`  ")
    L.append(f"**Hedef dizin:** `src/data/machines/yilmaz/`")
    L.append("")
    L.append("## Özet")
    L.append("")
    L.append("| Metrik | Değer |")
    L.append("|---|---|")
    L.append(f"| Başarılı (will-write/written) | {ok_c} |")
    L.append(f"| Hatalı | {err_c} |")
    L.append(f"| Atlanan / Hariç tutuldu | {skip_c} |")
    if mode == "apply" and not abort:
        L.append(f"| Yazılan dosya | {written} |")
        L.append(f"| Backup (.bak) oluşturulan | {bak_count} |")
        L.append(f"| Toplam byte değişimi | {byte_delta:+d} bytes |")
    if abort:
        L.append("| **DURUM** | ❌ **ABORT — hiçbir dosya yazılmadı** |")
    elif mode == "apply":
        L.append("| **DURUM** | ✅ **TAMAMLANDI** |")
    else:
        L.append("| **DURUM** | ℹ️ **DRY-RUN — hiçbir dosya yazılmadı** |")
    L.append("")
    L.append("## Özel Notlar")
    L.append("")
    L.append(
        "- **`alm-6510-aluminyum-profil-isleme-ve-kesme-merkezi`**: "
        "**KAYIP** — individual dosya yok, inject hedefi bulunamadı. "
        "Bu makinenin BG çevirisi kurtarılamaz."
    )
    L.append(
        "- **`vce-3500`**, **`vce-4000`**: ghost BG skeleton "
        "(`name: \"\"`, `description: \"\"`, `images: []`, boş specs) "
        "gerçek içerikle **REPLACE** edildi (`[ghost replaced]` notu ile işaretli)."
    )
    L.append(
        "- BG `specs` anahtarları Kiril alfabesiyle bırakıldı (RENAME YOK): "
        "`СТАНДАРТНИ АКСЕСОАРИ` / `ОПЦИОНАЛНИ АКСЕСОАРИ` / `ОБЩИ ХАРАКТЕРИСТИКИ`."
    )
    L.append(
        "- `ТЕХНИЧЕСКИ ДАННИ` key'i kaynak veride her zaman boş `{}` "
        "olduğundan DROP edildi."
    )
    L.append("- `diller.en`, `diller.ru`, top-level field'lar **değiştirilmedi**.")
    L.append("")
    L.append("## Makine Detay Tablosu")
    L.append("")
    L.append("| # | Slug | Sonuç | Bytes Önce→Sonra | Not |")
    L.append("|---|---|---|---|---|")

    # Sıralama: error/excluded/skip önce, sonra alfabetik
    prio = {"error": 0, "excluded": 1, "skip": 2,
            "will-write": 3, "written": 3, "pending": 3}
    sorted_r = sorted(records, key=lambda r: (prio.get(r["status"], 9), r["slug"]))

    for i, r in enumerate(sorted_r, 1):
        b_before = str(r["bytes_before"]) if r["bytes_before"] else "—"
        b_after = str(r["bytes_after"]) if r["bytes_after"] else "—"
        size_col = f"{b_before} → {b_after}" if b_after != "—" else b_before
        L.append(f"| {i} | `{r['slug']}` | **{r['status']}** | {size_col} | {r['msg']} |")

    L.append("")
    if mode == "apply" and not abort and written > 0:
        L.append("## Backup Dosyaları")
        L.append("")
        for r in records:
            if r["status"] == "written" and r.get("bak"):
                bak_name = Path(r["bak"]).name
                L.append(f"- `{bak_name}`")
        L.append("")

    L.append("---")
    L.append(f"*Generated by `tools/recover_yilmaz_bg.py` — {ts}*")
    L.append("")

    REPORT_PATH.write_text("\n".join(L), encoding="utf-8")
    print(f"[recover_yilmaz_bg] Report → {REPORT_PATH.name}")


# ── Ana akış ──────────────────────────────────────────────────────────────────

def run(mode: str) -> int:
    print(f"[recover_yilmaz_bg] === mode={mode} ===")

    # 1. Kaynak yükle
    print(f"[recover_yilmaz_bg] git show {SOURCE_COMMIT}:{SOURCE_PATH} …")
    try:
        source_machines = load_source()
    except Exception as exc:
        print(f"[recover_yilmaz_bg] ERROR loading source: {exc}", file=sys.stderr)
        return 1

    # BG dolu slug → bg_obj haritası
    bg_map: dict = {}
    for m in source_machines:
        slug = m.get("slug", "")
        bg = (m.get("diller") or {}).get("bg") or {}
        if (bg.get("description") or "").strip():
            bg_map[slug] = bg

    print(f"[recover_yilmaz_bg] BG-dolu kaynak makine: {len(bg_map)}")

    # 2. Her slug için kayıt hazırla (hepsi memory'de, henüz yazılmıyor)
    records: list = []
    abort = False

    for slug in sorted(bg_map.keys()):

        # Hariç tutulan (dosyası yok)
        if slug in EXCLUDED_SLUGS:
            records.append({
                "slug": slug, "status": "excluded",
                "msg": "no individual file — BG content lost (alm-6510)",
                "bytes_before": 0, "bytes_after": 0,
                "new_bytes": None, "path": None, "bak": None,
            })
            continue

        target = TARGET_DIR / f"{slug}.json"
        if not target.exists():
            records.append({
                "slug": slug, "status": "skip",
                "msg": f"target not found: {target.name}",
                "bytes_before": 0, "bytes_after": 0,
                "new_bytes": None, "path": target, "bak": None,
            })
            continue

        raw = target.read_bytes()

        try:
            machine = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            records.append({
                "slug": slug, "status": "error",
                "msg": f"JSON parse error: {exc}",
                "bytes_before": len(raw), "bytes_after": 0,
                "new_bytes": None, "path": target, "bak": None,
            })
            abort = True
            continue

        new_bg = build_bg(bg_map[slug])
        errs = validate_bg(new_bg)
        if errs:
            records.append({
                "slug": slug, "status": "error",
                "msg": "Validation: " + "; ".join(errs),
                "bytes_before": len(raw), "bytes_after": 0,
                "new_bytes": None, "path": target, "bak": None,
            })
            abort = True
            continue

        new_machine = inject_bg(machine, new_bg)
        le = detect_le(raw)
        tnl = has_trailing_nl(raw)
        new_raw = to_bytes(new_machine, le, tnl)

        ghost_note = " [ghost replaced]" if slug in GHOST_SLUGS else ""
        records.append({
            "slug": slug,
            "status": "will-write" if mode == "dry-run" else "pending",
            "msg": f"OK{ghost_note}",
            "bytes_before": len(raw), "bytes_after": len(new_raw),
            "new_bytes": new_raw, "path": target, "bak": None,
        })

    # 3. Herhangi hata varsa abort
    if abort:
        print("[recover_yilmaz_bg] ABORT — validation/parse errors. No files written.",
              file=sys.stderr)
        write_report(mode, records, abort=True, written=0, bak_count=0, byte_delta=0)
        return 1

    # 4. Apply modu
    written = 0
    bak_count = 0
    byte_delta = 0

    if mode == "apply":
        # Backup slot ön-kontrolü (atomik — tümü hazır değilse hiç yazma)
        for r in records:
            if r["status"] == "pending":
                bak = alloc_bak(r["path"])
                if bak is None:
                    r["status"] = "error"
                    r["msg"] = "backup slots exhausted (.bak … .bak.5 all exist)"
                    abort = True
                else:
                    r["bak"] = str(bak)

        if abort:
            print("[recover_yilmaz_bg] ABORT — backup allocation failed.", file=sys.stderr)
            write_report(mode, records, abort=True, written=0, bak_count=0, byte_delta=0)
            return 1

        # Önce tüm backup'ları yaz
        for r in records:
            if r["status"] == "pending":
                Path(r["bak"]).write_bytes(r["path"].read_bytes())
                bak_count += 1

        # Sonra tüm hedef dosyaları yaz
        for r in records:
            if r["status"] == "pending":
                r["path"].write_bytes(r["new_bytes"])
                r["status"] = "written"
                written += 1
                byte_delta += r["bytes_after"] - r["bytes_before"]

    # 5. Raporu yaz
    write_report(mode, records, abort=False,
                 written=written, bak_count=bak_count, byte_delta=byte_delta)

    # 6. Özet
    ok_c = sum(1 for r in records if r["status"] in ("will-write", "written"))
    err_c = sum(1 for r in records if r["status"] == "error")
    skip_c = sum(1 for r in records if r["status"] in ("skip", "excluded"))
    print(f"[recover_yilmaz_bg] OK={ok_c}  ERR={err_c}  SKIP={skip_c}")
    if mode == "apply":
        print(f"[recover_yilmaz_bg] Written={written}  Backups={bak_count}  "
              f"Δbytes={byte_delta:+d}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Recover Yılmaz BG translations from d6b5cc8 into individual JSON files."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--dry-run", action="store_true",
        help="Preview only — no files written (default if no flag given)"
    )
    group.add_argument(
        "--apply", action="store_true",
        help="Write files with backups"
    )
    args = parser.parse_args()
    mode = "apply" if args.apply else "dry-run"
    sys.exit(run(mode))


if __name__ == "__main__":
    main()
