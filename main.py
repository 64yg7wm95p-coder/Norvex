import os, time, json, sqlite3, requests
from openai import OpenAI
from dotenv import load_dotenv

# --- AYARLAR ---
load_dotenv()
DB_PATH = "scanner.db"

# --- 1. MODÜL: SHOPIFY LOADER ---
def fetch_shopify_data(url: str, limit: int = 5):
    target = f"{url.rstrip('/')}/products.json?limit={limit}"
    try:
        res = requests.get(target, timeout=15)
        return res.json().get("products", []) if res.status_code == 200 else []
    except: return []

# --- 2. MODÜL: AI OPTIMIZER ---
def secure_ai_optimizer(title: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "")
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "Create SEO-friendly eBay titles. Max 80 chars."}, {"role": "user", "content": title}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content).get("title", title)
    except: return title

# --- 3. MODÜL: DATABASE MANAGER ---
def setup_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT, shopify_product_id TEXT UNIQUE, 
        title TEXT, original_title TEXT, cost_price REAL, ebay_price REAL, 
        images TEXT, status TEXT)""")
    conn.commit(); conn.close()

def save_product(p):
    conn = sqlite3.connect(DB_PATH)
    cost = float(p.get("variants", [{}])[0].get("price", 0))
    ebay_p = round((cost * 1.35) + 2.00, 2)
    imgs = ",".join([i.get("src", "") for i in p.get("images", [])])
    title = secure_ai_optimizer(p.get("title", ""))
    
    conn.execute("""INSERT OR REPLACE INTO products 
        (shopify_product_id, title, original_title, cost_price, ebay_price, images, status) 
        VALUES (?, ?, ?, ?, ?, ?, ?)""", 
        (str(p.get("id")), title, p.get("title"), cost, ebay_p, imgs, "Hazir"))
    conn.commit(); conn.close()

# --- 4. ANA YÖNETİCİ ---
def main():
    print("=== SUPPLIERSCANNER ANA YÖNETİCİ BAŞLATILDI ===")
    setup_db()
    products = fetch_shopify_data("https://addax.co.uk", limit=4)
    for p in products:
        save_product(p)
        print(f"İşlendi: {p.get('title')}")
    print("İşlem Başarılı.")

if __name__ == "__main__":
    main()