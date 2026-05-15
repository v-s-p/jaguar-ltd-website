"""
Patch HB-12x3, HB-12x6, MH-8C specs only.
Uses text-block-5 items as FEATURED FEATURES; extracts voltage into TECHNICAL DATA.
Does NOT touch any other machines.
"""

import json, re, time
import urllib.request
from html import unescape

DATA_PATH = r"C:\Users\Kenan\Desktop\AI\Jaguar-ltd\src\data\gocmaksan.json"
SF_BASE   = "https://www.gocmaksan.com/eng/demir-tesisi-cozumleri/"

TARGETS = [
    "gms-hb-12x3-gocmaksan-hasir-demir-bukme-makinasi",
    "gms-hb-12x6-gocmaksan-hasir-demir-bukme-makinasi",
    "gms-mh-8c-gocmaksan-hasir-kesme-makinasi",
]

REQ_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

VOLT_RE = re.compile(r"^(\d+)\s*V$", re.IGNORECASE)


def fetch_html(url):
    req = urllib.request.Request(url, headers=REQ_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  FETCH ERROR: {e}")
        return None


def parse_hb_mh(html):
    # Extract text-block-5 items in document order
    raw_items = re.findall(r'class="text-block-5"[^>]*>([^<]+)<', html)
    items = [unescape(t).strip() for t in raw_items if t.strip()]

    features = []
    voltage  = None

    for item in items:
        m = VOLT_RE.match(item)
        if m:
            voltage = m.group(1)
        else:
            features.append(item)

    specs = {}
    if features:
        specs["FEATURED FEATURES"] = features
    if voltage:
        specs["TECHNICAL DATA"] = {"Voltage V": voltage}

    return specs


def main():
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    index = {m["slug"]: i for i, m in enumerate(data)}

    print("=== HB-12x3 / HB-12x6 / MH-8C specs patch ===\n")

    for slug in TARGETS:
        url = SF_BASE + slug
        print(f"[{slug}]")
        html = fetch_html(url)
        if html is None:
            print("  SKIP\n")
            continue

        specs = parse_hb_mh(html)
        ff_n  = len(specs.get("FEATURED FEATURES", []))
        td    = specs.get("TECHNICAL DATA", {})
        print(f"  FEATURED FEATURES : {ff_n} item")
        for item in specs.get("FEATURED FEATURES", []):
            print(f"    - {item}")
        print(f"  TECHNICAL DATA    : {td}")

        if slug in index:
            data[index[slug]]["specs"] = specs
        time.sleep(0.5)

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\nJSON kaydedildi.\n")
    print("=== OZET ===")
    for slug in TARGETS:
        if slug not in index:
            continue
        s = data[index[slug]]["specs"]
        has = bool(s and any(v for v in s.values()))
        print(f"  [{'DOLU' if has else 'BOS '}] {slug}")


if __name__ == "__main__":
    main()
