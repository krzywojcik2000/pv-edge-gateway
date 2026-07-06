import asyncio
import time


class CycleExecutor:

    def __init__(self, modbus_manager, processing, fanout, farm_id, interval=1.0):

        self.modbus = modbus_manager
        self.processing = processing
        self.fanout = fanout

        self.farm_id = farm_id
        self.interval = interval

        self.running = True

    # -----------------------------
    async def run(self):

        print("[CYCLE] started")

        while self.running:

            cycle_start = time.time()

            try:
                # =========================
                # 1. INPUT LAYER
                # =========================
                raw = self.modbus.read_raw()

                if raw is None:
                    # normalny brak danych z device layer
                    await self._sleep_cycle(cycle_start)
                    continue

                # =========================
                # 2. PROCESSING LAYER
                # =========================
                measurement = self.processing.process(raw)

                if measurement is None:
                    await self._sleep_cycle(cycle_start)
                    continue

                measurement.farm_id = self.farm_id

                # =========================
                # 3. FANOUT LAYER
                # =========================
                self.fanout.publish(measurement)

                print("[CYCLE] OK")

            except Exception as e:
                # TU JEST TYLKO SAFETY NET
                print("[CYCLE ERROR]", e)

            # =========================
            # 4. CYCLE TIMING CONTROL
            # =========================
            await self._sleep_cycle(cycle_start)

    # -----------------------------
    async def _sleep_cycle(self, start_time):

        elapsed = time.time() - start_time
        wait_time = max(0, self.interval - elapsed)

        await asyncio.sleep(wait_time)

    # -----------------------------
    def stop(self):
        self.running = False