import os
import requests
import json

# Üst dizin erişimi
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import log_action, get_connection
from ebay.auth import get_valid_access_token

EBAY_API_BASE = "https://api.ebay.com/sell/inventory/v1"

def sync_all_images_to_ebay_item(user_id: int, offer_id: str, access_token: str):
    """
    Kritik A+ Köprüsü: İlan yayınlanmadan hemen önce veritabanındaki 
    tüm çoklu resimleri çeker ve eBay'deki ilgili envanter kaydını günceller.
    """
    try:
        # 1. Teklif detaylarından ürünün 'sku' kodunu öğreniyoruz
        offer_url = f"{EBAY_API_BASE}/offer/{offer_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        offer_res = requests.get(offer_url, headers=headers)
        if offer_res.status_code != 200:
            return  # Teklif detayına erişilemezse sakince geç
            
        sku = offer_res.json().get("sku")
        if not sku:
            return

        # 2. Veritabanımızdan bu ürüne ait ana resmi ve çoklu resimleri çekiyoruz
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT image_url, additional_images FROM products WHERE offer_id = ? OR shopify_product_id = (SELECT shopify_product_id FROM products WHERE offer_id = ? ORDER BY id DESC LIMIT 1) LIMIT 1", (offer_id, offer_id))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return

        # Resim dizisini hazırlıyoruz
        all_images = []
        if row["image_url"]:
            all_images.append(row["image_url"])
            
        if row["additional_images"]:
            # Virgülle ayrılmış çoklu resimleri listeye geri çeviriyoruz
            extra_imgs = row["additional_images"].split(",")
            for img in extra_imgs:
                if img and img not in all_images:
                    all_images.append(img)

        if not all_images:
            return

        # 3. Canlı eBay Envanter Nesnesini Alıyoruz
        item_url = f"{EBAY_API_BASE}/inventory_item/{sku}"
        item_res = requests.get(item_url, headers=headers)
        if item_res.status_code != 200:
            return

        item_data = item_res.json()

        # 4. Envanter nesnesinin resim dizisini (imageUrls) yeni çoklu resimlerimizle aşılıyoruz
        if "product" not in item_data:
            item_data["product"] = {}
        
        item_data["product"]["imageUrls"] = all_images

        # 5. Güncellenmiş zengin envanteri eBay'e geri basıyoruz (PUT)
        requests.put(item_url, headers=headers, json=item_data)
        print(f"   [📸] {len(all_images)} adet çoklu resim eBay envanterine (SKU: {sku}) başarıyla senkronize edildi.")
        
    except Exception as e:
        print(f"   ⚠️ Çoklu resim senkronizasyon uyarısı: {e}")

def publish_ebay_offer(db_session_or_none, user_id: int, offer_id: str) -> str:
    """
    Belirtilen kullanıcıya (user_id) ait oluşturulmuş bir teklifi (Offer ID)
    eBay üzerinde resmi olarak canlı ilana (Listing) dönüştürür.
    Teklif yayına girmeden önce tüm çoklu resimleri otonom olarak senkronize eder.
    """
    try:
        # SQLite3 uyumlu yeni auth motorumuzdan RAM'de yaşayan token'ı alıyoruz
        access_token = get_valid_access_token(None, user_id)
    except Exception as e:
        log_action(user_id, "PUBLISH_AUTH_ERROR", f"Token alınamadı: {str(e)}")
        raise Exception(f"Yayınlama için yetkilendirme başarısız: {e}")

    # 🔥 CANLI YAYIN ÖNCESİ ÇOKLU RESİM BOMBASINI ATEŞLE
    sync_all_images_to_ebay_item(user_id, offer_id, access_token)

    url = f"{EBAY_API_BASE}/offer/{offer_id}/publish"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    print(f"[*] İlan Yayınlama Tetikleniyor (User {user_id}, Offer {offer_id})...")
    
    # eBay publish API'si gövdede (body) veri beklemez, boş post atılır
    response = requests.post(url, headers=headers)
    
    print(f"[*] Publish Status (User {user_id}): {response.status_code}")

    # 200 OK başarılı demektir ve içinde bize resmi eBay ilan numarasını (listingId) döner
    if response.status_code == 200:
        res_json = response.json()
        listing_id = res_json.get("listingId")
        log_action(user_id, "PUBLISH_SUCCESS", f"Offer {offer_id} başarıyla yayınlandı. İlan ID: {listing_id}")
        return listing_id
    else:
        # Eğer ilan zaten yayındaysa veya bir hata varsa logla
        log_action(user_id, "PUBLISH_ERROR", f"Offer {offer_id} yayınlanamadı: {response.text[:100]}")
        print(f"❌ Publish Hatası: {response.text}")
        raise Exception(f"eBay İlanı Yayınlanamadı: {response.text}")

if __name__ == "__main__":
    print("[*] Çok kullanıcılı Publish katmanı modüler testi...")
    try:
        listing_id = publish_ebay_offer(None, user_id=99, offer_id="199391507011")
        print(f"[+] Başarılı! Canlı İlan Numarası: {listing_id}")
    except Exception as e:
        print(f"Test sonlandı (Beklenen durum): {e}")