import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database with the schema."""
        with sqlite3.connect(self.db_path) as conn:
            with open('src/database/schema.sql', 'r') as f:
                conn.executescript(f.read())
            conn.commit()

    def insert_tip(self, category, content, source):
        """Insert a tip into the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tips (category, content, source) VALUES (?, ?, ?)",
                (category, content, source)
            )
            conn.commit()

    def get_random_tip(self, category=None):
        """Retrieve a random tip, optionally filtered by category."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute(
                    "SELECT content, source FROM tips WHERE category = ? ORDER BY RANDOM() LIMIT 1",
                    (category,)
                )
            else:
                cursor.execute(
                    "SELECT content, source FROM tips ORDER BY RANDOM() LIMIT 1"
                )
            result = cursor.fetchone()
            return result if result else (None, None)
