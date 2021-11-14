import os

API_KEY = os.environ.get('API_KEY')
API_SECRET = os.environ.get('API_SECRET')

TEST_DATABASE = False
INSERT_INTO_DATABASE = False
CLEARDB_URL = os.environ.get('DB_URL')
CLEARDB_HOST = 'eu-cdbr-west-01.cleardb.com'
CLEARDB_PORT = 3306
CLEARDB_NAME = 'heroku_ab718dfceb697b6'
CLEARDB_USERNAME = os.environ.get('DB_USERNAME')
CLEARDB_PASSWORD = os.environ.get('DB_PASSWORD')

ONE_DAY_IN_SECONDS = 3600 * 24

SUBSCRIPTIONS = [
    # 'kline.30.BTCUSD',
    # 'kline.30.ETHUSD',
    # 'kline.30.EOSUSD',
    # 'kline.30.DOTUSD',
    # 'kline.30.XRPUSD',
    # 'candle.30.BITUSDT',
    'candle.30.BTCUSDT', 
    # 'candle.30.ETHUSDT', 
    # 'candle.30.SHIB1000USDT',
    # 'candle.30.ADAUSDT',
    # 'candle.30.BNBUSDT',
    # 'candle.30.XRPUSDT',
    # 'candle.30.SOLUSDT',
    # 'candle.30.DOTUSDT',
    # 'candle.30.DOGEUSDT',
    # 'candle.30.UNIUSDT',
    # 'candle.30.LUNAUSDT',
    # 'candle.30.AVAXUSDT',
    # 'candle.30.LINKUSDT',
    # 'candle.30.LTCUSDT',
    # 'candle.30.ALGOUSDT',
    # 'candle.30.BCHUSDT',
    # 'candle.30.ATOMUSDT',
    # 'candle.30.MATICUSDT',
    # 'candle.30.FILUSDT',
    # 'candle.30.ICPUSDT',
    # 'candle.30.ETCUSDT',
    # 'candle.30.XLMUSDT',
    # 'candle.30.VETUSDT',
    # 'candle.30.AXSUSDT',
    # 'candle.30.TRXUSDT',
    # 'candle.30.FTTUSDT',
    # 'candle.30.XTZUSDT',
    # 'candle.30.THETAUSDT',
    # 'candle.30.HBARUSDT',
    # 'candle.30.EOSUSDT',
    # 'candle.30.AAVEUSDT',
    # 'candle.30.NEARUSDT',
    # 'candle.30.FTMUSDT',
    # 'candle.30.KSMUSDT',
    # 'candle.30.OMGUSDT',
    # 'candle.30.DASHUSDT',
    # 'candle.30.COMPUSDT',
    # 'candle.30.ONEUSDT',
    # 'candle.30.CHZUSDT',
    # 'candle.30.XEMUSDT',
    # 'candle.30.SUSHIUSDT',
    # 'candle.30.DYDXUSDT',
    # 'candle.30.SRMUSDT',
    # 'candle.30.CRVUSDT',
    # 'candle.30.IOSTUSDT',
    # 'candle.30.CELRUSDT',
    # 'candle.30.ALICEUSDT',
    # 'candle.30.C98USDT',
]

MAXIMUM_LAST_MACD_CROSSOVER_POSITION = 1
MINIMUM_LAST_PARABOLIC_SAR_DIFFERENCE_PERCENTAGE = 0.1
SECONDS_TO_WAIT_FOR_CHECK = 240
TAKE_PROFIT_PERCENTAGE = 0.015
STOP_LOSS_PERCENTAGE = 0.01
MAX_STOP_LOSS_PERCENTAGE = 0.01
PROFIT_TO_RISK_RATIO = 2
TRADING_BUDGET_PERCENTAGE = 0.05
LEVERAGE = 25
PERCENTAGES = []