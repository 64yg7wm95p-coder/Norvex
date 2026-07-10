import os
import re
from datetime import UTC, datetime
from html import unescape
from urllib.parse import quote

import requests
from fastapi import APIRouter, Depends, HTTPException

from ..auth.dependencies import get_current_user_from_cookie
from ..database import get_db_connection

router = APIRouter()

EBAY_API_BASE = "https://api.ebay.com/sell/inventory/v1"


def clean_sku(value: str) -> str:
    value = str(value or "").strip()
    value = re.sub(r"[^A-Za-z0-9_-]", "-", value)
    return value[:50]


def clean_text(value: str) -> str:
    value = unescape(str(value or ""))
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def get_ebay_token(user_id: int) -> str:
    conn = get_db_connection()

    row = conn.execute(
        """
        SELECT
            ebay_refresh_token,
            ebay_access_token,
            ebay_token_expires_at
        FROM users
        WHERE id = ?
        """,
        (user_id,),
    ).fetchone()

    conn.close()

    if not row or not row["ebay_refresh_token"]:
        raise HTTPException(
            status_code=400,
            detail="eBay hesabı bağlı değil.",
        )

    access_token = row["ebay_access_token"]
    expires_at = row["ebay_token_expires_at"]

    if access_token and expires_at:
        try:
            if datetime.fromisoformat(expires_at) > datetime.now(UTC):
                return access_token
        except ValueError:
            pass

    from ..services.ebay_service import refresh_access_token

    return refresh_access_token(
        user_id=user_id,
        refresh_token=row["ebay_refresh_token"],
    )


def ebay_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Content-Language": "en-GB",
        "Accept": "application/json",
    }


@router.get("/api/v1/ebay/connect")
def ebay_connect(
    current_user=Depends(get_current_user_from_cookie),
):
    client_id = os.getenv("EBAY_CLIENT_ID")
    redirect_uri = os.getenv("EBAY_REDIRECT_URI")

    if not client_id or not redirect_uri:
        raise HTTPException(
            status_code=500,
            detail="eBay OAuth ayarları eksik.",
        )

    auth_base = (
        "https://auth.sandbox.ebay.com"
        if os.getenv("EBAY_ENV", "").lower() == "sandbox"
        else "https://auth.ebay.com"
    )

    encoded_redirect_uri = quote(redirect_uri, safe="")
    encoded_scope = quote("https://api.ebay.com/oauth/api_scope", safe="")

    url = (
        f"{auth_base}/oauth2/authorize"
        f"?client_id={client_id}"
        "&response_type=code"
        f"&redirect_uri={encoded_redirect_uri}"
        f"&scope={encoded_scope}"
    )

    return {
        "success": True,
        "user_id": current_user["id"],
        "connect_url": url,
    }


@router.get("/api/v1/ebay/callback")
def ebay_callback(
    code: str,
    current_user=Depends(get_current_user_from_cookie),
):
    from ..services.ebay_service import exchange_code_for_token

    # Query-string ayrıştırması sırasında "+" karakterleri
    # boşluğa dönüşmüşse eBay authorization code'unu düzelt.
    normalized_code = code.replace(" ", "+")

    exchange_code_for_token(
        current_user["id"],
        normalized_code,
    )

    return {
        "success": True,
        "message": "eBay hesabı bağlandı.",
    }

    return {
        "success": True,
        "message": "eBay hesabı bağlandı.",
    }


