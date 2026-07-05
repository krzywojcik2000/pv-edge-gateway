import asyncio


class FanoutManager:
    """
    Distributes decoded telemetry to independent processing pipelines.

    Every downstream service owns its own asyncio queue.
    Services consume data independently and cannot block each other.
    """

    def __init__(self, maxsize=200):
        self.db_queue = asyncio.Queue(maxsize=maxsize)
        self.mqtt_queue = asyncio.Queue(maxsize=maxsize)
        self.opcua_queue = asyncio.Queue(maxsize=maxsize)

    # --------------------------------------------------
    # Publish one telemetry sample to all pipelines
    # --------------------------------------------------
    async def publish(self, data):
        await self._publish(self.db_queue, data, "DB")
        await self._publish(self.mqtt_queue, data, "MQTT")
        await self._publish(self.opcua_queue, data, "OPCUA")

    async def _publish(self, queue, data, name):
        try:
            queue.put_nowait(data)
        except asyncio.QueueFull:
            print(f"[FANOUT] {name} queue FULL")

    # --------------------------------------------------
    # Consumers
    # --------------------------------------------------
    async def get_db(self):
        return await self.db_queue.get()

    async def get_mqtt(self):
        return await self.mqtt_queue.get()

    async def get_opcua(self):
        return await self.opcua_queue.get()

    # --------------------------------------------------
    # Monitoring
    # --------------------------------------------------
    def stats(self):
        return {
            "db_queue": self.db_queue.qsize(),
            "mqtt_queue": self.mqtt_queue.qsize(),
            "opcua_queue": self.opcua_queue.qsize(),
        }