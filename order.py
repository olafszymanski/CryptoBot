from enum import Enum
from config import INSERT_INTO_DATABASE, MAX_STOP_LOSS_PERCENTAGE, PROFIT_TO_RISK_RATIO, TEST_DATABASE, TAKE_PROFIT_PERCENTAGE, STOP_LOSS_PERCENTAGE
from connectors import get_database_connection
from utils import timestamp_to_date


class OrderType(Enum):
    UNDEFINED = -1
    LONG = 0
    SHORT = 1

    
    def __str__(self):
        return str(self.name)


class Order:
    def __init__(self):
        self.type = OrderType.UNDEFINED
        self.value = 0
        self.open_time = 0
        self.open = False
        self.take_profit_value = 0
        self.take_profit_percentage = 0
        self.stop_loss_value = 0
        self.stop_loss_percentage = 0


    def insert_into_database(self, kline, status, percent):
        if INSERT_INTO_DATABASE:
            connection, cursor = get_database_connection()
            cursor.execute(f"INSERT INTO {'test_contracts' if TEST_DATABASE else 'contracts'} (symbol, type, value, status, open_time, close_time, percent) VALUES ('{kline.symbol}', '{str(self.type)}', {self.value}, '{status}', {self.open_time}, {kline.open_time}, {percent});")
            connection.commit()
            cursor.close()
            connection.close()


    def test_make(self, type, kline, stop_loss_kline):
        self.type = type
        self.value = kline.close
        self.open_time = kline.open_time
        self.open = True
        if self.type == OrderType.LONG:
            self.stop_loss_value = self.value - self.value * MAX_STOP_LOSS_PERCENTAGE if self.value / stop_loss_kline.low > 1 + MAX_STOP_LOSS_PERCENTAGE else stop_loss_kline.low
            self.take_profit_value = self.value + (self.value - self.stop_loss_value) * PROFIT_TO_RISK_RATIO
        else:
            self.stop_loss_value = self.value + self.value * MAX_STOP_LOSS_PERCENTAGE if stop_loss_kline.high / self.value > 1 + MAX_STOP_LOSS_PERCENTAGE else stop_loss_kline.high
            self.take_profit_value = self.value - (self.stop_loss_value - self.value) * PROFIT_TO_RISK_RATIO
        self.take_profit_percentage = self.take_profit_value / self.value - 1
        self.stop_loss_percentage = 1 - self.stop_loss_value / self.value

    
    def make(self, type, kline, p_sar):
        self.type = type
        self.value = kline.close
        self.open_time = kline.open_time
        self.open = True
        if self.type == OrderType.LONG:
            p_sar_level_difference_percentage = (self.value - p_sar) / self.value
            if p_sar_level_difference_percentage > STOP_LOSS_PERCENTAGE:
                self.take_profit_percentage = 1 + TAKE_PROFIT_PERCENTAGE
                self.stop_loss_percentage = 1 - STOP_LOSS_PERCENTAGE
                self.take_profit_value = self.value * (1 + TAKE_PROFIT_PERCENTAGE)
                self.stop_loss_value = self.value * (1 - STOP_LOSS_PERCENTAGE)
            else:
                self.take_profit_percentage = 1 + p_sar_level_difference_percentage
                self.stop_loss_percentage = 1 - p_sar_level_difference_percentage
                self.take_profit_value = self.value * (1 + (p_sar_level_difference_percentage * 1.5))
                self.stop_loss_value = self.value * (1 - p_sar_level_difference_percentage)
        elif self.type == OrderType.SHORT:
            p_sar_level_difference_percentage = (p_sar - self.value) / p_sar
            if p_sar_level_difference_percentage > TAKE_PROFIT_PERCENTAGE:
                self.take_profit_percentage = 1 - TAKE_PROFIT_PERCENTAGE
                self.stop_loss_percentage = 1 + STOP_LOSS_PERCENTAGE
                self.take_profit_value = self.value * (1 - TAKE_PROFIT_PERCENTAGE)
                self.stop_loss_value = self.value * (1 + STOP_LOSS_PERCENTAGE)
            else:
                self.take_profit_percentage = 1 - p_sar_level_difference_percentage
                self.stop_loss_percentage = 1 + p_sar_level_difference_percentage
                self.take_profit_value = self.value * (1 - (p_sar_level_difference_percentage * 1.5))
                self.stop_loss_value = self.value * (1 + p_sar_level_difference_percentage)

        if INSERT_INTO_DATABASE:
            connection, cursor = get_database_connection()
            cursor.execute(f"INSERT INTO positions (symbol, type, open_time, value, take_profit, stop_loss) VALUES ('{kline.symbol}', '{str(self.type)}', {self.open_time}, {self.value}, {self.take_profit_percentage}, {self.stop_loss_percentage});")
            connection.commit()
            cursor.close()
            connection.close()


    def test_validate(self, kline):
        if self.type == OrderType.LONG:
            if kline.open >= self.take_profit_value or kline.close >= self.take_profit_value or kline.low >= self.take_profit_value or kline.high >= self.take_profit_value:
                percent = self.take_profit_percentage
                print(f'(TAKE PROFIT) WON LONG at {timestamp_to_date(self.open_time)} --- {timestamp_to_date(kline.open_time)}, {round(percent * 100, 2)}%')
                self.open = False

                self.insert_into_database(kline, 'WON', self.take_profit_percentage)
                
                return percent
            elif kline.open <= self.stop_loss_value or kline.close <= self.stop_loss_value or kline.low <= self.stop_loss_value or kline.high <= self.stop_loss_value:
                percent = self.stop_loss_percentage
                print(f'(STOP LOSS) LOST LONG at {timestamp_to_date(self.open_time)} --- {timestamp_to_date(kline.open_time)}, -{round(percent * 100, 2)}%')
                self.open = False

                self.insert_into_database(kline, 'LOST', self.stop_loss_percentage)
                
                return percent
        elif self.type == OrderType.SHORT:
            if kline.open <= self.take_profit_value or kline.close <= self.take_profit_value or kline.low <= self.take_profit_value or kline.high <= self.take_profit_value:
                percent = self.take_profit_percentage
                print(f'(TAKE PROFIT) WON SHORT at {timestamp_to_date(self.open_time)} --- {timestamp_to_date(kline.open_time)}, {-round(percent * 100, 2)}%')
                self.open = False

                self.insert_into_database(kline, 'WON', self.take_profit_percentage)
                
                return percent
            elif kline.open >= self.stop_loss_value or kline.close >= self.stop_loss_value or kline.low >= self.stop_loss_value or kline.high >= self.stop_loss_value:
                percent = self.stop_loss_percentage
                print(f'(STOP LOSS) LOST SHORT at {timestamp_to_date(self.open_time)} --- {timestamp_to_date(kline.open_time)}, {round(percent * 100, 2)}%')
                self.open = False

                self.insert_into_database(kline, 'LOST', self.stop_loss_percentage)

                return percent

        return 0


    def validate(self, kline):
        if self.type == OrderType.LONG:
            if kline.close >= self.take_profit_value:
                self.open = False
                self.insert_into_database(kline, 'WON', self.take_profit_percentage)
            elif kline.close <= self.stop_loss_value:
                self.open = False
                self.insert_into_database(kline, 'LOST', self.stop_loss_percentage)
        elif self.type == OrderType.SHORT:
            if kline.close <= self.take_profit_value:
                self.open = False
                self.insert_into_database(kline, 'WON', self.take_profit_percentage)
            elif kline.close >= self.stop_loss_value:
                self.open = False
                self.insert_into_database(kline, 'LOST', self.stop_loss_percentage)