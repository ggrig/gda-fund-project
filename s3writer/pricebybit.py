import datetime
from log_json import log_json
from osbot_utils.utils.Json import str_to_json
from pricebase import PriceBase


TOPIC_BYBIT_INSURANCE   = "insurance"
TOPIC_BYBIT_KLINE       = "klineV2.1.BTCUSD"
TOPIC_BYBIT_OB200       = "orderBook_200.100ms.BTCUSD"
TOPIC_BYBIT_TRADE       = "trade"

class PriceBybit(PriceBase):
    def verify_trade_structure(self, json_data):
        if not 'topic' in json_data:
            return False

        if not 'data' in json_data:
            return False

        data = json_data['data']

        for entry in data:
            if not "trade_time_ms" in entry:
                return False
            if not "symbol" in entry:
                return False
            if not "price" in entry:
                return False
            break

        return True

    def verify_ob200_structure(self, json_data):
        if not 'topic' in json_data:
            return False

        if not 'data' in json_data:
            return False

        if not 'timestamp_e6' in json_data:
            return False

        data = json_data['data']

        if not 'insert' in data:
            return False

        for entry in data['insert']:
            if not "symbol" in entry:
                return False
            if not "price" in entry:
                return False
            break

        return True

    def verify_kline_structure(self, json_data):
        if not 'topic' in json_data:
            return False

        if not 'data' in json_data:
            return False

        if not 'timestamp_e6' in json_data:
            return False

        for entry in json_data['data']:
            if not "close" in entry:
                return False
            break

        return True

    def add_lob_action_data(self, json_data, lob_action_name:str, ):
        retval = []

        lob_actions = json_data['data'][lob_action_name]
        order_id = json_data['cross_seq']
        timestamp = int(json_data["timestamp_e6"]) / 1e3

        for entry in lob_actions:
            symbol  = entry["symbol"]
            price   = float(entry["price"])

            event = {
            'event_timestamp': datetime.datetime.fromtimestamp(timestamp / 1e3).isoformat(),
            'event_no': entry['id'],
            'quote_no': entry['id'],
            'end_of_event': False,
            'side': entry['side'],
            'lob_action': lob_action_name,
            'original_order_id': order_id,
            'order_id': order_id,
            'size': 0,
            'old_size': 0,
            'price': float(entry["price"]),
            'old_price': 0,
            'order_executed': False,
            'executed_size': 0,
            'order_type': 1,
            'time_in_force': 0
            }

            if 'size' in entry:
                event['size'] = entry['size']

            retval.append(event)

        return retval


    def process_json_data(self, topic:str, json_data):
        retval = []

        if TOPIC_BYBIT_INSURANCE    == topic:
            return retval
        elif TOPIC_BYBIT_KLINE      == topic:
            for entry in json_data['data']:
                symbol  = 'BTCUSD'
                price   = float(entry["close"])
                timestamp = int(json_data["timestamp_e6"]) / 1e3
                retval.append(self.getJson(symbol=symbol, price=price, timestamp=timestamp))
        elif TOPIC_BYBIT_OB200      == topic and self.verify_ob200_structure(json_data):

            retval += self.add_lob_action_data(json_data, 'delete')
            retval += self.add_lob_action_data(json_data, 'insert')
            retval += self.add_lob_action_data(json_data, 'update')

        elif TOPIC_BYBIT_TRADE      == topic and self.verify_trade_structure(json_data):
            data = json_data['data']
            for entry in data:
                symbol  = entry["symbol"]
                price   = float(entry["price"])
                timestamp = int(entry["trade_time_ms"])
                retval.append(self.getJson(symbol=symbol, price=price, timestamp=timestamp))

        return retval

if __name__ == '__main__':
    info = PriceBybit()

    # json_data = {"topic":"insurance.ETH","data":[{"currency":"ETH","timestamp":"2021-10-15T20:00:00Z","wallet_balance":4832029953542}]}
    # print(info.process_json_data(TOPIC_BYBIT_INSURANCE,json_data))

    # json_data = {"topic":"klineV2.1.BTCUSD","data":[{"start":1636174500,"end":1636174560,"open":61271,"close":61271,"high":61271,"low":61270.5,"volume":32951,"turnover":0.5377931700000002,"timestamp":1636174529019904,"confirm":"false","cross_seq":10550389298}],"timestamp_e6":1636174529026740}
    # print(info.process_json_data(TOPIC_BYBIT_KLINE,json_data))

    json_data = {"topic":"orderBook_200.100ms.BTCUSD","type":"delta","data":{"delete":[{"price":"61177.00","symbol":"BTCUSD","id":611770000,"side":"Sell"},{"price":"60955.50","symbol":"BTCUSD","id":609555000,"side":"Buy"}],"update":[{"price":"61017.00","symbol":"BTCUSD","id":610170000,"side":"Buy","size":1929},{"price":"60965.50","symbol":"BTCUSD","id":609655000,"side":"Buy","size":10149},{"price":"61076.00","symbol":"BTCUSD","id":610760000,"side":"Sell","size":18},{"price":"60916.50","symbol":"BTCUSD","id":609165000,"side":"Buy","size":3500}],"insert":[{"price":"61051.50","symbol":"BTCUSD","id":610515000,"side":"Sell","size":20000},{"price":"60902.00","symbol":"BTCUSD","id":609020000,"side":"Buy","size":335024}],"transactTimeE6":0},"cross_seq":10548595035,"timestamp_e6":1636156902211277}
    print(info.process_json_data(TOPIC_BYBIT_OB200,json_data))

    # json_data = {"topic":"trade.XRPUSD","data":[{"trade_time_ms":1634342763132,"timestamp":"2021-10-16T00:06:03.000Z","symbol":"XRPUSD","side":"Sell","size":1094,"price":1.1441,"tick_direction":"MinusTick","trade_id":"a6aa635a-89f7-5fd5-a29d-df9f0b13d937","cross_seq":3780829306},{"trade_time_ms":1634342763132,"timestamp":"2021-10-16T00:06:03.000Z","symbol":"XRPUSD","side":"Sell","size":200,"price":1.1441,"tick_direction":"ZeroMinusTick","trade_id":"ea2dcc4c-26f4-5a19-ba7b-2fc187b9b37b","cross_seq":3780829306},{"trade_time_ms":1634342763132,"timestamp":"2021-10-16T00:06:03.000Z","symbol":"XRPUSD","side":"Sell","size":4,"price":1.1441,"tick_direction":"ZeroMinusTick","trade_id":"aeaeaa83-79cb-5f80-887f-9e527153b6fb","cross_seq":3780829306},{"trade_time_ms":1634342763132,"timestamp":"2021-10-16T00:06:03.000Z","symbol":"XRPUSD","side":"Sell","size":9735,"price":1.1439,"tick_direction":"MinusTick","trade_id":"b3942a44-639c-5365-a82b-7ac67dd097e4","cross_seq":3780829306}]}
    # print(info.process_json_data(TOPIC_BYBIT_TRADE,json_data))

