import asyncio
from collections import deque


class FanoutManager:
    """
    Distributes incoming data to multiple independent pipelines.
    """

    def __init__(self, maxsize=200):
        self.db_queue = asyncio.Queue(maxsize=maxsize)
        self.mqtt_queue = asyncio.Queue(maxsize=maxsize)
        self.opcua_queue = asyncio.Queue(maxsize=maxsize)

        # fallback buffers (optional safety layer)
        self.db_fallback = deque(maxlen=1000)
        self.mqtt_fallback = deque(maxlen=1000)
        self.opcua_fallback = deque(maxlen=1000)

    # -----------------------------
    # INPUT (from Modbus reader)
    # -----------------------------
    async def publish(self, data):
        await self._safe_put(self.db_queue, self.db_fallback, data, "DB")
        await self._safe_put(self.mqtt_queue, self.mqtt_fallback, data, "MQTT")
        await self._safe_put(self.opcua_queue, self.opcua_fallback, data, "OPCUA")

    # -----------------------------
    # SAFE PUT (no system crash)
    # -----------------------------
    async def _safe_put(self, queue, fallback, data, name):
        try:
            queue.put_nowait(data)
        except asyncio.QueueFull:
            print(f"[FANOUT] {name} queue FULL → using fallback buffer")
            fallback.append(data)

    # -----------------------------
    # CONSUMERS
    # -----------------------------
    async def get_db(self):
        return await self.db_queue.get()

    async def get_mqtt(self):
        return await self.mqtt_queue.get()

    async def get_opcua(self):
        return await self.opcua_queue.get()

    # -----------------------------
    # MONITORING
    # -----------------------------
    def stats(self):
        return {
            "db": self.db_queue.qsize(),
            "mqtt": self.mqtt_queue.qsize(),
            "opcua": self.opcua_queue.qsize(),
            "db_fallback": len(self.db_fallback),
            "mqtt_fallback": len(self.mqtt_fallback),
            "opcua_fallback": len(self.opcua_fallback),
        }