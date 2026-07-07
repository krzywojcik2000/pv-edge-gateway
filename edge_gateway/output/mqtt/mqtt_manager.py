import asyncio



class MQTTManager:


    def __init__(
        self,
        queue,
        publisher,
        retry_manager,
        error_store,
        farm_id
    ):

        self.queue = queue

        self.publisher = publisher

        self.retry = retry_manager

        self.error_store = error_store

        self.farm_id = farm_id

        self.running = True



    async def run(self):


        print("[MQTT] started")


        while self.running:


            try:

                item = await asyncio.to_thread(
                    self.queue.get
                )


                m = item.measurement


                payload = {

                    "farm_id": self.farm_id,

                    "temperature": m.temperature,

                    "dc_power": m.dc_power,

                    "ac_power": m.ac_power,

                    "energy": m.energy,

                    "alarm": {

                        "overtemperature":
                            m.alarm.overtemperature,

                        "overpower":
                            m.alarm.overpower,

                        "raw":
                            m.alarm.raw

                    }

                }


                self.retry.execute(

                    self.publisher.publish,

                    "pv/telemetry",

                    payload,

                    component="mqtt",

                    operation="publish",

                    error_store=self.error_store

                )


            except Exception as e:


                print(
                    "[MQTT ERROR]",
                    e
                )


                await asyncio.sleep(1)



    def stop(self):

        self.running=False