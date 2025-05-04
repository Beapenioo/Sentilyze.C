import sqlite3
from datetime import datetime
import os

class DatabaseOperations:
    def __init__(self, db_path=None):
        if db_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(current_dir, "users.db")
        else:
            self.db_path = db_path
        self.create_tables()

    def create_tables(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        surname TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
        except Exception as e:
            print(f"Error creating tables: {e}")

    def register_user(self, name, surname, email, password):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (name, surname, email, password)
                    VALUES (?, ?, ?, ?)
                ''', (name, surname, email, password))
                conn.commit()
                return True
        except sqlite3.IntegrityError as e:
            print(f"Integrity error: {e}")
            return False
        except Exception as e:
            print(f"Error registering user: {e}")
            return False

    def check_user_exists(self, email):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM users 
                    WHERE email = ?
                ''', (email,))
                return cursor.fetchone()[0] > 0
        except Exception as e:
            print(f"Error checking user: {e}")
            return False 