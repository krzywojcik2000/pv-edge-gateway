from edge_gateway.domain.measurement import Measurement


class Normalizer:

    def normalize(self, m: Measurement):

        try:
            m.temperature = round(float(m.temperature), 2)
            m.ac_power = float(m.ac_power)
            m.dc_power = float(m.dc_power)
            m.energy = float(m.energy)

            return m

        except Exception as e:
            print("[NORMALIZER ERROR]", e)
            return None