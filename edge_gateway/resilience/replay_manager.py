class ReplayManager:


    def __init__(
        self,
        persistent_store,
        handlers
    ):

        self.store = persistent_store

        self.handlers = handlers



    # =====================================================
    # REPLAY
    # =====================================================

    def replay(
        self,
        limit=100
    ):

        records = self.store.fetch_pending(
            limit
        )


        if not records:
            return



        synced_ids = []


        for row_id, channel, payload in records:


            try:

                handler = self.handlers.get(
                    channel
                )


                if not handler:
                    continue



                handler(payload)


                synced_ids.append(
                    row_id
                )


            except Exception as e:

                print(
                    "[REPLAY ERROR]",
                    channel,
                    e
                )



        if synced_ids:

            self.store.mark_synced(
                synced_ids
            )