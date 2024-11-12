import sqlite3

conn = sqlite3.connect('koktepa.db') 
conn.row_factory = sqlite3.Row  # This makes each row return as a dictionary
cur = conn.cursor()

def create_db():
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100),
                telefon VARCHAR(20),
                user_id INTEGER
                )""")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS category(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100)
                )""")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS product(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100),
                price INTEGER,
                category_id INTEGER,
                image TEXT,
                FOREIGN KEY (category_id) REFERENCES category(id))""")
    
    conn.commit()


def hozirgi_userni_olish(user_id):
    user = cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if user:
        return dict(user)  # Convert Row object to dictionary
    return None

def user_in_database(id):
    user = cur.execute("SELECT * FROM users WHERE user_id = ?", (id,)).fetchone()
    return user is not None

def add_data_to_users(name, telefon, user_id):
    cur.execute("INSERT INTO users(name, telefon, user_id) VALUES(?, ?, ?)", (name, telefon, user_id))
    conn.commit()


def add_data_to_category(name):
    cur.execute("INSERT INTO category(name) VALUES(?)", (name,))
    conn.commit()

def add_data_to_product(category_id, name, price, image):
    cur.execute("INSERT INTO product(category_id, name, price, image) VALUES(?, ?, ?, ?)", (category_id, name, price, image))
    conn.commit()

def get_all_categories():
    categories = cur.execute("SELECT * FROM category").fetchall()
    return [dict(row) for row in categories]  # Row obyektlarini dict ga aylantirish

def get_category_id(name):
    category = cur.execute("SELECT * FROM category WHERE name=?", (name,)).fetchone()
    return dict(category) if category else None

def delete_category_by_id(id):
    cur.execute("DELETE FROM category WHERE id=?", (id,))
    conn.commit()


def get_all_products():
    products = cur.execute("SELECT * FROM product").fetchall()
    return [dict(row) for row in products]  # Row obyektlarini dict ga aylantirish

def get_product_by_id(id):
    product = cur.execute("SELECT * FROM product WHERE id=?", (id,)).fetchone()
    return dict(product) if product else None


def get_c_id_by_name(name):
    row = cur.execute("SELECT id FROM category WHERE name=?", (name,)).fetchone()
    return row['id'] if row else None  # Agar topilmasa, None qaytaradi
