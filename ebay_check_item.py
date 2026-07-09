import os
import json
import requests
from dotenv import load_dotenv

load_dotenv(".env", override=True)

TOKEN = os.getenv("EBAY_ACCESS_TOKEN")
SKU = "TEST-SUPPLIERSCANNER-001"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Content-Language": "en-GB"
}

url = f"https://api.ebay.com/sell/inventory/v1/inventory_item/{SKU}"

response = requests.get(url, headers=headers)

print("Status:", response.status_code)

data = response.json()
print(json.dumps(data, indent=4))

print("\nIMAGE URLS:")
print(data.get("product", {}).get("imageUrls"))