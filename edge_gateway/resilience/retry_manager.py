# edge_gateway/resilience/retry_manager.py

import time


class RetryManager:

    def __init__(
        self,
        max_retries=3,
        backoff=0.5
    ):

        self.max_retries = max_retries
        self.backoff = backoff

    # =====================================================
    # PUBLIC API
    # =====================================================

    def execute(
        self,
        operation,
        *args,
        **kwargs
    ):

        last_error = None

        for attempt in range(self.max_retries):

            try:

                return operation(*args, **kwargs)

            except Exception as error:

                last_error = error

                if attempt < self.max_retries - 1:

                    time.sleep(
                        self.backoff * (attempt + 1)
                    )

        raise last_error