import asyncio
import time



class CycleExecutor:


    def __init__(
        self,
        modbus_manager,
        processing,
        fanout,
        error_store,
        interval=1.0
    ):

        self.modbus = modbus_manager

        self.processing = processing

        self.fanout = fanout

        self.error_store = error_store

        self.interval = interval

        self.running = True



    async def run(self):

        print("[CYCLE] started")


        while self.running:


            start = time.time()


            try:

                # -------------------------
                # INPUT
                # -------------------------

                raw = self.modbus.read_raw()


                if raw is None:

                    await self._wait(start)
                    continue



                # -------------------------
                # PROCESSING
                # -------------------------

                measurement = (
                    self.processing.process(raw)
                )


                if measurement is None:

                    await self._wait(start)
                    continue



                # -------------------------
                # FANOUT
                # -------------------------

                self.fanout.publish(
                    measurement
                )


            except Exception as e:


                print(
                    "[CYCLE ERROR]",
                    e
                )


                if self.error_store:

                    self.error_store.record(
                        component="cycle",
                        operation="execute",
                        error=e
                    )



            await self._wait(start)



    async def _wait(self,start):

        elapsed = time.time()-start

        delay=max(
            0,
            self.interval-elapsed
        )

        await asyncio.sleep(delay)



    def stop(self):

        self.running=False