from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "src" / "data" / "gocmaksan.json"
CATALOG_DIR = PROJECT_ROOT / "public" / "catalogs" / "gocmaksan"
BASE_URL = "https://www.gocmaksan.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/136.0.0.0 Safari/537.36"
    )
}

CATEGORY_PATHS = {
    "Bending Machines": ["eng/bukme-makinalari", "tr/bukme-makinalari"],
    "Light Construction": ["eng/hafif-insaat-makinalari", "tr/hafif-insaat-makinalari"],
    "Hand Tools": [
        "eng/el-aletleri",
        "tr/el-aletleri",
        "eng/insaatci-el-aletleri",
        "tr/insaatci-el-aletleri",
        "eng/builder-hand-tools",
        "tr/insaatci-el-aletleri",
        "eng/hand-tools",
        "tr/hand-tools",
    ],
}

MANUAL_URLS = {
    "gms-bs-45-gocmaksan-insaat-demiri-bukme-makinasi-sy0wu": [
        "https://www.gocmaksan.com/tr/bukme-makinalari/gms-bs-45-gocmaksan-insaat-demiri-bukme-makinasi",
        "https://www.gocmaksan.com/eng/bukme-makinalari/gms-bs-45-gocmaksan-insaat-demiri-bukme-makinasi-sy0wu",
    ],
    "gms-kompaktor": [
        "https://www.gocmaksan.com/eng/hafif-insaat-makinalari/gms-kompaktor",
        "https://www.gocmaksan.com/tr/hafif-insaat-makinalari/gms-kompaktor",
    ],
    "gms-rl-2000-gocmaksan-cift-tamburlu-silindir": [
        "https://www.gocmaksan.com/tr/hafif-insaat-makinalari/gms-rl-2000-gocmaksan-cift-tamburlu-silindir",
        "https://www.gocmaksan.com/eng/hafif-insaat-makinalari/gms-rl-2000-gocmaksan-cift-tamburlu-silindir",
    ],
}

PDF_RE = re.compile(r"https?://[^\"'>\s]+\.pdf(?:\?[^\"'>\s]+)?|/[^\"'>\s]+\.pdf(?:\?[^\"'>\s]+)?", re.I)


def new_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(HEADERS)
    session.trust_env = False
    return session


def load_missing_machines() -> list[dict[str, Any]]:
    machines = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    missing: list[dict[str, Any]] = []
    for machine in machines:
        if machine.get("pdf_catalog"):
            continue
        slug_pdf = CATALOG_DIR / f"{machine['slug']}.pdf"
        if not slug_pdf.exists():
            missing.append(machine)
    return missing


def is_internal(url: str) -> bool:
    parsed = urlparse(url)
    return not parsed.netloc or parsed.netloc.endswith("gocmaksan.com")


def absolutize(url: str) -> str:
    return urljoin(BASE_URL, url)


def fetch_html(session: requests.Session, url: str) -> str | None:
    try:
        response = session.get(url, timeout=30)
        if response.ok and "text/html" in response.headers.get("content-type", ""):
            return response.text
    except requests.RequestException:
        return None
    return None


def parse_links(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []
    for anchor in soup.select("a[href]"):
        href = anchor.get("href", "").strip()
        if not href:
            continue
        links.append(absolutize(href))
    return links


def discover_product_urls(session: requests.Session, machine: dict[str, Any]) -> list[str]:
    slug = machine["slug"]
    candidates: list[str] = []

    candidates.extend(MANUAL_URLS.get(slug, []))

    for category in machine.get("categories", []):
        for prefix in CATEGORY_PATHS.get(category, []):
            candidates.append(f"{BASE_URL}/{prefix}/{slug}")

    for search_url in [
        f"{BASE_URL}/?s={quote_plus(slug)}",
        f"{BASE_URL}/eng/?s={quote_plus(slug)}",
        f"{BASE_URL}/tr/?s={quote_plus(slug)}",
    ]:
        html = fetch_html(session, search_url)
        if not html:
            continue
        for link in parse_links(html):
            if slug in link and is_internal(link):
                candidates.append(link)

    seen: set[str] = set()
    deduped: list[str] = []
    for url in candidates:
        if url not in seen:
            seen.add(url)
            deduped.append(url)
    return deduped


def find_pdf_links(page_url: str, html: str) -> list[str]:
    links: list[str] = []
    soup = BeautifulSoup(html, "html.parser")
    for anchor in soup.select("a[href]"):
        href = anchor.get("href", "").strip()
        if ".pdf" not in href.lower():
            continue
        links.append(urljoin(page_url, href))

    for match in PDF_RE.findall(html):
        links.append(urljoin(page_url, match))

    seen: set[str] = set()
    deduped: list[str] = []
    for link in links:
        clean = link.replace("&amp;", "&")
        if clean not in seen:
            seen.add(clean)
            deduped.append(clean)
    return deduped


def download_pdf(session: requests.Session, pdf_url: str, target: Path) -> tuple[bool, str]:
    try:
        response = session.get(pdf_url, timeout=60)
        response.raise_for_status()
    except requests.RequestException as exc:
        return False, f"download failed: {exc}"

    content_type = response.headers.get("content-type", "")
    data = response.content
    if "pdf" not in content_type.lower() and not data.startswith(b"%PDF"):
        return False, f"not a pdf response ({content_type or 'unknown content-type'})"

    target.write_bytes(data)
    return True, f"saved {len(data)} bytes"


def main() -> None:
    session = new_session()
    missing = load_missing_machines()
    report: list[dict[str, Any]] = []

    for machine in missing:
        slug = machine["slug"]
        product_urls = discover_product_urls(session, machine)
        status = {
            "slug": slug,
            "product_urls_checked": len(product_urls),
            "resolved_product_url": None,
            "pdf_url": None,
            "saved_to": None,
            "result": "not_found",
            "note": "No product page or PDF link found.",
        }

        for product_url in product_urls:
            html = fetch_html(session, product_url)
            if not html:
                continue
            pdf_links = find_pdf_links(product_url, html)
            if not pdf_links:
                continue
            pdf_url = pdf_links[0]
            target = CATALOG_DIR / f"{slug}.pdf"
            ok, note = download_pdf(session, pdf_url, target)
            status["resolved_product_url"] = product_url
            status["pdf_url"] = pdf_url
            status["saved_to"] = str(target.relative_to(PROJECT_ROOT))
            status["result"] = "downloaded" if ok else "failed"
            status["note"] = note
            if ok:
                break

        report.append(status)

    downloaded = sum(1 for item in report if item["result"] == "downloaded")
    unresolved = sum(1 for item in report if item["result"] != "downloaded")
    print(
        json.dumps(
            {
                "missing_candidates": len(missing),
                "downloaded": downloaded,
                "unresolved": unresolved,
                "report": report,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
