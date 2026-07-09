import os
import requests
from dotenv import load_dotenv

load_dotenv(".env", override=True)

TOKEN = os.getenv("EBAY_ACCESS_TOKEN")

OFFER_ID = "198817588011"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Content-Language": "en-GB"
}

url = f"https://api.ebay.com/sell/inventory/v1/offer/{OFFER_ID}/publish"

response = requests.post(url, headers=headers)

print("Status:", response.status_code)
print(response.text)