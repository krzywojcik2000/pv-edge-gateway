import asyncio


class Lifecycle:


    def __init__(
        self,
        cycle_executor,
        db_runtime,
        mqtt_manager,
        opcua_manager
    ):

        self.cycle_executor = cycle_executor
        self.db_runtime = db_runtime
        self.mqtt_manager = mqtt_manager
        self.opcua_manager = opcua_manager

        self.tasks = []

        self.running = True



    # ==================================================
    # PUBLIC START
    # ==================================================

    def start(self):

        try:

            asyncio.run(
                self._run()
            )


        except KeyboardInterrupt:

            print(
                "[LIFECYCLE] shutdown requested"
            )



    # ==================================================
    # MAIN ASYNC LOOP
    # ==================================================

    async def _run(self):


        print(
            "[LIFECYCLE] starting system"
        )


        self.tasks = [

            asyncio.create_task(
                self.cycle_executor.run(),
                name="cycle"
            ),

            asyncio.create_task(
                self.db_runtime.run(),
                name="database"
            ),

            asyncio.create_task(
                self.mqtt_manager.run(),
                name="mqtt"
            ),

            asyncio.create_task(
                self.opcua_manager.run(),
                name="opcua"
            )
        ]


        try:

            await asyncio.gather(
                *self.tasks
            )


        except Exception as e:

            print(
                "[LIFECYCLE ERROR]",
                e
            )


        finally:

            await self.shutdown()



    # ==================================================
    # GRACEFUL SHUTDOWN
    # ==================================================

    async def shutdown(self):


        print(
            "[LIFECYCLE] stopping components"
        )


        self.cycle_executor.stop()

        self.db_runtime.stop()

        self.mqtt_manager.stop()

        self.opcua_manager.stop()



        for task in self.tasks:

            if not task.done():

                task.cancel()



        await asyncio.sleep(0.1)


        print(
            "[LIFECYCLE] stopped"
        )