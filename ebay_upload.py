import os
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv(".env", override=True)

TOKEN = os.getenv("EBAY_ACCESS_TOKEN")
CSV_FILE = "ebay_upload_ready.csv"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Content-Language": "en-GB",
}

df = pd.read_csv(CSV_FILE)
df = df.head(5)  # ilk test: sadece 1 ürün

for _, row in df.iterrows():
    sku = str(row["Custom label (SKU)"]).strip()
    title = str(row["*Title"]).strip()[:80]
    description = str(row["*Description"]).strip()
    brand = str(row.get("Brand", "Unbranded")).strip()
    quantity = int(row["*Quantity"])

    payload = {
        "availability": {
            "shipToLocationAvailability": {
                "quantity": quantity
            }
        },
        "condition": "NEW",
        "product": {
            "title": title,
            "description": description,
            "brand": brand,
            "mpn": sku
        }
    }

    url = f"https://api.ebay.com/sell/inventory/v1/inventory_item/{sku}"
    response = requests.put(url, headers=headers, json=payload)

    print("SKU:", sku)
    print("Status:", response.status_code)
    print(response.text)
    print("-" * 40)