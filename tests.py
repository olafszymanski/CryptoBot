from config import PERCENTAGES, SUBSCRIPTIONS, TRADING_BUDGET_PERCENTAGE, LEVERAGE
from klines import Klines
from trade import backtest_strategy
from utils import timestamp_to_date


date = '13/10/2021'
interval = '30'

for subscription in SUBSCRIPTIONS:
    symbol = subscription.split('.')[2]
    print(f'Downloading data for {symbol}...')
    klines = Klines(symbol, date, interval)
    backtest_strategy(klines)

capital = 5250
PERCENTAGES.sort(key=lambda percent: percent['open_time'])
for index, percent in enumerate(PERCENTAGES):
    capital = capital + (capital * TRADING_BUDGET_PERCENTAGE * percent['percent'] * LEVERAGE * 0.99925)
    print(capital)
    PERCENTAGES[index]['open_time'] = timestamp_to_date(PERCENTAGES[index]['open_time'])

print(PERCENTAGES)