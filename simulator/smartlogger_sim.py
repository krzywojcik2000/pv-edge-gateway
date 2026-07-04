from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock
import threading
import time
import random

# -----------------------------
# MODBUS MEMORY (holding registers)
# -----------------------------
store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [0] * 100)
)

context = ModbusServerContext(slaves=store, single=True)

# -----------------------------
# SIMULATION LOOP
# -----------------------------
def update_loop():
    energy_counter = 10000

    while True:
        # PV VALUES
        temperature = random.randint(200, 850)   # /10 => 20.0 - 85.0°C
        dc_power = random.randint(800, 1200)
        ac_power = int(dc_power * 0.95)

        energy_counter += random.randint(5, 20)

        # ALARMS (bitmask)
        alarm_overtemp = 1 if temperature > 750 else 0
        alarm_overpower = 1 if dc_power > 1150 else 0

        alarm = (alarm_overtemp << 0) | (alarm_overpower << 1)

        # WRITE TO HOLDING REGISTERS
        store.setValues(3, 0, [temperature])    # HR40001
        store.setValues(3, 1, [dc_power])       # HR40002
        store.setValues(3, 2, [ac_power])       # HR40003
        store.setValues(3, 3, [energy_counter]) # HR40004
        store.setValues(3, 4, [alarm])          # HR40005

        time.sleep(1)


# run background thread
threading.Thread(target=update_loop, daemon=True).start()

print("SmartLogger Simulator running on 0.0.0.0:5020")

# -----------------------------
# START MODBUS TCP SERVER
# -----------------------------
StartTcpServer(context, address=("0.0.0.0", 5020))