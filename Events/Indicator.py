class Indicator:
    def __init__(self, name: str, instrument: str, payload):
        self.type = Indicator.get_name()
        self.name = name
        self.instrument = instrument
        self.payload = payload

    @staticmethod
    def get_name():
        return 'INDICATOR'
