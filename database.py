import sqlite3

DATABASE_NAME = 'koktepa.db'
conn = sqlite3.connect(DATABASE_NAME)
conn.row_factory = sqlite3.Row
cur = conn.cursor()


def create_db():
    with conn:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                telefon TEXT NOT NULL,
                user_id INTEGER UNIQUE NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS category(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS product(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price INTEGER NOT NULL,
                category_id INTEGER,
                image TEXT,
                FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE CASCADE
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_product(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cart(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                products INTEGER,
                total_price INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)


def hozirgi_userni_olish(user_id):
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    return dict(row) if row else None


def user_in_database(user_id):
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return bool(cur.fetchone())


def add_data_to_users(name, telefon, user_id):
    cur.execute("INSERT INTO users(name, telefon, user_id) VALUES(?, ?, ?)", (name, telefon, user_id))
    conn.commit()


def get_user_id(user_id):
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    return dict(row) if row else None


def add_data_to_category(name):
    cur.execute("INSERT INTO category(name) VALUES(?)", (name,))
    conn.commit()


def add_data_to_product(category_id, name, price, image):
    cur.execute("INSERT INTO product(category_id, name, price, image) VALUES(?, ?, ?, ?)", (category_id, name, price, image))
    conn.commit()


def get_all_categories():
    cur.execute("SELECT * FROM category")
    rows = cur.fetchall()
    return [dict(row) for row in rows] if rows else []


def get_category_id(name):
    cur.execute("SELECT * FROM category WHERE name=?", (name,))
    row = cur.fetchone()
    return dict(row) if row else None


def delete_category_by_id(id):
    cur.execute("DELETE FROM category WHERE id=?", (id,))
    conn.commit()


def get_all_products():
    cur.execute("SELECT * FROM product")
    rows = cur.fetchall()
    return [dict(row) for row in rows] if rows else []


def get_product_by_id(id):
    cur.execute("SELECT * FROM product WHERE id=?", (id,))
    row = cur.fetchone()
    return dict(row) if row else None


def get_c_id_by_name(name):
    cur.execute("SELECT id FROM category WHERE name=?", (name,))
    row = cur.fetchone()
    return row['id'] if row else None


def delete_product_by_id(id):
    cur.execute("DELETE FROM product WHERE id=?", (id,))
    conn.commit()


def add_data_user_product(user_id, product_id):
    cur.execute("INSERT INTO user_product(user_id, product_id) VALUES(?, ?)", (user_id, product_id))
    conn.commit()


def add_data_to_cart(user_id, products, total_price):
    cur.execute("INSERT INTO cart(user_id, products, total_price) VALUES(?, ?, ?)", (user_id, products, total_price))
    conn.commit()


def get_user_product(user_id):
    cur.execute("SELECT * FROM user_product WHERE user_id=?", (user_id,))
    rows = cur.fetchall()
    return [dict(row) for row in rows] if rows else []
