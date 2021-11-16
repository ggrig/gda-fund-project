import datetime
from log_json import log_json
from osbot_utils.utils.Json import str_to_json

class PriceBase(object):
    def __init__(self):
        self.log = log_json()
        self.normalized = {
        'event_timestamp': 0,
        'event_no': 0,
        'quote_no': 0,
        'end_of_event': False,
        'side': '',
        'lob_action': '',
        'original_order_id': '',
        'order_id': '',
        'size': 0,
        'old_size': 0,
        'price': 0,
        'old_price': 0,
        'order_executed': False,
        'executed_size': 0,
        'order_type': 1,
        'time_in_force': 0
        }

    def getJson(self, symbol:str, price:float, timestamp:int):
        date = datetime.datetime.fromtimestamp(timestamp / 1e3).isoformat()
        return {
            "symbol"    : symbol,
            "price"     : price,
            "timestamp" : date
        }

