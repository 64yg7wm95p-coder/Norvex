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

types = ["fulfillment_policy", "payment_policy", "return_policy"]

for policy_type in types:
    url = f"https://api.ebay.com/sell/account/v1/{policy_type}?marketplace_id=EBAY_GB"
    response = requests.get(url, headers=headers)

    print("\n", policy_type)
    print("Status:", response.status_code)
    print(response.text)