import asyncio



class OPCUAManager:


    def __init__(
        self,
        queue,
        opcua_server,
        retry_manager,
        error_store=None
    ):

        self.queue = queue

        self.server = opcua_server

        self.retry = retry_manager

        self.error_store = error_store

        self.running = True



    async def run(self):


        print(
            "[OPCUA Manager] started"
        )


        while self.running:


            try:


                item = await asyncio.to_thread(
                    self.queue.get
                )


                self.retry.execute(

                    self.server.update,

                    item.measurement,

                    component="opcua",

                    operation="update",

                    error_store=self.error_store

                )


            except Exception as e:


                print(
                    "[OPCUA ERROR]",
                    e
                )


                await asyncio.sleep(1)



    def stop(self):

        self.running=False