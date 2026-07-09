from .status import set_scan_status
from .shopify import fetch_shopify_products
from .repository import clear_user_products, save_product
from .product_parser import extract_product_data
from ..core import ProductPipeline


def run_shopify_scan(site_url: str, limit: int, user_id: int = 1):
    set_scan_status(True, 0, limit, "Tarama başlatıldı...", "info")

    try:
        clear_user_products(user_id)

        raw_products = fetch_shopify_products(site_url, limit)

        set_scan_status(
            True,
            0,
            len(raw_products),
            f"{len(raw_products)} ürün bulundu.",
            "info"
        )

        if not raw_products:
            set_scan_status(False, 0, 0, "Ürün bulunamadı.", "error")
            return

        pipeline = ProductPipeline()

        for index, raw_product in enumerate(raw_products, 1):
            product = extract_product_data(raw_product)
            product = pipeline.process(product)
            save_product(user_id, product)

            set_scan_status(
                True,
                index,
                len(raw_products),
                f"Kaydedildi: {product.title}",
                "info"
            )

        set_scan_status(
            False,
            len(raw_products),
            len(raw_products),
            "Tarama tamamlandı.",
            "success"
        )

    except Exception as error:
        set_scan_status(
            False,
            0,
            0,
            f"Scanner hata: {error}",
            "error"
        )