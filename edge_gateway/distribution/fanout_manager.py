from queue import Full


class FanoutManager:

    def __init__(self, db_queue, mqtt_queue, opcua_queue, persistent_store=None):

        self.db_queue = db_queue
        self.mqtt_queue = mqtt_queue
        self.opcua_queue = opcua_queue

        self.persistent_store = persistent_store

    # -----------------------------
    # PUBLIC API
    # -----------------------------
    def publish(self, measurement):

        # DB (critical - must not lose data)
        self._safe_put(
            self.db_queue,
            measurement,
            system="DB",
            critical=True
        )

        # MQTT (best effort)
        self._safe_put(
            self.mqtt_queue,
            measurement,
            system="MQTT",
            critical=False
        )

        # OPCUA (state layer - last value wins semantics)
        self._safe_put(
            self.opcua_queue,
            measurement,
            system="OPCUA",
            critical=False
        )

    # -----------------------------
    # INTERNAL SAFE PUT
    # -----------------------------
    def _safe_put(self, queue, item, system: str, critical: bool):

        try:
            queue.put_nowait(item)

        except Full:

            # =========================
            # DB → NEVER DROP
            # =========================
            if system == "DB":
                print("[FANOUT] DB overflow → persistent store (CRITICAL)")

                if self.persistent_store:
                    self.persistent_store.store(item)

            # =========================
            # MQTT → DROP OK
            # =========================
            elif system == "MQTT":
                print("[FANOUT] MQTT overflow → DROP (non-critical)")

            # =========================
            # OPCUA → DROP (manager keeps last value anyway)
            # =========================
            elif system == "OPCUA":
                print("[FANOUT] OPCUA overflow → DROP (state is overwritten downstream)")