import os
import requests
from dotenv import load_dotenv

load_dotenv(".env", override=True)

TOKEN = os.getenv("EBAY_ACCESS_TOKEN")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Content-Language": "en-GB"
}

url = "https://api.ebay.com/sell/inventory/v1/offer"

payload = {
    "sku": "TEST-SUPPLIERSCANNER-001",
    "marketplaceId": "EBAY_GB",
    "format": "FIXED_PRICE",
    "availableQuantity": 1,

    "pricingSummary": {
        "price": {
            "value": "19.99",
            "currency": "GBP"
        }
    },

    "listingPolicies": {
        "fulfillmentPolicyId": "246605969024",
        "paymentPolicyId": "246606207024",
        "returnPolicyId": "246605957024"
    }
}

response = requests.post(
    url,
    headers=headers,
    json=payload
)

print("Status:", response.status_code)
print(response.text)