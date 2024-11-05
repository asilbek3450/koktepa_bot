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
    
    cur.execute("""CREATE TABLE IF NOT EXISTS CATEGORY(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100)
                )""")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS PRODUCT(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100),
                price INTEGER,
                category_id INTEGER,
                FOREIGN KEY (category_id) REFERENCES CATEGORY(id))""")
    
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
    cur.execute("INSERT INTO CATEGORY(name) VALUES(?)", (name,))
    conn.commit()


def get_all_categories():
    categories = cur.execute("SELECT * FROM CATEGORY").fetchall()
    return categories