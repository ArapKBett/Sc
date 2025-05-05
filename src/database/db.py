import sqlite3
import logging

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self._create_tables()
        self._migrate_schema()
        self.last_tip_ids = {}  # Track last tip ID per category

    def _create_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tips (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    content TEXT,
                    source TEXT
                )
            ''')
            conn.commit()

    def _migrate_schema(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Check if 'used' column exists
            cursor.execute("PRAGMA table_info(tips)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'used' not in columns:
                cursor.execute('ALTER TABLE tips ADD COLUMN used INTEGER DEFAULT 0')
                logging.getLogger().info("Added 'used' column to tips table")
            conn.commit()

    def insert_tip(self, category, content, source):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO tips (category, content, source, used) VALUES (?, ?, ?, ?)',
                    (category, content, source, 0)
                )
                conn.commit()
        except sqlite3.Error as e:
            logging.getLogger().error(f"Error inserting tip: {e}")

    def get_random_tip(self, category=None):
        logger = logging.getLogger()
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                last_tip_id = self.last_tip_ids.get(category, 0)
                if category:
                    cursor.execute(
                        'SELECT id, content, source FROM tips WHERE category = ? AND used = 0 AND id != ? ORDER BY RANDOM() LIMIT 1',
                        (category, last_tip_id)
                    )
                else:
                    cursor.execute(
                        'SELECT id, content, source FROM tips WHERE used = 0 AND id != ? ORDER BY RANDOM() LIMIT 1',
                        (last_tip_id,)
                    )
                result = cursor.fetchone()
                if not result:
                    # Reset used flags
                    cursor.execute('UPDATE tips SET used = 0 WHERE category = ?', (category,) if category else ())
                    conn.commit()
                    logger.info(f"Reset used flags for category {category or 'all'}")
                    # Retry fetching
                    if category:
                        cursor.execute(
                            'SELECT id, content, source FROM tips WHERE category = ? AND id != ? ORDER BY RANDOM() LIMIT 1',
                            (category, last_tip_id)
                        )
                    else:
                        cursor.execute(
                            'SELECT id, content, source FROM tips WHERE id != ? ORDER BY RANDOM() LIMIT 1',
                            (last_tip_id,)
                        )
                    result = cursor.fetchone()
                if result:
                    tip_id, content, source = result
                    cursor.execute('UPDATE tips SET used = 1 WHERE id = ?', (tip_id,))
                    conn.commit()
                    self.last_tip_ids[category] = tip_id
                    logger.debug(f"Fetched tip ID {tip_id} for category {category}")
                    return content, source
                logger.warning(f"No tips available for category {category}")
                return None, None
        except sqlite3.Error as e:
            logger.error(f"Error fetching tip: {e}")
            return None, None