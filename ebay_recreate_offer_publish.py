import os
import requests
from dotenv import load_dotenv

load_dotenv(".env", override=True)

TOKEN = os.getenv("EBAY_ACCESS_TOKEN")

SKU = "TEST-SUPPLIERSCANNER-001"
LOCATION_KEY = "TERA_UK"

FULFILLMENT_POLICY = "246605969024"
PAYMENT_POLICY = "246606207024"
RETURN_POLICY = "246605957024"

CATEGORY_ID = "11554"  # Women's Clothing > Trousers

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Content-Language": "en-GB"
}

print("1) Eski offer aranıyor...")

r = requests.get(
    f"https://api.ebay.com/sell/inventory/v1/offer?sku={SKU}",
    headers=headers,
)

offer_id = None

if r.status_code == 200:
    data = r.json()
    if data.get("offers"):
        offer_id = data["offers"][0]["offerId"]

if offer_id:
    print("Eski offer bulundu:", offer_id)

    d = requests.delete(
        f"https://api.ebay.com/sell/inventory/v1/offer/{offer_id}",
        headers=headers,
    )

    print("Delete Status:", d.status_code)
else:
    print("Eski offer bulunamadı.")

print("\n2) Yeni offer oluşturuluyor...")

payload = {
    "sku": SKU,
    "marketplaceId": "EBAY_GB",
    "format": "FIXED_PRICE",
    "availableQuantity": 1,
    "categoryId": CATEGORY_ID,
    "merchantLocationKey": LOCATION_KEY,
    "listingDescription": "SupplierScanner test product",
    "pricingSummary": {
        "price": {
            "value": "19.99",
            "currency": "GBP"
        }
    },
    "listingPolicies": {
        "fulfillmentPolicyId": FULFILLMENT_POLICY,
        "paymentPolicyId": PAYMENT_POLICY,
        "returnPolicyId": RETURN_POLICY
    }
}

r = requests.post(
    "https://api.ebay.com/sell/inventory/v1/offer",
    headers=headers,
    json=payload
)

print("Create Status:", r.status_code)
print(r.text)

if r.status_code != 201:
    raise SystemExit("Offer oluşturulamadı.")

offer_id = r.json()["offerId"]

print("\n3) Publish ediliyor...")
print("Yeni Offer ID:", offer_id)

r = requests.post(
    f"https://api.ebay.com/sell/inventory/v1/offer/{offer_id}/publish",
    headers=headers
)

print("Publish Status:", r.status_code)
print(r.text)