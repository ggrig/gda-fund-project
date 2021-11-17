import datetime
from log_json import log_json
from osbot_utils.utils.Json import str_to_json

class PriceBase(object):
    def __init__(self):
        self.log = log_json()
        self.lob_action_dictionary = {
            'skip'      : 1,
            'insert'    : 2,
            'remove'    : 3,
            'delete'    : 3,
            'update'    : 4
        }


    def get_lob_action_index(self, action:str):
        if not action in self.lob_action_dictionary:
            return 0
        return self.lob_action_dictionary[action]
