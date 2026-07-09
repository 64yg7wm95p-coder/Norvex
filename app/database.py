import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(
    BASE_DIR,
    "data",
    "supplierscanner.db"
)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    create_tables(conn)
    migrate_users_table(conn)
    migrate_products_table(conn)
    seed_default_plans(conn)

    conn.commit()
    conn.close()


def create_tables(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user',
            plan TEXT DEFAULT 'free',
            ebay_refresh_token TEXT,
            ebay_access_token TEXT,
            ebay_token_expires_at TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,

            source_marketplace TEXT DEFAULT 'shopify',
            source_product_id TEXT,
            target_marketplace TEXT DEFAULT 'ebay',
            target_listing_id TEXT,

            shopify_product_id TEXT,
            title TEXT,
            original_title TEXT,
            body_html TEXT,
            cost_price REAL,
            ebay_price REAL,
            additional_images TEXT,
            status TEXT DEFAULT 'Hazır',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            monthly_price REAL DEFAULT 0,
            product_limit INTEGER DEFAULT 20,
            ai_limit INTEGER DEFAULT 50,
            marketplace_limit INTEGER DEFAULT 1,
            is_active INTEGER DEFAULT 1
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_name TEXT DEFAULT 'free',
            status TEXT DEFAULT 'active',
            stripe_customer_id TEXT,
            stripe_subscription_id TEXT,
            started_at TEXT DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            default_markup REAL DEFAULT 1.35,
            default_fixed_fee REAL DEFAULT 2.00,
            default_currency TEXT DEFAULT 'GBP',
            auto_ai_title INTEGER DEFAULT 1,
            auto_ai_description INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS scan_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            source_marketplace TEXT DEFAULT 'shopify',
            source_url TEXT,
            status TEXT DEFAULT 'pending',
            total_products INTEGER DEFAULT 0,
            processed_products INTEGER DEFAULT 0,
            message TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            finished_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS export_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            target_marketplace TEXT DEFAULT 'ebay',
            status TEXT DEFAULT 'pending',
            target_listing_id TEXT,
            message TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            finished_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)


def migrate_users_table(conn):
    existing_columns = get_table_columns(conn, "users")

    required_columns = {
        "email": "TEXT",
        "role": "TEXT DEFAULT 'user'",
        "plan": "TEXT DEFAULT 'free'",
        "ebay_refresh_token": "TEXT",
        "ebay_access_token": "TEXT",
        "ebay_token_expires_at": "TEXT",
        "is_active": "INTEGER DEFAULT 1",
        "created_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
    }

    for column_name, column_type in required_columns.items():
        if column_name not in existing_columns:
            conn.execute(
                f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
            )

    conn.execute("""
        UPDATE users
        SET plan = COALESCE(plan, 'free')
    """)


def migrate_products_table(conn):
    existing_columns = get_table_columns(conn, "products")

    required_columns = {
        "user_id": "INTEGER DEFAULT 1",
        "source_marketplace": "TEXT DEFAULT 'shopify'",
        "source_product_id": "TEXT",
        "target_marketplace": "TEXT DEFAULT 'ebay'",
        "target_listing_id": "TEXT",

        "shopify_product_id": "TEXT",
        "title": "TEXT",
        "original_title": "TEXT",
        "body_html": "TEXT",
        "cost_price": "REAL",
        "ebay_price": "REAL",
        "additional_images": "TEXT",
        "status": "TEXT DEFAULT 'Hazır'",

        "created_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
    }

    for column_name, column_type in required_columns.items():
        if column_name not in existing_columns:
            conn.execute(
                f"ALTER TABLE products ADD COLUMN {column_name} {column_type}"
            )

    conn.execute("""
        UPDATE products
        SET source_marketplace = COALESCE(source_marketplace, 'shopify')
    """)

    conn.execute("""
        UPDATE products
        SET source_product_id = COALESCE(source_product_id, shopify_product_id)
    """)

    conn.execute("""
        UPDATE products
        SET target_marketplace = COALESCE(target_marketplace, 'ebay')
    """)

    conn.execute("""
        UPDATE products
        SET status = COALESCE(status, 'Hazır')
    """)


def get_table_columns(conn, table_name: str) -> set:
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row["name"] for row in rows}


def seed_default_plans(conn):
    plans = [
        ("free", 0, 20, 50, 1),
        ("starter", 19, 500, 1000, 2),
        ("pro", 49, 5000, 10000, 5),
        ("business", 99, 20000, 50000, 20),
    ]

    for name, price, product_limit, ai_limit, marketplace_limit in plans:
        conn.execute(
            """
            INSERT OR IGNORE INTO plans (
                name,
                monthly_price,
                product_limit,
                ai_limit,
                marketplace_limit
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name,
                price,
                product_limit,
                ai_limit,
                marketplace_limit
            )
        )