import os
import requests
from dotenv import load_dotenv

load_dotenv(".env", override=True)

token = os.getenv("EBAY_ACCESS_TOKEN")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

url = "https://api.ebay.com/sell/inventory/v1/inventory_item"

response = requests.get(url, headers=headers)

print("Status:", response.status_code)
print(response.json())