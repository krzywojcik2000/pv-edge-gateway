import json
import paho.mqtt.client as mqtt


class MQTTConnectionError(Exception):
    pass



class MQTTPublisher:


    def __init__(
        self,
        host,
        port
    ):

        self.host = host
        self.port = port

        self.client = mqtt.Client()

        self.connected = False



    # =========================================
    # CONNECT
    # =========================================

    def connect(self):

        try:

            result = self.client.connect(
                self.host,
                self.port,
                60
            )


            if result != 0:

                raise MQTTConnectionError(
                    "MQTT broker connection failed"
                )


            self.connected = True


        except Exception as e:

            self.connected = False

            raise MQTTConnectionError(
                f"MQTT connect error: {e}"
            )



    # =========================================
    # PUBLISH
    # =========================================

    def publish(
        self,
        topic,
        payload
    ):

        if not self.connected:

            self.connect()


        try:

            result = self.client.publish(
                topic,
                json.dumps(payload)
            )


            if result.rc != mqtt.MQTT_ERR_SUCCESS:

                raise MQTTConnectionError(
                    "MQTT publish failed"
                )


        except Exception:

            self.connected = False

            raise



    # =========================================
    # HEALTH
    # =========================================

    def is_connected(self):

        return self.connected