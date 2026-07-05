import sqlite3
import json
from pathlib import Path


class PersistentStore:
    """
    SQLite-based persistent FIFO queue.

    Used as a fallback when PostgreSQL is unavailable.
    """

    def __init__(self, db_path="database/persistent_store.db"):

        Path("database").mkdir(exist_ok=True)

        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS queue (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                payload TEXT NOT NULL

            )
        """)

        self.conn.commit()

        print("[PersistentStore] SQLite ready")

    # -------------------------------------------------
    # PUSH
    # -------------------------------------------------

    def enqueue(self, data):

        payload = json.dumps(data)

        self.cursor.execute("""
            INSERT INTO queue(payload)
            VALUES(?)
        """, (payload,))

        self.conn.commit()

    # -------------------------------------------------
    # PEEK
    # -------------------------------------------------

    def peek(self):

        self.cursor.execute("""
            SELECT id, payload
            FROM queue
            ORDER BY id
            LIMIT 1
        """)

        row = self.cursor.fetchone()

        if row is None:
            return None

        record_id, payload = row

        return record_id, json.loads(payload)

    # -------------------------------------------------
    # REMOVE FIRST
    # -------------------------------------------------

    def dequeue(self):

        self.cursor.execute("""
            SELECT id
            FROM queue
            ORDER BY id
            LIMIT 1
        """)

        row = self.cursor.fetchone()

        if row is None:
            return

        record_id = row[0]

        self.cursor.execute("""
            DELETE FROM queue
            WHERE id=?
        """, (record_id,))

        self.conn.commit()

    # -------------------------------------------------
    # INFO
    # -------------------------------------------------

    def size(self):

        self.cursor.execute("""
            SELECT COUNT(*)
            FROM queue
        """)

        return self.cursor.fetchone()[0]

    def is_empty(self):

        return self.size() == 0