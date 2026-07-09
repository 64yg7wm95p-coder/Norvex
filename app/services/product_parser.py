from ..core import UniversalProduct


def extract_product_data(product: dict) -> UniversalProduct:
    original_title = product.get("title", "Unknown Product")
    shopify_id = str(product.get("id"))
    body_html = product.get("body_html") or ""

    variants = product.get("variants") or []
    cost_price = 0.0

    if variants:
        try:
            cost_price = float(variants[0].get("price", 0) or 0)
        except ValueError:
            cost_price = 0.0

    images = []

    for img in product.get("images", []):
        src = img.get("src") if isinstance(img, dict) else None

        if src and src not in images:
            images.append(src)

    return UniversalProduct(
        source="shopify",
        source_product_id=shopify_id,
        original_title=original_title,
        title=original_title,
        description=body_html,
        cost_price=cost_price,
        target_price=0.0,
        images=images,
        status="Hazır"
    )