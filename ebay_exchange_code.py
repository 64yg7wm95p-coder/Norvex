import os
import base64
import urllib.parse
import requests
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv(".env", override=True)

# Bilgileri oku
client_id = os.getenv("EBAY_CLIENT_ID")
client_secret = os.getenv("EBAY_CLIENT_SECRET")
runame = os.getenv("EBAY_RUNAME")
auth_code = os.getenv("EBAY_AUTH_CODE")

# Authorization code URL encoded geldiyse çöz
auth_code = urllib.parse.unquote(auth_code)

# Basic Authentication oluştur
credentials = f"{client_id}:{client_secret}"
basic_auth = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

# eBay Token Endpoint
url = "https://api.ebay.com/identity/v1/oauth2/token"

headers = {
    "Authorization": f"Basic {basic_auth}",
    "Content-Type": "application/x-www-form-urlencoded",
}

payload = {
    "grant_type": "authorization_code",
    "code": auth_code,
    "redirect_uri": runame,
}

# İstek gönder
response = requests.post(url, headers=headers, data=payload)

print("Status Code:", response.status_code)
print(response.text)
import json

tokens = response.json()

print("\nACCESS TOKEN:\n")
print(tokens["access_token"])

print("\nREFRESH TOKEN:\n")
print(tokens["refresh_token"])