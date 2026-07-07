import time


class AggregationManager:

    def __init__(self, window_seconds=60):

        self.window_seconds = window_seconds

        self.buffer = []
        self.window_start = time.time()

    # -----------------------------
    def add(self, measurement):

        self.buffer.append(measurement)

    # -----------------------------
    def should_flush(self):

        if not self.buffer:
            return False

        return (time.time() - self.window_start) >= self.window_seconds

    # -----------------------------
    def flush(self):

        aggregate = self._build_aggregate()

        self.buffer.clear()

        self.window_start = time.time()

        return aggregate

    # -----------------------------
    def _build_aggregate(self):

        data = self.buffer

        return {

            "farm_id": data[0].farm_id,

            "avg_temperature":
                sum(m.temperature for m in data) / len(data),

            "avg_dc_power":
                sum(m.dc_power for m in data) / len(data),

            "avg_ac_power":
                sum(m.ac_power for m in data) / len(data),

            "energy_sum":
                sum(m.energy for m in data),

            "alarm_count":
                sum(int(m.alarm.raw) for m in data)

        }