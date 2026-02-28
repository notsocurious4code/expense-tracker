import sqlite3

DB_NAME = "expenses.db"

def connect():
    return sqlite3.connect(DB_NAME)

def create_table():
    conn = connect()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            description TEXT,
            amount REAL
        )
    """)
    
    conn.commit()
    conn.close()

def add_expense(date, category, description, amount):
    conn = connect()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO expenses (date, category, description, amount)
        VALUES (?, ?, ?, ?)
    """, (date, category, description, amount))
    
    conn.commit()
    conn.close()

def get_expenses():
    conn = connect()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    
    conn.close()
    return rows