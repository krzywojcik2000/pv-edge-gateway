import sqlite3


class RuntimeDatabase:


    def __init__(
        self,
        path="runtime_data/edge_runtime.db"
    ):

        self.conn = sqlite3.connect(
            path,
            check_same_thread=False
        )

        self._initialize()



    # =====================================================
    # CREATE TABLES
    # =====================================================

    def _initialize(self):

        cursor = self.conn.cursor()


        # ---------------------------------
        # FAILED DATA BUFFER
        # ---------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS buffer
            (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                timestamp REAL NOT NULL,

                channel TEXT NOT NULL,

                payload TEXT NOT NULL,

                synced INTEGER DEFAULT 0

            )
            """
        )


        # ---------------------------------
        # ERROR HISTORY
        # ---------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS errors
            (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                timestamp REAL NOT NULL,

                component TEXT NOT NULL,

                operation TEXT NOT NULL,

                error_type TEXT,

                message TEXT,

                context TEXT

            )
            """
        )


        # ---------------------------------
        # INDEXES
        # ---------------------------------

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_buffer_pending

            ON buffer(synced)
            """
        )


        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_errors_time

            ON errors(timestamp)
            """
        )


        self.conn.commit()



    # =====================================================
    # CONNECTION
    # =====================================================

    def close(self):

        self.conn.close()