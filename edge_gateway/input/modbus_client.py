from pymodbus.client import ModbusTcpClient


class ModbusIOError(Exception):
    pass


class ModbusClient:

    def __init__(self, host: str, port: int):

        self.host = host
        self.port = port

        self.client = ModbusTcpClient(host=self.host, port=self.port)
        self.connected = False

    # -----------------------------
    # CONNECT
    # -----------------------------
    def connect(self):

        try:
            self.connected = self.client.connect()

            if not self.connected:
                raise ModbusIOError("Unable to connect to Modbus device")

        except Exception as e:
            self.connected = False
            raise ModbusIOError(f"Modbus connect failed: {e}")

    # -----------------------------
    # READ RAW REGISTERS
    # -----------------------------
    def read_raw(self, address: int = 0, count: int = 5) -> list[int]:

        if not self.connected:
            self.connect()

        try:
            response = self.client.read_holding_registers(address, count)

            if response is None or response.isError():
                raise ModbusIOError("Invalid Modbus response")

            return response.registers

        except Exception as e:
            self.connected = False
            raise ModbusIOError(f"Modbus read failed: {e}")

    # -----------------------------
    # STATUS
    # -----------------------------
    def is_connected(self) -> bool:
        return self.connected

    # -----------------------------
    # CLOSE
    # -----------------------------
    def close(self):

        try:
            self.client.close()
            self.connected = False

        except Exception:
            self.connected = False