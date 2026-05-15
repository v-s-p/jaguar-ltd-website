"""
Gocmaksan Steel Factory (8) + Hand Tools (6) specs parser.
Only touches these 14 machines — leaves the other 33 untouched.

Steel Factory reality: all SF URLs serve the same HTML with 5 spec blocks.
HB-12x3, HB-12x6, MH-8C have no spec data on site → kept empty.
"""

import json, re, time
import urllib.request

DATA_PATH = r"C:\Users\Kenan\Desktop\AI\Jaguar-ltd\src\data\gocmaksan.json"

SF_URL  = "https://www.gocmaksan.com/eng/demir-tesisi-cozumleri/gms-axis-50s-gocmaksan-spiral-demir-bukme-makinasi"
HT_BASE = "https://www.gocmaksan.com/eng/insaatci-el-aletleri/"

STEEL_FACTORY = [
    "gms-axis-50s-gocmaksan-spiral-demir-bukme-makinasi",
    "gms-hb-12x3-gocmaksan-hasir-demir-bukme-makinasi",
    "gms-hb-12x6-gocmaksan-hasir-demir-bukme-makinasi",
    "gms-matrix-55-gocmaksan-demir-demir-kesme-hatti",
    "gms-matrix-55s-gocmaksan-demir-kesme-hatti",
    "gms-mh-8c-gocmaksan-hasir-kesme-makinasi",
    "gms-sls-12-gocmaksan-otomatik-etriye-bukme-makinasi",
    "gms-synclone-45s-gocmaksan-demir-bukme-hatti",
]
HAND_TOOLS = [
    "gms-ayarli-kosebentler-gocmaksan",
    "gms-demirci-anahtarlari-gocmaksan",
    "gms-el-makaslari-gocmaksan",
    "gms-etriye-kollari-gocmaksan",
    "gms-kalip-sokmeler-gocmaksan",
    "gms-oturak-makaslari-gocmaksan",
]

REQ_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

ITEM_PATTERN = re.compile(
    r'class="paragraph-ba-l-k"[^>]*>(?:<[^>]+>)*([^<]+)|'
    r'class="paragraph-25"[^>]*>([^<]+)'
)


