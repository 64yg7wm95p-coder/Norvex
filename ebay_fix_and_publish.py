import os
import requests
from dotenv import load_dotenv

load_dotenv(".env", override=True)

TOKEN = os.getenv("EBAY_ACCESS_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Content-Language": "en-GB",
}

SKU = "TEST-SUPPLIERSCANNER-001"
OFFER_ID = "198817588011"
LOCATION_KEY = "TERA_UK"

# 1) Location bilgisini düzelt
location_url = f"https://api.ebay.com/sell/inventory/v1/location/{LOCATION_KEY}"

location_payload = {
    "name": "Tera Fulfilment UK",
    "merchantLocationStatus": "ENABLED",
    "locationTypes": ["WAREHOUSE"],
    "location": {
        "address": {
            "addressLine1": "1 Commercial Street",
            "city": "London",
            "postalCode": "E1 6AN",
            "country": "GB"
        }
    }
}

r1 = requests.post(location_url, headers=HEADERS, json=location_payload)
print("Location Status:", r1.status_code)
print(r1.text)

# 2) Inventory item bilgisini country/weight/size ile güçlendir
item_url = f"https://api.ebay.com/sell/inventory/v1/inventory_item/{SKU}"

item_payload = {
    "availability": {
        "shipToLocationAvailability": {
            "quantity": 1
        }
    },
    "condition": "NEW",
    "product": {
        "title": "SupplierScanner Test Product",
        "description": "This is a test product created by SupplierScanner Pro.",
        "brand": "Unbranded",
        "mpn": "TEST001"
    },
    "packageWeightAndSize": {
        "dimensions": {
            "height": 5,
            "length": 20,
            "width": 15,
            "unit": "CENTIMETER"
        },
        "weight": {
            "value": 1,
            "unit": "KILOGRAM"
        }
    }
}

r2 = requests.put(item_url, headers=HEADERS, json=item_payload)
print("Item Status:", r2.status_code)
print(r2.text)

# 3) Offer publish et
publish_url = f"https://api.ebay.com/sell/inventory/v1/offer/{OFFER_ID}/publish"

r3 = requests.post(publish_url, headers=HEADERS)
print("Publish Status:", r3.status_code)
print(r3.text)