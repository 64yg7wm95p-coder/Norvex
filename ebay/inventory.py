import os
import sys
import json
import requests

# Proje kök dizinini ekliyoruz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection, get_user_token

def sync_all_users_inventory():
    """
    Sistemdeki tüm benzersiz kullanıcıların stok ve fiyat senkronizasyonunu yönetir.
    eBay tokenı olmayan kullanıcıları hatasız bir şekilde atlar.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Veritabanında işlem görmüş tüm benzersiz kullanıcı ID'lerini çekiyoruz
        cursor.execute("SELECT DISTINCT user_id FROM products")
        users = cursor.fetchall()
        
        if not users:
            print("[-] Sistemde taranacak aktif kullanıcı veya ürün bulunamadı.")
            return
            
        print(f"[*] Toplam {len(users)} farklı SaaS kullanıcısı için stok döngüsü başlatılıyor...")
        
        for user_row in users:
            user_id = user_row["user_id"]
            print(f"\n--- 👤 USER ID: {user_id} İÇİN İŞLEMLER BAŞLADI ---")
            
            # 🔐 GÜVENLİ TOKEN KONTROLÜ
            token_data = get_user_token(user_id)
            if not token_data or not token_data.get("access_token"):
                print(f"⚠️ Uyarı: User ID {user_id} için aktif bir eBay entegrasyonu bulunamadı. Stok döngüsü atlanıyor.")
                continue
                
            # Token metnini rstrip hatasından koruyarak güvenle alıyoruz
            access_token = token_data["access_token"]
            if hasattr(access_token, "rstrip") and access_token:
                access_token = access_token.rstrip()
            else:
                access_token = str(access_token).strip() if access_token else ""
                
            if not access_token:
                print(f"⚠️ Uyarı: User ID {user_id} için geçersiz token yapısı. Atlanıyor.")
                continue
                
            # Kullanıcının ürünlerini çekip tedarikçi fiyatlarıyla karşılaştırma mantığı
            cursor.execute("SELECT * FROM products WHERE user_id = ?", (user_id,))
            user_products = cursor.fetchall()
            print(f"[*] User ID {user_id} için {len(user_products)} ürün tedarikçisiyle karşılaştırılıyor...")
            
            # TODO: Gerçek stok karşılaştırma API istekleri burada access_token ile yürütülebilir.
            
    except Exception as e:
        print(f"❌ Zamanlayıcı döngüsünde hata oluştu: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("[*] Envanter motoru doğrudan test ediliyor...")
    sync_all_users_inventory()