from edge_gateway.domain.measurement import Measurement, Alarm


class Decoder:

    def decode(self, raw: dict):

        try:
            alarm_raw = raw.get("alarm", {})

            alarm = Alarm(
                overtemperature=alarm_raw.get("overtemperature", False),
                overpower=alarm_raw.get("overpower", False),
                raw=alarm_raw.get("raw", 0)
            )

            return Measurement(
                temperature=raw.get("temperature", 0.0),
                dc_power=raw.get("dc_power", 0),
                ac_power=raw.get("ac_power", 0),
                energy=raw.get("energy", 0),
                alarm=alarm
            )

        except Exception as e:
            print("[DECODER ERROR]", e)
            return None