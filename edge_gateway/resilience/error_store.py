import sqlite3
import json
import time
import threading


class ErrorStore:


    def __init__(
        self,
        path="edge_runtime.db"
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
                CREATE TABLE IF NOT EXISTS errors
                (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    timestamp REAL,

                    component TEXT,

                    operation TEXT,

                    error_type TEXT,

                    message TEXT,

                    context TEXT

                )
                """
            )

            self.conn.commit()



    # =====================================================
    # RECORD ERROR
    # =====================================================

    def record(
        self,
        component,
        operation,
        error,
        context=None
    ):


        with self.lock:

            self.cursor.execute(
                """
                INSERT INTO errors
                (
                    timestamp,
                    component,
                    operation,
                    error_type,
                    message,
                    context
                )

                VALUES (?, ?, ?, ?, ?, ?)

                """,
                (

                    time.time(),

                    component,

                    operation,

                    type(error).__name__,

                    str(error),

                    json.dumps(
                        context or {},
                        default=str
                    )

                )
            )


            self.conn.commit()



    # =====================================================
    # READ HISTORY
    # =====================================================

    def fetch_recent(
        self,
        limit=100
    ):


        with self.lock:

            self.cursor.execute(
                """
                SELECT
                    timestamp,
                    component,
                    operation,
                    error_type,
                    message

                FROM errors

                ORDER BY id DESC

                LIMIT ?

                """,
                (limit,)
            )


            return self.cursor.fetchall()



    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup(
        self,
        max_rows=10000
    ):

        with self.lock:

            self.cursor.execute(
                """
                DELETE FROM errors

                WHERE id NOT IN

                (
                    SELECT id
                    FROM errors
                    ORDER BY id DESC
                    LIMIT ?
                )

                """,
                (max_rows,)
            )

            self.conn.commit()