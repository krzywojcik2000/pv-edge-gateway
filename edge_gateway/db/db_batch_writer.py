import asyncio


class DBBatchWriter:
    """
    Buffers DB operations and writes in batches.
    Handles:
    - retry
    - persistence store
    - batching
    """

    def __init__(self, db_writer, persistent_store, batch_size=50):
        self.db = db_writer
        self.store = persistent_store

        self.queue = asyncio.Queue(maxsize=1000)
        self.batch_size = batch_size

    # -----------------------------
    # INPUT FROM FANOUT
    # -----------------------------
    async def publish(self, data):
        await self.queue.put(data)

    # -----------------------------
    # MAIN LOOP
    # -----------------------------
    async def run(self):
        while True:
            batch = []

            try:
                # gather batch
                for _ in range(self.batch_size):
                    batch.append(await asyncio.wait_for(self.queue.get(), timeout=1))

            except asyncio.TimeoutError:
                pass

            if not batch:
                continue

            await self._process_batch(batch)

    # -----------------------------
    # PROCESS BATCH
    # -----------------------------
    async def _process_batch(self, batch):

        for data in batch:
            try:
                farm_id = data["farm_id"]

                self.db.insert_raw(farm_id, data)
                self.db.insert_aggregate(farm_id, data)
                self.db.insert_business(farm_id, data)
                self.db.insert_alarm(farm_id, data)

            except Exception as e:
                print("[DB-BATCH] ERROR:", e)

                # fallback to persistent store
                self.store.enqueue(data)
                continue

        try:
            self.db.commit()
        except Exception as e:
            print("[DB-BATCH] COMMIT FAILED:", e)
            self.db.rollback()

            for data in batch:
                self.store.enqueue(data)