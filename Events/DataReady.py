class DataReady:
    def __init__(self):
        self.type = DataReady.get_name()

    @staticmethod
    def get_name():
        return 'DATAREADY'
