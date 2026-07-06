from edge_gateway.processing.decoder import Decoder
from edge_gateway.processing.normalizer import Normalizer
from edge_gateway.processing.enricher import Enricher


class ProcessingPipeline:

    def __init__(self):
        self.decoder = Decoder()
        self.normalizer = Normalizer()
        self.enricher = Enricher()

    # -----------------------------
    def process(self, raw: dict):

        m = self.decoder.decode(raw)
        if m is None:
            return None

        m = self.normalizer.normalize(m)
        if m is None:
            return None

        m = self.enricher.enrich(m)
        if m is None:
            return None

        return m