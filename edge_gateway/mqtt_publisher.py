import json
import paho.mqtt.client as mqtt


class MQTTPublisher:
    def __init__(self, host="localhost", port=1883, topic="pv/farm1/telemetry"):
        self.client = mqtt.Client()
        self.client.connect(host, port, 60)

        self.topic = topic

        print(f"[MQTT] Connected to {host}:{port}")

    def publish_telemetry(self, farm_id, data):
        payload = {
            "farm_id": farm_id,
            "temperature": data["temperature"],
            "dc_power": data["dc_power"],
            "ac_power": data["ac_power"],
            "energy": data["energy"],
            "alarm": data["alarm"]
        }

        self.client.publish(self.topic, json.dumps(payload))

    def publish_alarm(self, farm_id, data):
        if data["alarm"]["overtemperature"] or data["alarm"]["overpower"]:
            self.client.publish(
                "pv/farm1/alarms",
                json.dumps({
                    "farm_id": farm_id,
                    "alarm": data["alarm"]
                })
            )