@router.post("/api/v1/ebay/list")
def ebay_list(
    shopify_id: str,
    current_user=Depends(get_current_user_from_cookie),
):
    user_id = current_user["id"]
    token = get_ebay_token(user_id)
    headers = ebay_headers(token)

    conn = get_db_connection()

    product = conn.execute(
        """
        SELECT *
        FROM products
        WHERE user_id = ?
          AND shopify_product_id = ?
        LIMIT 1
        """,
        (user_id, shopify_id),
    ).fetchone()

    if not product:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Ürün bulunamadı.",
        )

    sku = clean_sku(
        product["shopify_product_id"]
        or product["source_product_id"]
        or product["id"]
    )
    title = clean_text(product["title"] or product["original_title"])[:80]
    description = clean_text(product["body_html"] or title)

    price = product["ebay_price"] or product["cost_price"]
    if not price:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Üründe eBay fiyatı bulunamadı.",
        )

    image_urls = []
    if product["additional_images"]:
        image_urls = [
            img.strip()
            for img in str(product["additional_images"]).split(",")
            if img.strip().startswith("http")
        ]

    inventory_payload = {
        "availability": {
            "shipToLocationAvailability": {
                "quantity": 1
            }
        },
        "condition": "NEW",
        "product": {
            "title": title,
            "description": description,
            "brand": "Unbranded",
            "mpn": sku,
        },
        "packageWeightAndSize": {
            "dimensions": {
                "height": 5,
                "length": 20,
                "width": 15,
                "unit": "CENTIMETER",
            },
            "weight": {
                "value": 1,
                "unit": "KILOGRAM",
            },
        },
    }

    if image_urls:
        inventory_payload["product"]["imageUrls"] = image_urls[:12]

    inventory_url = f"{EBAY_API_BASE}/inventory_item/{sku}"
    inventory_response = requests.put(
        inventory_url,
        headers=headers,
        json=inventory_payload,
        timeout=30,
    )

    if inventory_response.status_code not in (200, 201, 204):
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"eBay inventory oluşturulamadı: {inventory_response.text}",
        )

    offer_id = None

    check_offer_response = requests.get(
        f"{EBAY_API_BASE}/offer?sku={sku}",
        headers=headers,
        timeout=30,
    )

    if check_offer_response.status_code == 200:
        data = check_offer_response.json()
        offers = data.get("offers") or []
        if offers:
            offer_id = offers[0].get("offerId")

    if not offer_id:
        offer_payload = {
            "sku": sku,
            "marketplaceId": "EBAY_GB",
            "format": "FIXED_PRICE",
            "availableQuantity": 1,
            "categoryId": os.getenv("EBAY_CATEGORY_ID", "11554"),
            "merchantLocationKey": os.getenv("EBAY_LOCATION_KEY", "TERA_UK"),
            "listingDescription": description,
            "pricingSummary": {
                "price": {
                    "value": str(price),
                    "currency": "GBP",
                }
            },
            "listingPolicies": {
                "fulfillmentPolicyId": os.getenv(
                    "EBAY_FULFILLMENT_POLICY_ID",
                    "246605969024",
                ),
                "paymentPolicyId": os.getenv(
                    "EBAY_PAYMENT_POLICY_ID",
                    "246606207024",
                ),
                "returnPolicyId": os.getenv(
                    "EBAY_RETURN_POLICY_ID",
                    "246605957024",
                ),
            },
        }

        offer_response = requests.post(
            f"{EBAY_API_BASE}/offer",
            headers=headers,
            json=offer_payload,
            timeout=30,
        )

        if offer_response.status_code != 201:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail=f"eBay offer oluşturulamadı: {offer_response.text}",
            )

        offer_id = offer_response.json().get("offerId")

    publish_response = requests.post(
        f"{EBAY_API_BASE}/offer/{offer_id}/publish",
        headers=headers,
        timeout=30,
    )

    if publish_response.status_code != 200:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"eBay publish başarısız: {publish_response.text}",
        )

    listing_id = publish_response.json().get("listingId")

    conn.execute(
        """
        UPDATE products
        SET target_listing_id = ?,
            status = ?
        WHERE id = ?
        """,
        (
            listing_id,
            "eBay Published",
            product["id"],
        ),
    )
    conn.commit()
    conn.close()

    return {
        "success": True,
        "user_id": user_id,
        "shopify_id": shopify_id,
        "sku": sku,
        "offer_id": offer_id,
        "ebay_id": listing_id,
    }