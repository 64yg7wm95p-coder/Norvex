import os
import urllib.parse
from dotenv import load_dotenv

load_dotenv(".env", override=True)

client_id = os.getenv("EBAY_CLIENT_ID")
runame = os.getenv("EBAY_RUNAME")

scopes = [
    "https://api.ebay.com/oauth/api_scope",
    "https://api.ebay.com/oauth/api_scope/sell.inventory",
    "https://api.ebay.com/oauth/api_scope/sell.account",
    "https://api.ebay.com/oauth/api_scope/sell.fulfillment",
]

url = (
    "https://auth.ebay.com/oauth2/authorize?"
    + urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": runame,
        "response_type": "code",
        "scope": " ".join(scopes),
    })
)

print(url)