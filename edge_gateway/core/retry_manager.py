import asyncio


class RetryManager:
    """
    Replays data from PersistentStore to PostgreSQL.

    Responsibility:
    - restore lost DB writes
    - ensure eventual consistency
    """

    def __init__(self, db_writer, persistent_store, interval=5):
        self.db = db_writer
        self.store = persistent_store
        self.interval = interval

        self.running = False

    # -----------------------------------------
    # START LOOP
    # -----------------------------------------
    async def start(self):
        self.running = True
        print("[RetryManager] started")

        while self.running:
            try:
                await self._replay()
            except Exception as e:
                print("[RetryManager] ERROR:", e)

            await asyncio.sleep(self.interval)

    # -----------------------------------------
    # STOP
    # -----------------------------------------
    def stop(self):
        self.running = False

    # -----------------------------------------
    # MAIN REPLAY LOGIC
    # -----------------------------------------
    async def _replay(self):

        if self.store.is_empty():
            return

        print(f"[RetryManager] replay size={self.store.size()}")

        # IMPORTANT: we process ONE BY ONE for safety
        while not self.store.is_empty():

            record = self.store.peek()

            if record is None:
                break

            record_id, data = record

            try:
                farm_id = data.get("farm_id", "UNKNOWN")

                # re-run same DB pipeline
                self.db.insert_raw(farm_id, data)
                self.db.insert_aggregate(farm_id, data)
                self.db.insert_business(farm_id, data)
                self.db.insert_alarm(farm_id, data)

                # commit transaction
                self.db.commit()

                # if success → remove from persistent store
                self.store.dequeue()

                print(f"[RetryManager] replay OK id={record_id}")

            except Exception as e:

                # IMPORTANT:
                # stop processing on first failure
                # to avoid flooding DB with errors

                print(f"[RetryManager] replay FAILED id={record_id}: {e}")

                self.db.rollback()

                break