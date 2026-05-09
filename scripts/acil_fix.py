#!/usr/bin/env python3
# ACK 550 ve ACK 700 resim fix - mevcut machines.json'u geri yukler ve duzeltir
import json, shutil
from pathlib import Path

JSON = Path(r"C:\Users\Kenan\Desktop\AI\Jaguar-ltd\src\data\machines.json")
YEDEK = Path(r"C:\Users\Kenan\Desktop\AI\Jaguar-ltd\src\data\machines_duzelt_yedek_20260419_1755.json")

# Yedeği geri yükle (tam 89 makine)
if not YEDEK.exists():
    print("HATA: Yedek bulunamadi:", YEDEK)
    exit(1)

with open(YEDEK, 'r', encoding='utf-8') as f:
    data = json.load(f)

# ACK 550 ve 700 resimlerini düzelt
fixes = {
    "ack-550-up-cutting-saw-machine": [
        "/images/machines/ack-550-alttan-cikma-kesme-makinesi-1.jpg",
        "/images/machines/ack-550-alttan-cikma-kesme-makinesi-2.png"
    ],
    "ack-700-up-cutting-saw-machine": [
        "/images/machines/ack-700-alttan-cikma-kesme-makinesi-1.jpg"
    ]
}

for m in data:
    if m["slug"] in fixes:
        for dil in m["diller"].values():
            dil["resimler"] = fixes[m["slug"]]
        print(f"[OK] {m['slug']} - resim duzeltildi")

# Kaydet
with open(JSON, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Dogrula
bozuk = sum(1 for m in data if "logo.sv" in (m["diller"]["tr"]["resimler"] or [""])[0])
print(f"\nSonuc: {len(data)} makine, {bozuk} bozuk resim")
print("machines.json guncellendi!")
