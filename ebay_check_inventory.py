import os
import requests
from dotenv import load_dotenv

load_dotenv(".env", override=True)

headers = {
    "Authorization": f"Bearer {os.getenv('EBAY_ACCESS_TOKEN')}"
}

url = "https://api.ebay.com/sell/inventory/v1/inventory_item"

response = requests.get(url, headers=headers)

print("Status:", response.status_code)
print(response.text)