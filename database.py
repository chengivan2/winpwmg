import sqlite3
import os

DB_NAME = "pwmg.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # User table for master password and login lockout
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            master_password_hash TEXT NOT NULL,
            login_attempts INTEGER DEFAULT 0,
            login_lockout_until TEXT
        )
    ''')
    
    # Vault table for stored credentials
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vault (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            sensitive_attempts INTEGER DEFAULT 0,
            sensitive_lockout_until TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def create_user(password_hash):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (master_password_hash) VALUES (?)", (password_hash,))
    conn.commit()
    conn.close()

def get_user():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users LIMIT 1")
    user = cursor.fetchone()
    conn.close()
    return user

def update_login_lockout(attempts, lockout_until=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET login_attempts = ?, login_lockout_until = ?", (attempts, lockout_until))
    conn.commit()
    conn.close()

def add_password(url, email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO vault (url, email, password) VALUES (?, ?, ?)", (url, email, password))
    conn.commit()
    conn.close()

def get_passwords_by_url(url):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, password, sensitive_attempts, sensitive_lockout_until FROM vault WHERE url = ?", (url,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_password(vault_id, email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE vault SET email = ?, password = ?, sensitive_attempts = 0, sensitive_lockout_until = NULL WHERE id = ?", (email, password, vault_id))
    conn.commit()
    conn.close()

def delete_password(vault_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vault WHERE id = ?", (vault_id,))
    conn.commit()
    conn.close()

def update_sensitive_lockout(vault_id, attempts, lockout_until=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE vault SET sensitive_attempts = ?, sensitive_lockout_until = ? WHERE id = ?", (attempts, lockout_until, vault_id))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
