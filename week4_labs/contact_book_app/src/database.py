import sqlite3

def init_db():
    conn = sqlite3.connect("contacts.db", check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT
        )
    """)
    conn.commit()
    return conn

def insert_contact_db(conn, name, phone, email):
    cur = conn.cursor()
    cur.execute("INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)", (name, phone, email))
    conn.commit()

def get_all_contacts_db(conn, search_term=""):
    cur = conn.cursor()
    if search_term:
        cur.execute("SELECT * FROM contacts WHERE name LIKE ?", ('%' + search_term + '%',))
    else:
        cur.execute("SELECT * FROM contacts")
    return cur.fetchall()

def delete_contact_db(conn, contact_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
    conn.commit()
    return cur.rowcount
