from edge_gateway.opcua.opcua_server import Server

class OPCUAServer:
    def __init__(self):
        self.server = Server()
        self.server.set_endpoint("opc.tcp://0.0.0.0:4840/edge_gateway/")

        self.namespace = self.server.register_namespace("PV_EDGE")

        objects = self.server.get_objects_node()

        self.farm = objects.add_object(self.namespace, "PV_Farm")
        self.inverter = self.farm.add_object(self.namespace, "KRK-01")

        self.temperature = self.inverter.add_variable(self.namespace, "Temperature", 0.0)
        self.dc_power = self.inverter.add_variable(self.namespace, "DC_Power", 0)
        self.ac_power = self.inverter.add_variable(self.namespace, "AC_Power", 0)
        self.energy = self.inverter.add_variable(self.namespace, "Energy", 0)
        self.alarm = self.inverter.add_variable(self.namespace, "Alarm", 0)

        self.temperature.set_writable()
        self.dc_power.set_writable()
        self.ac_power.set_writable()
        self.energy.set_writable()
        self.alarm.set_writable()

        print("[OPC UA] initialized")

    def start(self):
        self.server.start()
        print("[OPC UA] running on opc.tcp://0.0.0.0:4840")

    def update(self, data):
        self.temperature.set_value(data["temperature"])
        self.dc_power.set_value(data["dc_power"])
        self.ac_power.set_value(data["ac_power"])
        self.energy.set_value(data["energy"])
        self.alarm.set_value(int(data["alarm"]["raw"]))