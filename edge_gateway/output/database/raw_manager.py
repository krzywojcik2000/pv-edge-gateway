import time


class RawDataManager:

    def __init__(self, batch_size=100, flush_interval=2):

        self.batch_size = batch_size
        self.flush_interval = flush_interval

        self.buffer = []
        self.last_flush = time.time()

    # -----------------------------
    def add(self, measurement):

        self.buffer.append(measurement)

    # -----------------------------
    def should_flush(self):

        if not self.buffer:
            return False

        if len(self.buffer) >= self.batch_size:
            return True

        return (time.time() - self.last_flush) >= self.flush_interval

    # -----------------------------
    def flush(self):

        batch = self.buffer

        self.buffer = []

        self.last_flush = time.time()

        return batch