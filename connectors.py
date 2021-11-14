from config import SUBSCRIPTIONS, CLEARDB_HOST, CLEARDB_PORT, CLEARDB_NAME, CLEARDB_USERNAME, CLEARDB_PASSWORD
import mysql.connector
from pybit import HTTP, WebSocket
from websocket import WebSocketTimeoutException


client = HTTP('https://api.bybit.com')

connected = False
while not connected:
    try:
        web_socket = WebSocket('wss://stream.bybit.com/realtime_public', subscriptions=SUBSCRIPTIONS)
        connected = True
    except WebSocketTimeoutException as e:
        pass

def get_database_connection():
    connection = mysql.connector.connect(host=CLEARDB_HOST, port=CLEARDB_PORT, database=CLEARDB_NAME, user=CLEARDB_USERNAME, password=CLEARDB_PASSWORD)
    cursor = connection.cursor()
    return connection, cursor