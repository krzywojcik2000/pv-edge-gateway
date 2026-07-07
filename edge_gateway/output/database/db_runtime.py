import asyncio


class DBRuntime:


    def __init__(
        self,
        db_writer,
        raw_manager,
        aggregation_manager,
        business_manager,
        alarm_manager,
        retry_manager,
        persistent_store,
        watchdog,
        error_store=None
    ):

        self.db = db_writer

        self.raw = raw_manager
        self.agg = aggregation_manager
        self.biz = business_manager
        self.alarm = alarm_manager

        self.retry = retry_manager

        self.store = persistent_store

        self.watchdog = watchdog

        self.error_store = error_store

        self.running = True



    # =====================================================
    # MAIN LOOP
    # =====================================================

    async def run(self):

        print("[DBRuntime] started")


        while self.running:


            try:

                # ---------------------------------
                # RESILIENCE MONITORING
                # ---------------------------------

                self.watchdog.check()



                # ---------------------------------
                # DATABASE PIPELINES
                # ---------------------------------

                self.process_raw()

                self.process_aggregation()

                self.process_business()

                self.process_alarm()



            except Exception as e:


                self._record_error(
                    component="DBRuntime",
                    operation="MAIN_LOOP",
                    error=e
                )



            await asyncio.sleep(0.1)



    # =====================================================
    # RAW
    # =====================================================

    def process_raw(self):

        if not self.raw.should_flush():
            return


        batch = self.raw.flush()


        self._execute(
            self.db.insert_raw_batch,
            batch,
            component="database",
            operation="insert_raw"
        )



    # =====================================================
    # AGGREGATION
    # =====================================================

    def process_aggregation(self):

        if not self.agg.should_flush():
            return


        aggregate = self.agg.flush()


        self._execute(
            self.db.insert_aggregate,
            aggregate,
            component="database",
            operation="insert_aggregate"
        )



    # =====================================================
    # BUSINESS
    # =====================================================

    def process_business(self):

        if not self.biz.should_flush():
            return


        business = self.biz.flush()


        self._execute(
            self.db.insert_business,
            business,
            component="database",
            operation="insert_business"
        )



    # =====================================================
    # ALARM
    # =====================================================

    def process_alarm(self):

        if not self.alarm.should_flush():
            return


        alarms = self.alarm.flush()


        self._execute(
            self.db.insert_alarm_batch,
            alarms,
            component="database",
            operation="insert_alarm"
        )



    # =====================================================
    # COMMON DATABASE EXECUTION
    # =====================================================

    def _execute(
        self,
        operation,
        payload,
        component,
        operation_name
    ):


        try:


            self.retry.execute(

                operation,

                payload,

                component=component,

                operation_name=operation_name,

                error_store=self.error_store
            )



        except Exception as e:



            print(
                f"[DBRuntime] {operation_name} failed"
            )


            # ---------------------------------
            # LAST RESORT
            # SAVE LOCALLY
            # ---------------------------------

            self.store.store(

                channel="database",

                payload=payload

            )


            self._record_error(

                component,

                operation_name,

                e

            )



    # =====================================================
    # ERROR RECORDING
    # =====================================================

    def _record_error(
        self,
        component,
        operation,
        error
    ):


        print(
            f"[{component}:{operation}] {error}"
        )


        if self.error_store:


            self.error_store.record(

                component=component,

                operation=operation,

                error=error

            )



    # =====================================================
    # CONTROL
    # =====================================================

    def stop(self):

        self.running = False