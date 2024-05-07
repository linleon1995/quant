
from dataclasses import dataclass
from collections import deque
import datetime


@dataclass
class BaseCoinMeta:
    pass


@dataclass
class MACoinMeta:
    pass



@dataclass
class CoinData:
    raw_data: deque
    data_pool: dict


class MAMeta:
    def __init__(self, symbol, maxlen, ma_range_list):
        self.symbol = symbol
        self.ticks = deque(maxlen=maxlen)
        self.time = deque(maxlen=maxlen)
        self.ma_data_pool = {}
        self.signal_count = 0
        self.ma_ranges = ma_range_list
        for ma_range in ma_range_list:
            self.ma_data_pool[ma_range] = deque(maxlen=maxlen)

    def put_tick(self, tick, unix_time):
        self.ticks.append(tick)
        if isinstance(unix_time, int):
            self.time.append(datetime.datetime.fromtimestamp(unix_time/1000))
        elif isinstance(unix_time, datetime.datetime):
            self.time.append(unix_time)

        # TODO:
        self.put_ma_data()
        
    def put_ma_data(self):
        cur_ticks_len = len(self.ticks)
        for ma_range in self.ma_ranges:
            if cur_ticks_len >= ma_range and cur_ticks_len > 1:
                start = cur_ticks_len - ma_range
                ma_range_data = list(self.ticks)[start:]
                mean_average = sum(ma_range_data) / len(ma_range_data)
                self.ma_data_pool[ma_range].append(mean_average)

    @property
    def isValid(self):
        return len(self.ticks) >= max(self.ma_ranges)