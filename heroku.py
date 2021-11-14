from config import SUBSCRIPTIONS
from klines import Klines
from order import Order
from trade import trade
import asyncio


date = '05/10/2021'
interval = '30'


async def main():
    all_klines = []
    all_orders = []
    all_order_prerequirements = []

    for subscription in SUBSCRIPTIONS:
        symbol = subscription.split('.')[2]
        all_klines.append(Klines(symbol, date, interval))
        print(f'Downloading data for {symbol}...')
        all_orders.append(Order())
        all_order_prerequirements.append({
            'long_wait': False,
            'long_timestamp': 0,
            'long_value': 0,
            'short_wait': False,
            'short_timestamp': 0,
            'short_value': 0
        })
        
    while True:
        for index, subscription in enumerate(SUBSCRIPTIONS):
            task = asyncio.create_task(trade(subscription, all_klines[index], all_orders[index], all_order_prerequirements[index]))
            all_klines[index], all_orders[index], all_order_prerequirements[index] = await task

            await asyncio.sleep(0.5 / len(SUBSCRIPTIONS))

asyncio.run(main())