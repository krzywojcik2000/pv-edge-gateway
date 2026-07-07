from opcua import Server


class OPCUAIOError(Exception):
    pass



class OPCUAServer:


    def __init__(
        self,
        endpoint,
        farm_id="KRK-01"
    ):

        self.endpoint = endpoint
        self.farm_id = farm_id

        self.server = Server()

        self.started = False

        self._build_address_space()


    # =================================================
    # ADDRESS SPACE
    # =================================================

    def _build_address_space(self):

        self.server.set_endpoint(
            self.endpoint
        )


        self.namespace = (
            self.server.register_namespace(
                "PV_EDGE"
            )
        )


        objects = self.server.get_objects_node()


        farm = objects.add_object(
            self.namespace,
            "PV_Farm"
        )


        inverter = farm.add_object(
            self.namespace,
            self.farm_id
        )


        self.tags = {


            "temperature":
                inverter.add_variable(
                    self.namespace,
                    "Temperature",
                    0.0
                ),


            "dc_power":
                inverter.add_variable(
                    self.namespace,
                    "DC_Power",
                    0
                ),


            "ac_power":
                inverter.add_variable(
                    self.namespace,
                    "AC_Power",
                    0
                ),


            "energy":
                inverter.add_variable(
                    self.namespace,
                    "Energy",
                    0
                ),


            "alarm":
                inverter.add_variable(
                    self.namespace,
                    "Alarm",
                    0
                )

        }


        for tag in self.tags.values():

            tag.set_writable()



    # =================================================
    # LIFECYCLE
    # =================================================

    def start(self):

        try:

            self.server.start()

            self.started = True

            print(
                "[OPCUA] started"
            )


        except Exception as e:

            self.started = False

            raise OPCUAIOError(
                f"OPCUA start failed: {e}"
            )



    def stop(self):

        try:

            self.server.stop()

            self.started = False

            print(
                "[OPCUA] stopped"
            )


        except Exception as e:

            raise OPCUAIOError(
                f"OPCUA stop failed: {e}"
            )



    # =================================================
    # WRITE
    # =================================================

    def update(
        self,
        measurement
    ):


        if not self.started:

            raise OPCUAIOError(
                "OPCUA server not running"
            )


        try:


            self.tags["temperature"].set_value(
                measurement.temperature
            )


            self.tags["dc_power"].set_value(
                measurement.dc_power
            )


            self.tags["ac_power"].set_value(
                measurement.ac_power
            )


            self.tags["energy"].set_value(
                measurement.energy
            )


            self.tags["alarm"].set_value(
                int(measurement.alarm.raw)
            )



        except Exception as e:


            raise OPCUAIOError(
                f"OPCUA update failed: {e}"
            )