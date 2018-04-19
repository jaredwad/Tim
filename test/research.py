from DataImporter import CSVDataImporter
import matplotlib.pyplot as plt

importer = CSVDataImporter('/Users/jared/Dev/Tim/data/EUR_USD.csv')


importer.data["close"].plot(kind='line')

plt.show()
