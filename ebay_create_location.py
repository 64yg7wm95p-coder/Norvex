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

merchant_key = "TERA_UK"

url = f"https://api.ebay.com/sell/inventory/v1/location/{merchant_key}"

payload = {
    "location": {
        "address": {
            "addressLine1": "London",
            "city": "London",
            "postalCode": "E1 6AN",
            "country": "GB"
        }
    },
    "locationInstructions": "Main warehouse",
    "locationTypes": [
        "WAREHOUSE"
    ],
    "name": "Tera Fulfilment UK",
    "merchantLocationStatus": "ENABLED"
}

response = requests.post(url, headers=headers, json=payload)

print("Status:", response.status_code)
print(response.text)