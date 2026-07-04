class ModbusDecoder:
    """
    Converts raw SmartLogger registers → clean PV data model
    """

    def decode(self, registers):
        if not registers or len(registers) < 5:
            return None

        temperature_raw = registers[0]
        dc_power = registers[1]
        ac_power = registers[2]
        energy = registers[3]
        alarm_bits = registers[4]

        # -----------------------------
        # SCALING (PLC style)
        # -----------------------------
        temperature = temperature_raw / 10.0

        # -----------------------------
        # ALARMS (bit decoding)
        # -----------------------------
        alarm_overtemp = bool(alarm_bits & 0b0001)
        alarm_overpower = bool(alarm_bits & 0b0010)

        alarm = {
            "overtemperature": alarm_overtemp,
            "overpower": alarm_overpower,
            "raw": alarm_bits
        }

        # -----------------------------
        # FINAL PV MODEL
        # -----------------------------
        return {
            "temperature": temperature,
            "dc_power": dc_power,
            "ac_power": ac_power,
            "energy": energy,
            "alarm": alarm
        }