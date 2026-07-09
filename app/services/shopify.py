import json
import re
import time
from html import unescape
from urllib.parse import urljoin

import requests


HEADERS = {
    "User-Agent": "Mozilla/5.0 NorvexScanner/1.0",
    "Accept": "application/json,text/html,*/*",
}


def fetch_shopify_products(site_url: str, limit: int) -> list:
    base_url = site_url.rstrip("/")

    errors = []

    for method in (
        _from_products_json,
        _from_collection_json,
        _from_sitemap,
    ):
        try:
            products = method(base_url, limit)
            if products:
                return products[:limit]
        except Exception as e:
            errors.append(str(e))
            time.sleep(1)

    raise Exception(
        "Bu tedarikçi otomatik taranamadı. "
        + " | ".join(errors[:3])
    )


def _get(url: str):
    response = requests.get(url, headers=HEADERS, timeout=15)

    if response.status_code == 429:
        raise Exception("Tedarikçi geçici olarak çok fazla istek nedeniyle engelledi.")

    if response.status_code >= 400:
        raise Exception(f"{url} HTTP {response.status_code}")

    return response


def _from_products_json(base_url: str, limit: int) -> list:
    url = f"{base_url}/products.json?limit={limit}"
    response = _get(url)
    return response.json().get("products", [])


def _from_collection_json(base_url: str, limit: int) -> list:
    url = f"{base_url}/collections/all/products.json?limit={limit}"
    response = _get(url)
    return response.json().get("products", [])


def _from_sitemap(base_url: str, limit: int) -> list:
    sitemap_url = f"{base_url}/sitemap_products_1.xml"
    response = _get(sitemap_url)

    urls = re.findall(r"<loc>(.*?)</loc>", response.text)
    product_urls = [u for u in urls if "/products/" in u][:limit]

    products = []

    for index, product_url in enumerate(product_urls, 1):
        html = _get(product_url).text

        title = _extract_meta(html, "og:title") or f"Product {index}"
        description = _extract_meta(html, "og:description") or ""
        image = _extract_meta(html, "og:image") or ""
        price = _extract_price(html)

        products.append({
            "id": f"sitemap_{index}",
            "title": unescape(title),
            "body_html": unescape(description),
            "variants": [{"price": str(price)}],
            "images": [{"src": image}] if image else [],
        })

    return products


def _extract_meta(html: str, property_name: str) -> str:
    patterns = [
        rf'<meta[^>]+property=["\']{property_name}["\'][^>]+content=["\']([^"\']+)["\']',
        rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']{property_name}["\']',
    ]

    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return ""


def _extract_price(html: str) -> float:
    json_ld_blocks = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.DOTALL | re.IGNORECASE,
    )

    for block in json_ld_blocks:
        try:
            data = json.loads(block.strip())

            if isinstance(data, dict):
                offers = data.get("offers")
                if isinstance(offers, dict) and offers.get("price"):
                    return float(offers["price"])
                if isinstance(offers, list) and offers and offers[0].get("price"):
                    return float(offers[0]["price"])

        except Exception:
            pass

    match = re.search(r'"price"\s*:\s*"?([0-9]+(?:\.[0-9]+)?)"?', html)
    if match:
        return float(match.group(1))

    return 0.0