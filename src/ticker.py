

from typing import Any


from src.database_operator import ArcticDBOperator

class Ticker:
    def __init__(self, database_op: ArcticDBOperator, symbol='BTCUSDT', 
                 start_time='2021-01-01', end_time='2021-01-02', interval='1m'):
        self.symbol = symbol
        self.start_time = start_time
        self.end_time = end_time
        self.interval = interval
        self.database_op = database_op
        self.data = database_op.read(symbol, date_range=(start_time, end_time)).data
        self.idx = 0

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass

    # Define __iter__ to make the object an iterable
    def __iter__(self):
        return self

    # Define __next__ to generate the next value
    def __next__(self):
        if self.idx >= len(self.data):
            raise StopIteration
        else:
            self.idx += 1
            return self.data.iloc[self.idx-1]
        
    