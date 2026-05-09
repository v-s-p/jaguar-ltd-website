"""
recover_yedek.py — machines_yedek.json zengin içeriğini machines.json'a merge eder.

Strateji:
  - Model kodu öneki (ilk 3 slug parçası) ile eşleştir
  - Match: yedek diller (9 dil) al, mevcut slug/brand/categories/subcategory koru
  - Sadece yedekte var: _pending_review.json'a yaz (metadata eksik)
  - Sadece mevcut var: dokunma
  - Çıktı: machines.json.new (eski machines.json'a dokunulmaz)
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

YEDEK_PATH   = Path("src/data/machines_yedek.json")
MEVCUT_PATH  = Path("src/data/machines.json")
OUTPUT_PATH  = Path("src/data/machines.json.new")
PENDING_PATH = Path("src/data/_pending_review.json")


def model_key(slug: str) -> str:
    """İlk 3 slug parçasını model kodu olarak döndür (ör: 'ack-420-s')."""
    return "-".join(slug.split("-")[:3]).lower()


def main():
    with open(YEDEK_PATH, encoding="utf-8") as f:
        yedek = json.load(f)
    with open(MEVCUT_PATH, encoding="utf-8") as f:
        mevcut = json.load(f)

    # Mevcut makineleri model kodu ile indeksle
    mevcut_by_model: dict = {}
    for m in mevcut:
        key = model_key(m["slug"])
        mevcut_by_model[key] = m

    yedek_by_model: dict = {}
    for m in yedek:
        key = model_key(m["slug"])
        yedek_by_model[key] = m

    merged_machines = []
    stats = {"merged": 0, "mevcut_only": 0, "pending": 0}
    pending = []

    # 1. Tüm mevcut makineleri gez — match varsa yedek diller'ı ekle
    matched_model_keys = set()
    for m in mevcut:
        key = model_key(m["slug"])
        if key in yedek_by_model:
            y = yedek_by_model[key]
            # Yedek diller'ı mevcut makineye ekle (mevcut metadata korunur)
            enriched = {
                "slug":        m["slug"],          # mevcut İngilizce slug korunur
                "brand":       m.get("brand"),
                "categories":  m.get("categories"),
                "subcategory": m.get("subcategory"),
                "diller":      y["diller"],         # yedek 9-dil içeriği
            }
            # Mevcut EN'deki specs/technical_data/catalog'ı koru
            m_en = m["diller"].get("en", {})
            if "en" not in enriched["diller"]:
                enriched["diller"]["en"] = {}
            for preserve_key in ("specs", "technical_data", "catalog"):
                if preserve_key in m_en and preserve_key not in enriched["diller"]["en"]:
                    enriched["diller"]["en"][preserve_key] = m_en[preserve_key]

            merged_machines.append(enriched)
            matched_model_keys.add(key)
            stats["merged"] += 1
        else:
            # Mevcut-only: dokunma
            merged_machines.append(m)
            stats["mevcut_only"] += 1

    # 2. Sadece yedekte olan makineler → pending
    for m in yedek:
        key = model_key(m["slug"])
        if key not in matched_model_keys:
            pending.append(m)
            stats["pending"] += 1

    # Çıktı
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(merged_machines, f, ensure_ascii=False, indent=2)

    with open(PENDING_PATH, "w", encoding="utf-8") as f:
        json.dump(pending, f, ensure_ascii=False, indent=2)

    print("\n=== RECOVER_YEDEK SONUCU ===")
    print(f"Toplam birlestirildi (merged):      {stats['merged']}")
    print(f"Mevcut korundu (mevcut-only):       {stats['mevcut_only']}")
    print(f"Inceleme bekliyor (pending):         {stats['pending']}")
    print(f"machines.json.new toplam kayit:      {len(merged_machines)}")
    print(f"\nCikti: {OUTPUT_PATH}")
    print(f"Pending: {PENDING_PATH}")

    # İçerik kalite kontrolü
    sample = next((m for m in merged_machines if "diller" in m and len(m["diller"]) > 1), None)
    if sample:
        print(f"\nOrnek merged makine: {sample['slug']}")
        print(f"  diller: {list(sample['diller'].keys())}")
        tr = sample["diller"].get("tr", {})
        print(f"  TR isim: {tr.get('isim','?')}")
        print(f"  TR aciklama len: {len(tr.get('aciklama',''))} chars")
        print(f"  brand: {sample.get('brand')}")
        print(f"  categories: {sample.get('categories')}")

    if pending:
        print(f"\nPending makineler (ilk 5):")
        for p in pending[:5]:
            name = p["diller"].get("tr", p["diller"].get("en", {})).get("isim", p["slug"])
            print(f"  - {p['slug']} | {name}")
        if len(pending) > 5:
            print(f"  ... ve {len(pending)-5} tane daha")


if __name__ == "__main__":
    main()
