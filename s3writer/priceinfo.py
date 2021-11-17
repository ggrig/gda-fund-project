from datetime import datetime
from datetime import timezone
from log_json import log_json
from osbot_utils.utils.Json import str_to_json, json_to_str
from pricebybit import PriceBybit, TOPIC_BYBIT_INSURANCE, TOPIC_BYBIT_KLINE, TOPIC_BYBIT_OB200, TOPIC_BYBIT_TRADE
from pricebybitusdt import PriceBybitUSDT, TOPIC_BYBIT_USDT_CANDLE, TOPIC_BYBIT_USDT_OB200, TOPIC_BYBIT_USDT_TRADE
from pricebinance import PriceBinance, TOPIC_BINANCE_BINANCE
from pricecoinbase import PriceCoinbase, TOPIC_COINBASE_BTCUSD, TOPIC_COINBASE_ETHUSD

EX_BYBIT        = "ByBit"
EX_BYBIT_USDT   = "ByBit-USDT"
EX_BINANCE      = "Binanace"
EX_COINBASE     = "Coinbase"

class PriceInfo(object):
    def __init__(self):
        self.log = log_json()

    def getJson(self, symbol:str, price:float, timestamp:int):
        date = datetime.fromtimestamp(timestamp / 1e3).isoformat().replace(timezone.utc)
        return {
            "symbol"    : symbol,
            "price"     : price,
            "timestamp" : timestamp       
        }

    def verify_str_is_json(self, data:str):
        length = len(data)
        if length < 3:
            return False
        if data[0] != '{' or data[length - 2] != '}' or data[length - 1] != '\n':
            return False
        return True

    def process_raw_data(self, exchange:str, topic:str, data:str):
        if not self.verify_str_is_json(data):
            return []

        json_data = {}
        try:
            json_data = str_to_json(data)
        except Exception as ex:
            self.log.create("ERROR", str(ex))
            return []

        if EX_BYBIT         == exchange:        return PriceBybit().process_json_data(topic=topic, json_data=json_data)
        if EX_BYBIT_USDT    == exchange:        return PriceBybitUSDT().process_json_data(topic=topic, json_data=json_data)
        if EX_COINBASE      == exchange:        return PriceCoinbase().process_json_data(topic=topic, json_data=json_data)
        if EX_BINANCE       == exchange:        return PriceBinance().process_json_data(topic=topic, json_data=json_data)

        self.log.create("ERROR", f'{exchange} EXCHANGE NOT SUPPOTED')
        return []

