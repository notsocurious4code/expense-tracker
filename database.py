import sqlite3
import hashlib


# ------------------------
# Database Connection
# ------------------------

def get_connection():
    return sqlite3.connect("expenses.db", check_same_thread=False)


# ------------------------
# Create Tables
# ------------------------

def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT,
            category TEXT,
            description TEXT,
            amount REAL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# ------------------------
# Password Hashing
# ------------------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ------------------------
# User Functions
# ------------------------

def register_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    )

    user = cursor.fetchone()
    conn.close()
    return user


# ------------------------
# Expense Functions (CRUD)
# ------------------------

def add_expense(user_id, date, category, description, amount):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO expenses (user_id, date, category, description, amount) VALUES (?, ?, ?, ?, ?)",
        (user_id, date, category, description, amount)
    )

    conn.commit()
    conn.close()


def get_expenses(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, date, category, description, amount FROM expenses WHERE user_id=?",
        (user_id,)
    )

    data = cursor.fetchall()
    conn.close()
    return data


def delete_expense(expense_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id=? AND user_id=?",
        (expense_id, user_id)
    )

    conn.commit()
    conn.close()


def update_expense(expense_id, user_id, date, category, description, amount):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE expenses
        SET date=?, category=?, description=?, amount=?
        WHERE id=? AND user_id=?
        """,
        (date, category, description, amount, expense_id, user_id)
    )

    conn.commit()
    conn.close()