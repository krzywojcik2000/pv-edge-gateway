class AlarmManager:

    def __init__(self):

        self.buffer = []

    # -----------------------------
    def add(self, measurement):

        alarm = measurement.alarm

        if alarm.overtemperature:

            self.buffer.append({

                "farm_id": measurement.farm_id,
                "alarm_type": "OVERTEMPERATURE",
                "message": "Temperature exceeded limit",
                "value": measurement.temperature,
                "severity": "HIGH"

            })

        if alarm.overpower:

            self.buffer.append({

                "farm_id": measurement.farm_id,
                "alarm_type": "OVERPOWER",
                "message": "Power exceeded limit",
                "value": measurement.dc_power,
                "severity": "HIGH"

            })

    # -----------------------------
    def should_flush(self):

        return bool(self.buffer)

    # -----------------------------
    def flush(self):

        alarms = self.buffer

        self.buffer = []

        return alarms