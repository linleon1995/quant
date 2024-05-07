
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


class GeneralTickData:
    def __init__(self, symbol, maxlen, mean_average_spans):
        max_time_span = max(mean_average_spans)
        if maxlen < max_time_span:
            maxlen = max(maxlen, max_time_span)
            print(f'Change the queue max length from {maxlen} to {max_time_span} to prevent caculation error.')
        self.maxlen = maxlen
        self.symbol = symbol
        self.ticks = deque(maxlen=self.maxlen)
        self.time = deque(maxlen=self.maxlen)
        self.mean_average_data_pool = {}
        self.signal_count = 0
        self.mean_average_spans = mean_average_spans
        for mean_average_span in mean_average_spans:
            self.mean_average_data_pool[mean_average_span] = deque(maxlen=self.maxlen)

    def put_tick(self, tick: float, unix_time):
        # TODO: if no time send in, use datetime.now() directly
        # TODO: complete the testing for different time format
        # TODO: consider get a complex tick (dataframe, class, numpy.array) or simple price (float)
        self.ticks.append(tick)
        if isinstance(unix_time, int):
            self.time.append(datetime.datetime.fromtimestamp(unix_time/1000))
        elif isinstance(unix_time, datetime.datetime):
            self.time.append(unix_time)

        # TODO:
        self.put_ma_data()
        
    def put_ma_data(self):
        cur_ticks_len = len(self.ticks)
        for ma_range in self.mean_average_spans:
            if cur_ticks_len >= ma_range and cur_ticks_len > 1:
                start = cur_ticks_len - ma_range
                ma_range_data = list(self.ticks)[start:]
                mean_average = sum(ma_range_data) / len(ma_range_data)
                self.mean_average_data_pool[ma_range].append(mean_average)

    @property
    def isValid(self):
        return len(self.ticks) >= max(self.mean_average_spans)