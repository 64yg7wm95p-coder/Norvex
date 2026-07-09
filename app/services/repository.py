from ..database import get_db_connection
from ..core import UniversalProduct


def clear_user_products(user_id: int):
    conn = get_db_connection()

    conn.execute(
        "DELETE FROM products WHERE user_id = ?",
        (user_id,)
    )

    conn.commit()
    conn.close()


def save_product(user_id: int, product: UniversalProduct):
    conn = get_db_connection()

    conn.execute(
        """
        INSERT INTO products (
            user_id,
            shopify_product_id,
            title,
            original_title,
            body_html,
            cost_price,
            ebay_price,
            additional_images,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            product.source_product_id,
            product.title,
            product.original_title,
            product.description,
            product.cost_price,
            product.target_price,
            ",".join(product.images),
            product.status
        )
    )

    conn.commit()
    conn.close()