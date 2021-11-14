from types import NoneType
from config import MAXIMUM_LAST_MACD_CROSSOVER_POSITION, MINIMUM_LAST_PARABOLIC_SAR_DIFFERENCE_PERCENTAGE, PERCENTAGES, SECONDS_TO_WAIT_FOR_CHECK
from order import OrderType, Order
from klines import Kline
from utils import timestamp_to_date


def backtest_strategy(klines):
    order = Order()

    ema = klines.ema()
    stoch = klines.stoch()

    over_sold = -1
    place_long = -1

    for i in range(0, len(klines)):                
        if order.open:
            percent = order.test_validate(klines[i])
            if percent != 0:
                PERCENTAGES.append({
                    'symbol': klines[i].symbol,
                    'open_time': order.open_time,
                    'close_time': timestamp_to_date(klines[i].open_time),
                    'percent': percent
                })
    
        if stoch[0][i] > 80 and stoch[1][i] > 80:
            over_sold = 1
        elif stoch[0][i] < 20 and stoch[1][i] < 20:
            over_sold = 0

        if over_sold == 1 and (stoch[0][i] > 20 and stoch[1][i] > 20 and stoch[0][i] < 80 and stoch[1][i] < 80):
            place_long = 1
            over_sold = -1
        elif over_sold == 0 and (stoch[0][i] > 20 and stoch[1][i] > 20 and stoch[0][i] < 80 and stoch[1][i] < 80):
            place_long = 0
            over_sold = -1
        else:
            place_long = -1

        if klines[i].close > ema[i]:
            if not order.open and place_long == 1:
                lowest_low_kline = min(klines[i - 10:i], key=lambda kline: kline.low)
                order.test_make(OrderType.LONG, klines[i], lowest_low_kline)
                over_sold = -1
                place_long = -1
        elif klines[i].close < ema[i]:
            if not order.open and place_long == 0:
                highest_high_kline = max(klines[i - 10:i], key=lambda kline: kline.high)
                order.test_make(OrderType.SHORT, klines[i], highest_high_kline)
                over_sold = -1
                place_long = -1

# Real time trading uses a different strategy for now.
async def trade(subscription, _klines, _order, _order_prerequirements):
    klines = _klines
    order = _order
    order_prerequirements = _order_prerequirements

    kline = Kline.init_from_web_socket(subscription)
    if kline is not NoneType and klines[-1] is not NoneType:
        if kline.open != klines[-1].open:
            klines.pop()
            klines.append(kline)
        else:
            del klines[-1]
            klines.append(kline)

        ema = klines.ema()
        _, _, macd_histogram = klines.macd()
        p_sar = klines.parabolic_sar()

        if order.open:
            order.validate(kline)
        else:
            if order_prerequirements['long_timestamp'] > kline.end_time:
                order_prerequirements['long_wait'] = False
                order_prerequirements['long_timestamp'] = 0
                order_prerequirements['long_value'] = 0
            
            if order_prerequirements['short_timestamp'] > kline.end_time:
                order_prerequirements['short_wait'] = False
                order_prerequirements['short_timestamp'] = 0
                order_prerequirements['short_value'] = 0

            if kline.timestamp > order_prerequirements['long_timestamp'] and kline.close > ema[-1]:
                if macd_histogram[-1] > 0 and macd_histogram[-1 - MAXIMUM_LAST_MACD_CROSSOVER_POSITION] < 0:
                    p_sar_difference_percentage = (p_sar[-1] - p_sar[-2]) / p_sar[-1] * 100
                    if kline.close > p_sar[-1] and p_sar_difference_percentage > MINIMUM_LAST_PARABOLIC_SAR_DIFFERENCE_PERCENTAGE:
                        if order.open_time != kline.open_time:
                            if order_prerequirements['long_wait']:
                                if kline.close < order_prerequirements['long_value']:
                                    order.make(OrderType.LONG, kline, p_sar[-1])
                                    order_prerequirements['long_wait'] = False
                                    order_prerequirements['long_timestamp'] = 0
                                    order_prerequirements['long_value'] = 0
                                else:
                                    order_prerequirements['long_timestamp'] = kline.timestamp + SECONDS_TO_WAIT_FOR_CHECK / 2
                            else:
                                order_prerequirements['long_wait'] = True
                                order_prerequirements['long_timestamp'] = kline.timestamp + SECONDS_TO_WAIT_FOR_CHECK
                                order_prerequirements['long_value'] = kline.close

            if kline.timestamp > order_prerequirements['short_timestamp'] and kline.close < ema[-1]:
                if macd_histogram[-1] < 0 and macd_histogram[-1 - MAXIMUM_LAST_MACD_CROSSOVER_POSITION] > 0:
                    p_sar_difference_percentage = (p_sar[-2] - p_sar[-1]) / p_sar[-2] * 100
                    if kline.close < p_sar[-1] and p_sar_difference_percentage > MINIMUM_LAST_PARABOLIC_SAR_DIFFERENCE_PERCENTAGE:
                        if order.open_time != kline.open_time:
                            if order_prerequirements['short_wait']:
                                if kline.close > order_prerequirements['short_value']:
                                    order.make(OrderType.SHORT, kline, p_sar[-1])
                                    order_prerequirements['short_wait'] = False
                                    order_prerequirements['short_timestamp'] = 0
                                    order_prerequirements['short_value'] = 0
                                else:
                                    order_prerequirements['short_timestamp'] = kline.timestamp + SECONDS_TO_WAIT_FOR_CHECK / 2
                            else:
                                order_prerequirements['short_wait'] = True
                                order_prerequirements['short_timestamp'] = kline.timestamp + SECONDS_TO_WAIT_FOR_CHECK                                       
                                order_prerequirements['short_value'] = kline.close

        print(kline)

    return klines, order, order_prerequirements