import os
import requests
import json
from sqlalchemy.orm import Session

# Modüler dizin erişimi
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import log_action
from ebay.auth import get_valid_access_token

EBAY_API_BASE = "https://api.ebay.com/sell/inventory/v1"

def create_or_check_offer(db: Session, user_id: int, product_data: dict, category_id: str) -> str:
    """
    Kullanıcı bazlı (user_id) olarak eBay üzerinde ürün için bir teklif (Offer) oluşturur.
    Eğer ürünün zaten aktif bir Offer'ı varsa, terminalde aldığın hatayı engellemek için
    mevcut Offer ID'sini bulur ve geri döner.
    """
    try:
        access_token = get_valid_access_token(db, user_id)
    except Exception as e:
        log_action(db, user_id, "OFFER_AUTH_ERROR", f"Token alınamadı: {str(e)}")
        raise Exception(f"Offer için yetkilendirme başarısız: {e}")

    sku = product_data.get("sku")
    
    # 1. Önce Güvenlik: Bu SKU için eBay'de halihazırda bir offer var mı kontrol et (Terminal hatasını engeller)
    check_url = f"{EBAY_API_BASE}/offer?sku={sku}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    check_response = requests.get(check_url, headers=headers)
    if check_response.status_code == 200:
        res_json = check_response.json()
        if res_json.get("total", 0) > 0:
            existing_offer_id = res_json["offers"][0]["offerId"]
            print(f"[+] Mevcut Offer Bulundu (User {user_id}): {existing_offer_id}")
            return existing_offer_id

    # 2. Eğer Offer yoksa, yeni bir tane oluşturuyoruz (Payload Mimari)
    # Not: Burardaki Policy ID'ler kullanıcının kendi eBay hesabından SaaS panelinde eşlenecek.
    # Şimdilik senin çalışan test ID'lerini default olarak bırakıyoruz.
    payload = {
        "sku": sku,
        "marketplaceId": "EBAY_GB", # eBay UK
        "format": "FIXED_PRICE",
        "availableQuantity": int(product_data.get("stock_quantity", 5)),
        "pricingSummary": {
            "price": {
                "value": str(product_data.get("ebay_price")), # Örn: "9.61"
                "currency": "GBP"
            }
        },
        "listingPolicies": {
            "paymentPolicyId": os.getenv("EBAY_PAYMENT_POLICY_ID", "246606207024"),
            "returnPolicyId": os.getenv("EBAY_RETURN_POLICY_ID", "246605957024"),
            "fulfillmentPolicyId": os.getenv("EBAY_FULFILLMENT_POLICY_ID", "247135582024")
        },
        "categoryId": category_id if category_id else "155226", # Kadın Üst Giyim kategorisi
        "merchantLocationKey": os.getenv("EBAY_LOCATION_KEY", "TERA_UK"),
        "tax": {
            "applyTax": False
        },
        "listingDuration": "GTC" # Good 'Til Cancelled (İptal edilene kadar yayında kal)
    }

    url = f"{EBAY_API_BASE}/offer"
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    print(f"[*] Offer Status (User {user_id}): {response.status_code}")

    if response.status_code == 201:
        offer_id = response.json().get("offerId")
        log_action(db, user_id, "OFFER_CREATION_SUCCESS", f"SKU: {sku} için Offer {offer_id} oluşturuldu.")
        return offer_id
    else:
        log_action(db, user_id, "OFFER_CREATION_ERROR", f"SKU: {sku} için Offer oluşturulamadı.")
        print(f"❌ Offer Hatası: {response.text}")
        raise Exception(f"eBay Offer Oluşturulamadı: {response.text}")

if __name__ == "__main__":
    from database import SessionLocal
    db = SessionLocal()
    
    mock_product = {
        "sku": "SS-BOAT-NECK-RUCHED-T-SHIRT",
        "ebay_price": "9.61",
        "stock_quantity": 5
    }
    
    print("[*] Çok kullanıcılı Offer katmanı test ediliyor...")
    try:
        offer_id = create_or_check_offer(db, user_id=1, product_data=mock_product, category_id="155226")
        print(f"[+] Çıkan Sonuç: {offer_id}")
    except Exception as e:
        print(f"Test sonlandı: {e}")
        
    db.close()