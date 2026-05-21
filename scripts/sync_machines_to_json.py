"""
Sync per-machine JSON files back into monolithic arrays.
src/data/machines/yilmaz/*.json    -> src/data/yilmaz.json
src/data/machines/gocmaksan/*.json -> src/data/gocmaksan.json
Ordering: alphabetical by slug (filename).
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRANDS = {
    "yilmaz":    ROOT / "src" / "data" / "yilmaz.json",
    "gocmaksan": ROOT / "src" / "data" / "gocmaksan.json",
}

total = 0
for brand, dest_path in BRANDS.items():
    machines_dir = ROOT / "src" / "data" / "machines" / brand
    if not machines_dir.exists():
        print(f"  [SKIP] {brand}: klasor bulunamadi {machines_dir}")
        continue

    files = sorted(machines_dir.glob("*.json"))
    machines = []
    for f in files:
        with open(f, encoding="utf-8") as fp:
            machines.append(json.load(fp))

    with open(dest_path, "w", encoding="utf-8") as fp:
        json.dump(machines, fp, ensure_ascii=False, indent=2)

    print(f"  {brand}: {len(machines)} makine -> {dest_path.name}")
    total += len(machines)

print(f"\nToplam: {total} makine merge edildi.")
