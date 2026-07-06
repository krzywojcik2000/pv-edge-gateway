import time


class ModbusManager:

    def __init__(self, client, max_retries=3, backoff=0.2):
        self.client = client
        self.max_retries = max_retries
        self.backoff = backoff

        self.failure_count = 0
        self.last_error_time = 0

    # -----------------------------
    def read_raw(self):

        for attempt in range(self.max_retries):

            try:
                data = self.client.read_raw()

                self.failure_count = 0
                return data

            except Exception as e:

                self.failure_count += 1
                self.last_error_time = time.time()

                print(f"[MODBUS MANAGER] attempt {attempt+1} failed: {e}")

                time.sleep(self.backoff * (attempt + 1))

        return None