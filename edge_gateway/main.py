import time

from modbus_reader import ModbusReader
from modbus_decoder import ModbusDecoder
from database_writer import DatabaseWriter
from mqtt_publisher import MQTTPublisher


# -----------------------------
# CONFIG
# -----------------------------
config = {
    "db_name": "pv_scada",
    "db_user": "pv_user",
    "db_password": "pv_pass",
    "db_host": "localhost",
    "db_port": 5432
}

FARM_ID = "KRK-01"


# -----------------------------
# INIT COMPONENTS
# -----------------------------
reader = ModbusReader(host="127.0.0.1", port=5020)
decoder = ModbusDecoder()
db = DatabaseWriter(config)
mqtt = MQTTPublisher()


print("Edge Gateway started...")

# -----------------------------
# MAIN LOOP
# -----------------------------
while True:
    raw = reader.read_raw()

    if raw:
        data = decoder.decode(raw)

        if data:
            db.insert_raw(FARM_ID, data)
            db.insert_alarm(FARM_ID, data)
            db.insert_business(FARM_ID, data)

            mqtt.publish_telemetry(FARM_ID, data)
            mqtt.publish_alarm(FARM_ID, data)

            print("[OK] Data saved + published")

    time.sleep(1)