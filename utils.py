from datetime import datetime


def timestamp_to_date(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M:%S')