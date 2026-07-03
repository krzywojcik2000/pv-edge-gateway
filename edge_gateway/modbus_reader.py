from pymodbus.client import ModbusTcpClient


class ModbusReader:
    def __init__(self, host="127.0.0.1", port=5020):
        self.client = ModbusTcpClient(host, port=port)
        self.host = host
        self.port = port

        print(f"[MODBUS] Reader connected config: {host}:{port}")

    def read_raw(self):
        self.client.connect()

        rr = self.client.read_holding_registers(0, 5)

        if rr.isError():
            print("[MODBUS] Read error")
            return None

        return rr.registers