def fetch_html(url):
    req = urllib.request.Request(url, headers=REQ_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  FETCH ERROR: {e}")
        return None


def extract_items(html):
    """Return ordered list of (type, value): type is 'HEADER' or 'DATA'."""
    items = []
    for m in ITEM_PATTERN.finditer(html):
        if m.group(1):
            items.append(("HEADER", m.group(1).strip()))
        else:
            items.append(("DATA", m.group(2).strip()))
    return items


def pairs_to_dict(data_items):
    """Convert [label, value, label, value...] to {label: value}."""
    d = {}
    it = iter(data_items)
    for label in it:
        try:
            value = next(it)
            d[label] = value
        except StopIteration:
            break
    return d


def pairs_to_list(data_items):
    """Convert [a, b, a, b...] to ['a: b', ...]."""
    result = []
    it = iter(data_items)
    for a in it:
        try:
            b = next(it)
            result.append(f"{a}: {b}")
        except StopIteration:
            result.append(a)
    return result


def build_sections(items):
    """Split items into sections keyed by header text."""
    sections = {}
    current_header = None
    for typ, val in items:
        if typ == "HEADER":
            current_header = val
            sections[current_header] = []
        elif current_header is not None:
            sections[current_header].append(val)
    return sections


# ── Section header → slug mapping ────────────────────────────────────────────
# key = substring of header (case-insensitive), value = slug
SF_HEADER_MAP = {
    "axis 50s":      "gms-axis-50s-gocmaksan-spiral-demir-bukme-makinasi",
    "sls 12":        "gms-sls-12-gocmaksan-otomatik-etriye-bukme-makinasi",
    "matrix 55s":    "gms-matrix-55s-gocmaksan-demir-kesme-hatti",
    "matrix 55":     "gms-matrix-55-gocmaksan-demir-demir-kesme-hatti",
    "synclone 45s":  "gms-synclone-45s-gocmaksan-demir-bukme-hatti",
}

# Which header is a CAPACITY section for which slug
SF_CAPACITY_ORDER = [
    # (capacity_header_keyword, preceding_spec_header_keyword)
    ("capacity",          "axis 50s"),
    ("cutting capacities","matrix 55"),
    ("bending capacities","synclone 45s"),
]

APPARATUS_FOR = "gms-sls-12-gocmaksan-otomatik-etriye-bukme-makinasi"


def parse_steel_factory_page():
    """Fetch SF page once, return {slug: specs_dict}."""
    print(f"  Fetching: {SF_URL}")
    html = fetch_html(SF_URL)
    if html is None:
        return {}

    items   = extract_items(html)
    sections = build_sections(items)

    result = {slug: {"FEATURED FEATURES": [], "TECHNICAL DATA": {}, "CAPACITIES": []}
              for slug in STEEL_FACTORY}

    # Map SPECIFICATIONS / TECHNICAL DATA sections
    for header, data in sections.items():
        h_lower = header.lower()
        matched = None
        for keyword, slug in SF_HEADER_MAP.items():
            if keyword in h_lower:
                matched = slug
                break
        if matched and ("specification" in h_lower or "technical" in h_lower):
            result[matched]["TECHNICAL DATA"] = pairs_to_dict(data)

    # Map CAPACITY sections — assign to the slug that precedes them in order
    header_list = list(sections.keys())
    for cap_kw, spec_kw in SF_CAPACITY_ORDER:
        cap_idx = next((i for i, h in enumerate(header_list) if cap_kw in h.lower()), None)
        if cap_idx is None:
            continue
        # Find the spec section before this capacity section
        matched_slug = None
        for h in reversed(header_list[:cap_idx]):
            for keyword, slug in SF_HEADER_MAP.items():
                if keyword in h.lower():
                    matched_slug = slug
                    break
            if matched_slug:
                break
        if matched_slug:
            cap_header = header_list[cap_idx]
            data = sections[cap_header]
            result[matched_slug]["CAPACITIES"] = pairs_to_list(data)

    # Map APPARATUS SUPPLIED WITH THE MACHINE → SLS 12
    for header, data in sections.items():
        if "apparatus supplied" in header.lower():
            result[APPARATUS_FOR]["SUPPLIED EQUIPMENT"] = pairs_to_list(data)

    # Remove empty keys
    for slug in STEEL_FACTORY:
        s = result[slug]
        if not s.get("FEATURED FEATURES"):
            del s["FEATURED FEATURES"]
        if not s.get("TECHNICAL DATA"):
            del s["TECHNICAL DATA"]
        if not s.get("CAPACITIES"):
            del s["CAPACITIES"]

    return result


def parse_hand_tools():
    result = {}
    for slug in HAND_TOOLS:
        url = HT_BASE + slug
        print(f"  Fetching: {url}")
        html = fetch_html(url)
        if html is None:
            result[slug] = {}
            continue
        m = re.search(r'[Cc]apacity\s*[:\-]\s*([^\n<]+)', html)
        if m:
            cap_val = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            result[slug] = {"CAPACITY": [cap_val]}
            print(f"    CAPACITY: {cap_val}")
        else:
            result[slug] = {}
            print(f"    CAPACITY: not found")
        time.sleep(0.5)
    return result


def main():
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    index = {m["slug"]: i for i, m in enumerate(data)}

    print("\n=== STEEL FACTORY (8) — single fetch ===")
    sf_specs = parse_steel_factory_page()

    print("\n=== HAND TOOLS (6) ===")
    ht_specs = parse_hand_tools()

    all_specs = {**sf_specs, **ht_specs}

    patched = 0
    for slug, specs in all_specs.items():
        if slug in index:
            data[index[slug]]["specs"] = specs
            patched += 1

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nJSON kaydedildi — {patched}/14 makine guncellendi")

    print("\n=== OZET ===")
    dolu = 0
    for slug in STEEL_FACTORY + HAND_TOOLS:
        if slug not in index:
            print(f"  [???? ] {slug} (JSON'da yok)")
            continue
        s = data[index[slug]]["specs"]
        has = bool(s and any(v for v in s.values()))
        if has:
            dolu += 1
        print(f"  [{'DOLU' if has else 'BOS '}] {slug}")
        if has:
            for k, v in s.items():
                cnt = len(v) if isinstance(v, (list, dict)) else "?"
                print(f"         {k}: {cnt} item")
    print(f"\nSonuc: {dolu}/14 specs dolu.")
    if dolu < 14:
        print(f"  NOT: HB-12x3, HB-12x6, MH-8C icin sitede specs bulunmuyor.")


if __name__ == "__main__":
    main()
