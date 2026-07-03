from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
import threading
import time
import random

# -----------------------------
# HOLDING REGISTERS (PLC memory)
# -----------------------------
store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [0]*100)
)

context = ModbusServerContext(slaves=store, single=True)

# -----------------------------
# SIMULATION LOOP
# -----------------------------
def update_loop():
    energy_counter = 10000

    while True:
        # REALISTIC PV VALUES
        temperature = random.randint(200, 850)  # scaled: /10 => 20.0 - 85.0°C
        dc_power = random.randint(800, 1200)
        ac_power = int(dc_power * 0.95)

        energy_counter += random.randint(5, 20)

        # BITMASK ALARM (real PLC style)
        alarm_overtemp = 1 if temperature > 750 else 0
        alarm_overpower = 1 if dc_power > 1150 else 0

        alarm = (alarm_overtemp << 0) | (alarm_overpower << 1)

        # -----------------------------
        # MODBUS REGISTERS (REAL STYLE)
        # -----------------------------
        context[0].setValues(3, 1, [temperature])   # HR40001 (scaled)
        context[0].setValues(3, 2, [dc_power])      # HR40002
        context[0].setValues(3, 3, [ac_power])      # HR40003
        context[0].setValues(3, 4, [energy_counter])# HR40004
        context[0].setValues(3, 5, [alarm])         # HR40005 (bitmask)

        time.sleep(1)


thread = threading.Thread(target=update_loop)
thread.daemon = True
thread.start()

print("SmartLogger PV Simulator (UPGRADED) running on 0.0.0.0:5020")

# -----------------------------
# MODBUS TCP SERVER
# -----------------------------
StartTcpServer(context=context, address=("0.0.0.0", 5020))