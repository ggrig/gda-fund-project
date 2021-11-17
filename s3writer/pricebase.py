import datetime
from log_json import log_json
from osbot_utils.utils.Json import str_to_json

class PriceBase(object):
    ORDER_TYPE_UNKNOWN  = 0
    ORDER_TYPE_LIMIT    = 1
    ORDER_TYPE_MARKET   = 2

    def __init__(self):
        self.log = log_json()
        self.lob_action_dictionary = {
            'skip'      : 1,
            'insert'    : 2,
            'remove'    : 3,
            'delete'    : 3,
            'update'    : 4
        }
        self.side_index_dictionalry = {
            'bid'       : 1,
            'Buy'       : 1,
            'ask'       : 2,
            'Sell'      : 2
        }


    def get_lob_action_index(self, action:str):
        if not action in self.lob_action_dictionary:
            return 0
        return self.lob_action_dictionary[action]

    def get_side_index(self, side:str):
        if not side in self.side_index_dictionalry:
            return 0
        return self.side_index_dictionalry[side]
