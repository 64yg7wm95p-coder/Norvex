import os
import requests
from dotenv import load_dotenv

load_dotenv(".env", override=True)

TOKEN = os.getenv("EBAY_ACCESS_TOKEN")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Content-Language": "en-GB",
}

SKU = "TEST-SUPPLIERSCANNER-001"

url = f"https://api.ebay.com/sell/inventory/v1/inventory_item/{SKU}"

payload = {
    "availability": {
        "shipToLocationAvailability": {
            "quantity": 1
        }
    },
    "condition": "NEW",
    "product": {
        "title": "Round Neck Basic Sweatshirt",
        "description": "Round Neck Basic Sweatshirt from Addax.",
        "brand": "Addax",
        "mpn": "TEST001",
        "aspects": {
            "Department": ["Women"],
            "Style": ["Sweatshirt"]
        },
        "imageUrls": [
            "https://addax.co.uk/cdn/shop/files/ADX-00037638211-6.jpg?v=1782977455&width=990"
        ]
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

response = requests.put(url, headers=headers, json=payload)

print("Item Status:", response.status_code)
print(response.text)