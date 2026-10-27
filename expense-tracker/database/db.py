import sqlite3
import os
from werkzeug.security import generate_password_hash

# Database file path relative to this file (project root)
DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'expense_tracker.db')


def get_db():
    """
    Returns a SQLite connection with row_factory and foreign keys enabled.
    Enables dict-like access to rows and enforces foreign key constraints.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    """
    Creates all tables using CREATE TABLE IF NOT EXISTS.
    Tables: users, expenses
    """
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()


def seed_db():
    """
    Inserts sample data for development.
    Creates a demo user and 8 sample expenses across categories.
    """
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Check if data already exists (to avoid duplicates on re-seeding)
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] > 0:
            print('Database already seeded. Skipping...')
            conn.close()
            return

        # Hash password for demo user
        password_hash = generate_password_hash('demo123')

        # Insert demo user
        cursor.execute('''
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
        ''', ('Demo User', 'demo@spendly.com', password_hash))

        # Get demo user ID
        cursor.execute('SELECT id FROM users WHERE email = ?', ('demo@spendly.com',))
        demo_user_id = cursor.fetchone()[0]

        # 8 sample expenses for demo user across current month (2026-10)
        # Covers all 7 categories from spec: Food, Transport, Bills, Health, Entertainment, Shopping, Other
        demo_expenses = [
            (demo_user_id, 25.50, 'Food', '2026-10-05', 'Lunch at cafe'),
            (demo_user_id, 15.00, 'Transport', '2026-10-06', 'Bus fare'),
            (demo_user_id, 120.00, 'Bills', '2026-10-01', 'Electric bill'),
            (demo_user_id, 45.00, 'Health', '2026-10-10', 'Pharmacy'),
            (demo_user_id, 30.00, 'Entertainment', '2026-10-12', 'Movie tickets'),
            (demo_user_id, 80.00, 'Shopping', '2026-10-15', 'New shoes'),
            (demo_user_id, 22.00, 'Other', '2026-10-20', 'Miscellaneous'),
            (demo_user_id, 18.50, 'Food', '2026-10-25', 'Groceries'),
        ]

        for user_id, amount, category, date, description in demo_expenses:
            cursor.execute('''
                INSERT INTO expenses (user_id, amount, category, date, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, amount, category, date, description))

        conn.commit()
        print('Database seeded successfully.')

    except Exception as e:
        conn.rollback()
        print(f'Error seeding database: {e}')
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    init_db()
    seed_db()