import pandas as pd


class CSVDataImporter:
    def __init__(self, file):
        self.data = pd.read_csv(file, index_col='datetime')


if __name__ == "__main__":
    importer = CSVDataImporter('/Users/jared/Dev/Tim/data/EUR_USD.csv')
