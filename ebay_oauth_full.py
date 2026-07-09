import os
import base64
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv(".env", override=True)

client_id = os.getenv("EBAY_CLIENT_ID")
client_secret = os.getenv("EBAY_CLIENT_SECRET")
runame = os.getenv("EBAY_RUNAME")

scopes = [
    "https://api.ebay.com/oauth/api_scope",
    "https://api.ebay.com/oauth/api_scope/sell.inventory",
    "https://api.ebay.com/oauth/api_scope/sell.account",
    "https://api.ebay.com/oauth/api_scope/sell.fulfillment",
]

params = {
    "client_id": client_id,
    "redirect_uri": runame,
    "response_type": "code",
    "scope": " ".join(scopes),
}

auth_url = "https://auth.ebay.com/oauth2/authorize?" + urllib.parse.urlencode(params)

print("\nBU URL'YI CHROME'A YAPISTIR:\n")
print(auth_url)

returned_url = input("\nAgree and Continue sonrasi gelen TAM URL'yi buraya yapistir: ").strip()

parsed = urllib.parse.urlparse(returned_url)
query = urllib.parse.parse_qs(parsed.query)

code = query.get("code", [None])[0]

if not code:
    print("Code bulunamadi.")
    print(returned_url)
    raise SystemExit

credentials = f"{client_id}:{client_secret}"
basic_auth = base64.b64encode(credentials.encode()).decode()

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Basic {basic_auth}",
}

data = {
    "grant_type": "authorization_code",
    "code": code,
    "redirect_uri": runame,
}

response = requests.post(
    "https://api.ebay.com/identity/v1/oauth2/token",
    headers=headers,
    data=data
)

print("Status:", response.status_code)
print(response.text)
if response.status_code == 200:
    tokens = response.json()

    with open(".env", "a", encoding="utf-8") as f:
        f.write("\nEBAY_ACCESS_TOKEN=" + tokens["access_token"])
        f.write("\nEBAY_REFRESH_TOKEN=" + tokens["refresh_token"])

    print("✅ Tokenlar .env dosyasına kaydedildi.")
else:
    print("❌ Token alınamadı.")