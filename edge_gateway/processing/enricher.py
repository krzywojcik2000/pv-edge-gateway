from datetime import datetime
from edge_gateway.domain.measurement import Measurement


class Enricher:

    def enrich(self, m: Measurement):

        try:
            m.timestamp = datetime.utcnow()

            dc = m.dc_power
            ac = m.ac_power

            if dc and dc > 0:
                m.efficiency = (ac / dc) * 100
            else:
                m.efficiency = 0.0

            return m

        except Exception as e:
            print("[ENRICHER ERROR]", e)
            return None