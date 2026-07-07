import time


class Watchdog:


    def __init__(
        self,
        error_store=None,
        persistent_store=None
    ):

        self.error_store = error_store
        self.store = persistent_store


        self.status = {
            "db": "UNKNOWN",
            "buffer": "NORMAL",
            "errors": "NORMAL"
        }


    # =====================================================
    # MAIN CHECK
    # =====================================================

    def check(self):

        self._check_buffer()

        self._check_errors()

        return self.status



    # =====================================================
    # BUFFER MONITORING
    # =====================================================

    def _check_buffer(self):

        if not self.store:
            return


        count = self.store.count_pending()


        if count > 10000:

            self.status["buffer"] = "CRITICAL"


        elif count > 1000:

            self.status["buffer"] = "WARNING"


        else:

            self.status["buffer"] = "NORMAL"



    # =====================================================
    # ERROR MONITORING
    # =====================================================

    def _check_errors(self):

        if not self.error_store:
            return


        errors = self.error_store.count_recent(
            seconds=300
        )


        if errors > 100:

            self.status["errors"] = "CRITICAL"


        elif errors > 20:

            self.status["errors"] = "WARNING"


        else:

            self.status["errors"] = "NORMAL"