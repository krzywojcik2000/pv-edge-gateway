
from pymodbus.client.sync import ModbusTcpClient

class ModbusReader:
    def __init__(self, config):
        self.host = config["host"]
        self.port = config["port"]
        
        self.client = ModbusTcpClient(
            host=self.host,
            port=self.port
        )
        self.client.connect()

    def read_raw(self):
        rr = self.client.read_holding_registers(0, 5)
        if rr.isError():
            print("[MODBUS] Read error")
            return None

        return rr.registers