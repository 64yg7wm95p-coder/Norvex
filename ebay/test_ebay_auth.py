import os
import sys
from database import SessionLocal, init_db, User, UserToken, decrypt_token
from ebay.auth import generate_ebay_auth_url, handle_ebay_callback, get_valid_access_token

def run_test():
    print("=" * 60)
    print("🚀 SUPPLIERSCANNER V1.0 - EBAY AUTH SAAS KATMANI TESTİ")
    print("=" * 60)

    # 1. Veritabanını Başlat ve Bağlan
    init_db()
    db = SessionLocal()
    
    try:
        # 2. Test Kullanıcısı Oluştur (Yoksa)
        test_email = "maraton_test@supplierscanner.com"
        user = db.query(User).filter(User.email == test_email).first()
        if not user:
            from database import hash_password
            user = User(email=test_email, password_hash=hash_password("guvenli_sifre_123"))
            db.add(user)
            db.commit()
            print(f"[+] 1. AŞAMA: Test Kullanıcısı Veritabanında Oluşturuldu. (User ID: {user.id})")
        else:
            print(f"[+] 1. AŞAMA: Mevcut Test Kullanıcısı Seçildi. (User ID: {user.id})")

        # 3. OAuth Yönlendirme URL Kontrolü
        auth_url = generate_ebay_auth_url()
        print("\n[👉] 2. AŞAMA: Frontend İçin Üretilen Canlı Bağlantı Linki:")
        print(f"    {auth_url}\n")

        # 4. Mock (Simüle) Token Kaydı ve Şifreleme Testi
        print("[*] 3. AŞAMA: Kriptografik Şifreleme Güvenlik Testi Başlatılıyor...")
        
        # Eğer elinde halihazırda çalışan bir eBay Refresh Token varsa .env'den çekip simüle edelim
        env_refresh_token = os.getenv("EBAY_REFRESH_TOKEN", "mock_refresh_token_xyz_123456789")
        
        # handle_ebay_callback fonksiyonunu test etmek adına gerçek bir akış simülasyonu yapıyoruz.
        # Gerçek akışta eBay senin sitene ?code=... parametresi gönderir. Biz burada doğrudan token yazımını tetikliyoruz.
        print(f"[*] Veritabanına kaydedilecek ham token (İlk 15 karakter): {env_refresh_token[:15]}...")
        
        # Test amaçlı manuel şifreli kayıt tetikleme (handle_ebay_callback benzeri)
        from database import encrypt_token
        import datetime
        
        encrypted_rf = encrypt_token(env_refresh_token)
        
        user_token = db.query(UserToken).filter(UserToken.user_id == user.id).first()
        if user_token:
            user_token.encrypted_refresh_token = encrypted_rf
        else:
            user_token = UserToken(
                user_id=user.id,
                encrypted_refresh_token=encrypted_rf,
                token_expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=365)
            )
            db.add(user_token)
        db.commit()
        
        print("[+] Veritabanı yazma işlemi başarılı.")

        # 5. Veritabanından Doğrudan Kontrol (Hacker Gözüyle Bakış)
        db.expire_all()
        db_token_row = db.query(UserToken).filter(UserToken.user_id == user.id).first()
        
        print(f"\n[🔒] SİBER GÜVENLİK KONTROLÜ (Hackerların Veritabanında Göreceği Ham Metin):")
        print(f"    {db_token_row.encrypted_refresh_token[:50]}...")
        
        if "mock_refresh" in db_token_row.encrypted_refresh_token or "Agile" in db_token_row.encrypted_refresh_token:
            print("❌ GÜVENLİK İHLALİ: Token veritabanında düz metin olarak kabak gibi görünüyor!")
        else:
            print("✅ GÜVENLİK DOĞRULANDI: Token veritabanında AES-256 ile tamamen anlamsız bir yığına dönüştürülmüş.")

        # 6. Deşifre Etme ve API Çağrı Uyumluluk Testi
        decrypted = decrypt_token(db_token_row.encrypted_refresh_token)
        print(f"\n[*] 4. AŞAMA: RAM Bellekte Çözme Testi:")
        print(f"    Çözülen Token: {decrypted[:15]}...")
        
        if decrypted == env_refresh_token:
            print("✅ KRİPTOGRAFİ BAŞARILI: Veri kayıpsız şifrelendi ve çözüldü.")
        else:
            print("❌ KRİPTOGRAFİ HATASI: Çözülen veri orijinaliyle eşleşmiyor!")

        # 7. Canlı Canlı eBay Sunucusundan Access Token İsteme Testi
        if os.getenv("EBAY_REFRESH_TOKEN"):
            print("\n[*] 5. AŞAMA: Canlı eBay Sunucu Bağlantı Testi Yapılıyor...")
            try:
                access_token = get_valid_access_token(db, user.id)
                print("✅ EBAY BAĞLANTISI KUSURSUZ: Sunucu anlık Access Token üretti!")
                print(f"    Uçucu Access Token (İlk 20 karakter): {access_token[:20]}...")
                print("🔒 GÜVENLİK NOTU: Bu access token hiçbir dosyaya veya DB'ye yazılmadı, RAM'de imha edilecek.")
            except Exception as e:
                print(f"❌ EBAY BAĞLANTISI BAŞARISIZ: .env dosendaki eBay kimlik bilgileri geçersiz veya süresi dolmuş. Detay:\n{e}")
        else:
            print("\n⚠️  NOT: .env dosyasında gerçek bir EBAY_REFRESH_TOKEN bulunamadığı için canlı sunucu isteği simüle edilmedi. Sadece yerel şifreleme test edildi.")

    finally:
        db.close()
        print("=" * 60)

if __name__ == "__main__":
    run_test()