from datetime import datetime

from rx.subjects import Subject

from Indicator.Candle import Candle
from DataImporter import CSVDataImporter
from Events.Tick import Tick
from Indicator.Breakout import Breakout
from Portfolio.Portfolio import Portfolio
from Strategies.PricePredictor import PricePredictor

message_broker = Subject()

instrument = "EUR_USD"

portfolio = Portfolio(message_broker, initial_funds=100000)

indicator = Breakout(message_broker, length=5)

PricePredictor("/Users/jared/Dev/Tim/research/linear_regressesor.pkl", message_broker, instrument=instrument)

importer = CSVDataImporter('/Users/jared/Dev/Tim/data/EUR_USD_very_long.csv')

message_broker.filter(lambda x: x.type == 'MARKET').subscribe(lambda x: print("Market order"))

for index, row in importer.data.iterrows():
    date = datetime.strptime(index, "%Y-%m-%dT%H:%M:%S")
#    print(date)

    message_broker.on_next(Tick(candle=Candle(open=row['open'], high=row['high'], low=row['low'], close=row['close'], volume=row['volume']), granularity='H', date=date, instrument=instrument))
#    time.sleep(.01)

portfolio.print_pnl()

input("Press Enter to terminate...")
