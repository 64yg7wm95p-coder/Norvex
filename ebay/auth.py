import os
import base64
import requests
import datetime
from dotenv import load_dotenv

# Bir üst dizindeki database.py'a erişim
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# ARTIK UserToken YOK; Yerine saf SQLite3 fonksiyonlarımızı çağırıyoruz!
from database import encrypt_token, decrypt_token, log_action, save_user_token, get_user_token

load_dotenv()

CLIENT_ID = os.getenv("EBAY_CLIENT_ID")
CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("EBAY_REDIRECT_URI")

EBAY_OAUTH_URL = "https://api.ebay.com/identity/v1/oauth2/token"

def get_auth_header() -> str:
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError("KRİTİK HATA: EBAY_CLIENT_ID veya EBAY_CLIENT_SECRET bulunamadı!")
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    return base64.b64encode(auth_str.encode()).decode()

def generate_ebay_auth_url() -> str:
    scopes = (
        "https://api.ebay.com/oauth/api_scope "
        "https://api.ebay.com/oauth/api_scope/sell.inventory "
        "https://api.ebay.com/oauth/api_scope/sell.account"
    )
    from urllib.parse import quote
    encoded_scopes = quote(scopes)
    url = f"https://auth.ebay.com/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={encoded_scopes}"
    return url

def handle_ebay_callback(user_id: int, code: str) -> bool:
    """SaaS Callback mekanizması: Kodu alır, şifreler ve SQLite3'e yazar."""
    headers = {
        "Authorization": f"Basic {get_auth_header()}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    
    response = requests.post(EBAY_OAUTH_URL, headers=headers, data=data)
    if response.status_code != 200:
        return False
        
    res_data = response.json()
    refresh_token = res_data.get("refresh_token")
    
    # SQLite3 uyumlu şifreli kayıt
    encrypted_rf = encrypt_token(refresh_token)
    save_user_token(user_id, encrypted_rf)
    return True

def get_valid_access_token(db_session_or_none, user_id: int) -> str:
    """
    Kullanıcının şifreli refresh token'ını çözer ve canlı access token alır.
    Geriye dönük uyumluluk için ilk parametreyi boş bırakabiliriz (Göz ardı edilir).
    """
    # SQLite3 fonksiyonumuzla şifreli token'ı doğrudan çekiyoruz
    encrypted_token = get_user_token(user_id)
    if not encrypted_token:
        raise ValueError(f"Bu kullanıcıya ({user_id}) ait bağlı bir eBay hesabı bulunamadı!")
        
    decrypted_refresh_token = decrypt_token(encrypted_token)
    
    headers = {
        "Authorization": f"Basic {get_auth_header()}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": decrypted_refresh_token,
        "scope": "https://api.ebay.com/oauth/api_scope https://api.ebay.com/oauth/api_scope/sell.inventory https://api.ebay.com/oauth/api_scope/sell.account",
    }

    response = requests.post(EBAY_OAUTH_URL, headers=headers, data=data)
    if response.status_code != 200:
        raise ValueError(f"eBay token yenilenemedi: {response.text}")

    return response.json()["access_token"]