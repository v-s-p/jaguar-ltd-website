"""
Split monolithic JSON arrays into per-machine files.
src/data/yilmaz.json    -> src/data/machines/yilmaz/{slug}.json
src/data/gocmaksan.json -> src/data/machines/gocmaksan/{slug}.json
"""
import json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRANDS = {
    "yilmaz":    ROOT / "src" / "data" / "yilmaz.json",
    "gocmaksan": ROOT / "src" / "data" / "gocmaksan.json",
}

total = 0
for brand, src_path in BRANDS.items():
    out_dir = ROOT / "src" / "data" / "machines" / brand
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(src_path, encoding="utf-8") as f:
        machines = json.load(f)

    count = 0
    for machine in machines:
        slug = machine.get("slug")
        if not slug:
            print(f"  [SKIP] {brand}: slug yok -> {machine}")
            continue
        out_file = out_dir / f"{slug}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(machine, f, ensure_ascii=False, indent=2)
        count += 1

    print(f"  {brand}: {count} dosya -> {out_dir}")
    total += count

print(f"\nToplam: {total} dosya olusturuldu.")
