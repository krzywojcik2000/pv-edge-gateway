import asyncio
import time


class Watchdog:
    """
    Monitors health of entire edge pipeline.
    """

    def __init__(self, fanout, db_batch_writer, persistent_store):

        self.fanout = fanout
        self.db_batch_writer = db_batch_writer
        self.store = persistent_store

        self.running = False

        # thresholds
        self.max_queue_size = 150
        self.max_persistent_size = 5000

        self.last_db_activity = time.time()

    # ----------------------------------------
    # START LOOP
    # ----------------------------------------
    async def start(self):

        self.running = True
        print("[Watchdog] started")

        while self.running:

            try:
                self._check_fanout()
                self._check_db_queue()
                self._check_persistent_store()
                self._check_db_liveness()

            except Exception as e:
                print("[Watchdog] ERROR:", e)

            await asyncio.sleep(5)

    # ----------------------------------------
    # STOP
    # ----------------------------------------
    def stop(self):
        self.running = False

    # ----------------------------------------
    # CHECK FANOUT QUEUES
    # ----------------------------------------
    def _check_fanout(self):

        stats = self.fanout.stats()

        for name, size in stats.items():

            if size > self.max_queue_size:
                print(f"[WATCHDOG] WARNING: {name} queue HIGH = {size}")

    # ----------------------------------------
    # CHECK DB BATCH QUEUE
    # ----------------------------------------
    def _check_db_queue(self):

        size = self.db_batch_writer.queue.qsize()

        if size > self.max_queue_size:
            print(f"[WATCHDOG] DB batch queue HIGH = {size}")

    # ----------------------------------------
    # CHECK PERSISTENT STORE
    # ----------------------------------------
    def _check_persistent_store(self):

        size = self.store.size()

        if size > self.max_persistent_size:
            print(f"[WATCHDOG] CRITICAL: SQLite backlog = {size}")

    # ----------------------------------------
    # DB LIVENESS CHECK (soft heartbeat)
    # ----------------------------------------
    def _check_db_liveness(self):

        try:
            # lightweight query
            self.db_batch_writer.db.cursor.execute("SELECT 1")
            self.db_batch_writer.db.conn.commit()

            self.last_db_activity = time.time()

        except Exception:
            print("[WATCHDOG] CRITICAL: PostgreSQL DOWN")