if __name__ == '__main__':
    info = PriceInfo()

    raw_data = "{\"topic\":\"insurance.ETH\",\"data\":[{\"currency\":\"ETH\",\"timestamp\":\"2021-10-15T20:00:00Z\",\"wallet_balance\":4832029953542}]}\n"
    print(info.process_raw_data(EX_BYBIT,TOPIC_BYBIT_INSURANCE,raw_data))
    print('')

    raw_data = "{\"topic\":\"klineV2.1.BTCUSD\",\"data\":[{\"start\":1636174500,\"end\":1636174560,\"open\":61271,\"close\":61271,\"high\":61271,\"low\":61270.5,\"volume\":32951,\"turnover\":0.5377931700000002,\"timestamp\":1636174529019904,\"confirm\":false,\"cross_seq\":10550389298}],\"timestamp_e6\":1636174529026740}\n"
    print(info.process_raw_data(EX_BYBIT,TOPIC_BYBIT_KLINE,raw_data))
    print('')

    raw_data = "{\"topic\":\"orderBook_200.100ms.BTCUSD\",\"type\":\"delta\",\"data\":{\"delete\":[{\"price\":\"61177.00\",\"symbol\":\"BTCUSD\",\"id\":611770000,\"side\":\"Sell\"},{\"price\":\"60955.50\",\"symbol\":\"BTCUSD\",\"id\":609555000,\"side\":\"Buy\"}],\"update\":[{\"price\":\"61017.00\",\"symbol\":\"BTCUSD\",\"id\":610170000,\"side\":\"Buy\",\"size\":1929},{\"price\":\"60965.50\",\"symbol\":\"BTCUSD\",\"id\":609655000,\"side\":\"Buy\",\"size\":10149},{\"price\":\"61076.00\",\"symbol\":\"BTCUSD\",\"id\":610760000,\"side\":\"Sell\",\"size\":18},{\"price\":\"60916.50\",\"symbol\":\"BTCUSD\",\"id\":609165000,\"side\":\"Buy\",\"size\":3500}],\"insert\":[{\"price\":\"61051.50\",\"symbol\":\"BTCUSD\",\"id\":610515000,\"side\":\"Sell\",\"size\":20000},{\"price\":\"60902.00\",\"symbol\":\"BTCUSD\",\"id\":609020000,\"side\":\"Buy\",\"size\":335024}],\"transactTimeE6\":0},\"cross_seq\":10548595035,\"timestamp_e6\":1636156902211277}\n"
    print(json_to_str(info.process_raw_data(EX_BYBIT,TOPIC_BYBIT_OB200,raw_data)))
    print('')

    raw_data = "{\"topic\":\"trade.XRPUSD\",\"data\":[{\"trade_time_ms\":1634342763132,\"timestamp\":\"2021-10-16T00:06:03.000Z\",\"symbol\":\"XRPUSD\",\"side\":\"Sell\",\"size\":1094,\"price\":1.1441,\"tick_direction\":\"MinusTick\",\"trade_id\":\"a6aa635a-89f7-5fd5-a29d-df9f0b13d937\",\"cross_seq\":3780829306},{\"trade_time_ms\":1634342763132,\"timestamp\":\"2021-10-16T00:06:03.000Z\",\"symbol\":\"XRPUSD\",\"side\":\"Sell\",\"size\":200,\"price\":1.1441,\"tick_direction\":\"ZeroMinusTick\",\"trade_id\":\"ea2dcc4c-26f4-5a19-ba7b-2fc187b9b37b\",\"cross_seq\":3780829306},{\"trade_time_ms\":1634342763132,\"timestamp\":\"2021-10-16T00:06:03.000Z\",\"symbol\":\"XRPUSD\",\"side\":\"Sell\",\"size\":4,\"price\":1.1441,\"tick_direction\":\"ZeroMinusTick\",\"trade_id\":\"aeaeaa83-79cb-5f80-887f-9e527153b6fb\",\"cross_seq\":3780829306},{\"trade_time_ms\":1634342763132,\"timestamp\":\"2021-10-16T00:06:03.000Z\",\"symbol\":\"XRPUSD\",\"side\":\"Sell\",\"size\":9735,\"price\":1.1439,\"tick_direction\":\"MinusTick\",\"trade_id\":\"b3942a44-639c-5365-a82b-7ac67dd097e4\",\"cross_seq\":3780829306}]}\n"
    print(json_to_str(info.process_raw_data(EX_BYBIT,TOPIC_BYBIT_TRADE,raw_data)))
    print('')

    raw_data = "{\"key\":\"none\"}"
    print(info.process_raw_data(EX_BYBIT_USDT,TOPIC_BYBIT_USDT_CANDLE,raw_data))
    print('')

    raw_data = "{\"key\":\"none\"}"
    print(info.process_raw_data(EX_BYBIT_USDT,TOPIC_BYBIT_USDT_OB200,raw_data))
    print('')

    raw_data = "{\"key\":\"none\"}"
    print(info.process_raw_data(EX_BYBIT_USDT,TOPIC_BYBIT_USDT_TRADE,raw_data))
    print('')

    raw_data = "{\"key\":\"none\"}"
    print(info.process_raw_data(EX_COINBASE,TOPIC_COINBASE_BTCUSD,raw_data))
    print('')

    raw_data = "{\"key\":\"none\"}"
    print(info.process_raw_data(EX_COINBASE,TOPIC_COINBASE_ETHUSD,raw_data))
    print('')

    raw_data = "{\"stream\":\"btcusdt@aggTrade\",\"data\":{\"e\":\"aggTrade\",\"E\":1634390640539,\"a\":874355956,\"s\":\"BTCUSDT\",\"p\":\"60602.22\",\"q\":\"0.002\",\"f\":1546375311,\"l\":1546375311,\"T\":1634390640533,\"m\":false}}"
    print(info.process_raw_data(EX_BINANCE,TOPIC_BINANCE_BINANCE,raw_data))
    print('')
