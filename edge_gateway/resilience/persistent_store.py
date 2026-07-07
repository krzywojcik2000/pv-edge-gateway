import sqlite3
import json
import time
import threading


class PersistentStore:


    def __init__(
        self,
        path="edge_buffer.db"
    ):

        self.conn = sqlite3.connect(
            path,
            check_same_thread=False
        )

        self.cursor = self.conn.cursor()

        self.lock = threading.Lock()

        self._init_table()


    # =====================================================
    # INIT
    # =====================================================

    def _init_table(self):

        with self.lock:

            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS buffer (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    ts REAL,

                    channel TEXT,

                    payload TEXT,

                    synced INTEGER DEFAULT 0

                )
                """
            )

            self.conn.commit()



    # =====================================================
    # STORE FAILED DATA
    # =====================================================

    def store(
        self,
        channel,
        payload
    ):


        with self.lock:

            self.cursor.execute(
                """
                INSERT INTO buffer
                (
                    ts,
                    channel,
                    payload,
                    synced
                )

                VALUES (?, ?, ?, 0)

                """,
                (
                    time.time(),
                    channel,
                    json.dumps(
                        payload,
                        default=str
                    )
                )
            )


            self.conn.commit()



    # =====================================================
    # READ FAILED DATA
    # =====================================================

    def fetch_pending(
        self,
        limit=100
    ):

        with self.lock:

            self.cursor.execute(
                """
                SELECT
                    id,
                    channel,
                    payload

                FROM buffer

                WHERE synced = 0

                ORDER BY id ASC

                LIMIT ?

                """,
                (limit,)
            )

            return self.cursor.fetchall()



    # =====================================================
    # MARK COMPLETED
    # =====================================================

    def mark_synced(
        self,
        ids
    ):

        with self.lock:

            self.cursor.executemany(
                """
                UPDATE buffer

                SET synced = 1

                WHERE id = ?

                """,
                [
                    (i,)
                    for i in ids
                ]
            )

            self.conn.commit()



    # =====================================================
    # REMOVE OLD DATA
    # =====================================================

    def cleanup(
        self,
        limit=10000
    ):

        with self.lock:

            self.cursor.execute(
                """
                DELETE FROM buffer

                WHERE synced = 1

                AND id NOT IN

                (
                    SELECT id
                    FROM buffer
                    ORDER BY id DESC
                    LIMIT ?
                )

                """,
                (limit,)
            )

            self.conn.commit()