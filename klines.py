import pandas
from pandas.core.frame import DataFrame
from pandas_ta.overlap.supertrend import supertrend
from config import ONE_DAY_IN_SECONDS
from types import NoneType
from connectors import client
from datetime import datetime
from utils import timestamp_to_date
import numpy, talib, pandas_ta
from connectors import web_socket


class Kline:
    def __init__(self):
        self.symbol = ''
        self.interval = ''
        self.open_time = 0
        self.end_time = 0
        self.timestamp = 0
        self.open = 0
        self.high = 0
        self.low = 0
        self.close = 0
        self.volume = 0


    @staticmethod
    def init_from_rest_api(data):
        kline = Kline()
        kline.symbol = data['symbol']
        kline.interval = data['interval']
        kline.open_time = data['open_time']
        kline.open = float(data['open'])
        kline.high = float(data['high'])
        kline.low = float(data['low'])
        kline.close = float(data['close'])
        kline.volume = float(data['volume'])

        return kline


    @staticmethod
    def init_from_web_socket(subscription):
        kline = Kline()
        data = web_socket.fetch(subscription)
        if data:
            subscription = subscription.split('.')
            kline.symbol = subscription[2]
            kline.interval = subscription[1]
            kline.open_time = data['start']
            kline.end_time = data['end']
            kline.timestamp = data['timestamp'] / 1000000
            kline.open = float(data['open'])
            kline.high = float(data['high'])
            kline.low = float(data['low'])
            kline.close = float(data['close'])
            kline.volume = float(data['volume'])
            
            return kline

        return NoneType


    def __repr__(self):
        return f'Kline({self.symbol} | {timestamp_to_date(self.open_time)} | ${self.close})'


class Klines:
    def __init__(self, symbol, date_from, interval):
        self.klines = []

        timestamp = float(client.server_time()['time_now'])
        date_from_timestamp = datetime.timestamp(datetime.strptime(date_from, '%d/%m/%Y'))

        timestamp_delta = timestamp - date_from_timestamp
        remainder = timestamp_delta % ONE_DAY_IN_SECONDS
        nearest_day = timestamp_delta - remainder + ONE_DAY_IN_SECONDS
        iterations = nearest_day / ONE_DAY_IN_SECONDS

        hourly_updates = 60 / int(interval)
        limit = hourly_updates * 24
        multiplier = int(200 / limit)
        limit = hourly_updates * 24 * multiplier
        iterations = int(numpy.ceil(iterations / multiplier))

        for i in range(0, iterations):
            results = client.query_kline(**{'symbol': symbol, 'from': date_from_timestamp, 'interval': interval, 'limit': limit})['result']

            if results is not None:
                date_over = False
                for data in results:
                    kline = Kline.init_from_rest_api(data)
                    if i == 0 and kline.open_time > date_from_timestamp:
                        date_from_timestamp = kline.open_time
                        date_over = True
                    else:
                        self.klines.append(kline)
                if date_over:
                    date_from_timestamp = date_from_timestamp + 1800
                    date_over = False
                else:
                    date_from_timestamp = date_from_timestamp + (ONE_DAY_IN_SECONDS * multiplier)
            else:
                break


    def pop(self, index=0):
        self.klines.pop(index)


    def append(self, kline):
        self.klines.append(kline)


    def opens(self):
        return numpy.array([kline.open for kline in self.klines])


    def highs(self):
        return numpy.array([kline.high for kline in self.klines])
    

    def lows(self):
        return numpy.array([kline.low for kline in self.klines])


    def closes(self):
        return numpy.array([kline.close for kline in self.klines])


    def rsi(self, time_period=14):
        return talib.RSI(self.closes(), time_period)


    def ema(self, time_period=200):
        return talib.EMA(self.closes(), time_period)

    
    def dema(self, time_period=200):
        return talib.DEMA(self.closes(), time_period)


    def macd(self, fast_period=12, slow_period=26, signal_period=9):
        return talib.MACD(self.closes(), fast_period, slow_period, signal_period)


    def parabolic_sar(self, acceleration=0.02, max=0.2):
        return talib.SAR(self.highs(), self.lows(), acceleration, max)

    
    def stoch(self, time_period=14, k_period=1, d_period=3):
        return talib.STOCH(self.highs(), self.lows(), self.closes(), fastk_period=time_period, slowk_period=k_period, slowk_matype=0, slowd_period=d_period, slowd_matype=0)


    def stoch_rsi(self, time_period=14, k_period=3, d_period=3):
        closes = pandas.DataFrame(self.closes(), columns=['close'])

        return pandas_ta.stochrsi(closes['close'], length=time_period, rsi_length=time_period, k=k_period, d=d_period).to_numpy()


    def supertrend(self, time_period=10, multiplier=3):
        highs = pandas.DataFrame(self.highs(), columns=['high'])
        lows = pandas.DataFrame(self.lows(), columns=['low'])
        closes = pandas.DataFrame(self.closes(), columns=['close'])

        return pandas_ta.supertrend(highs['high'], lows['low'], closes['close'], length=time_period, multiplier=multiplier).to_numpy()

    
    def tsv(self, length=13, ma_length=7):
        tsv = []
        for i in range(0, len(self.klines)):
            if self.klines[i].close > self.klines[i - 1].close:
                tsv.append(self.klines[i].volume * (self.klines[i].close - self.klines[i - 1].close))
            elif self.klines[i].close < self.klines[i - 1].close:
                tsv.append(self.klines[i].volume * (self.klines[i].close - self.klines[i - 1].close))
            else:
                tsv.append(length)
        
        return tsv


    def __getitem__(self, key):
        return self.klines[key]


    def __delitem__(self, index):
        del self.klines[index]


    def __len__(self):
        return len(self.klines)


    def __repr__(self):
        return str([kline for kline in self.klines])