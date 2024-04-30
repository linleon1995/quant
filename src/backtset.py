import time
from datetime import datetime, timedelta
import sys
print(sys.path)

import pandas as pd

from binance_api import BinanceAPI
from create_backtest_database import ArcticDBOperator
from strategies import mean_average, peak


# TODO: 假設前提為無資金假設，所有的交易都可以被完成，考慮這種情況的策略表現
class Evaluator:
    def __init__(self):
        self.init_money = {'USDT': 10000}

    def collect(self):
        pass

    def eval(self):
        pass


def main():
    arctic_ops = ArcticDBOperator(url="lmdb:///Leon/SideProject/quant", lib_name='Binance')
    DBobject = arctic_ops.read(data_name='WIFUSDT', date_range=(datetime(2024, 4, 1, 0, 0), datetime(2024, 4, 15, 16, 17)))
    evaluator = Evaluator()
    ma_strategy = mean_average.Strategy(
        ma_gap_rates=[1.008, 1.008],
        ma_grow_rates=[1.0005, 1.0005, 1.0005],
        count_threshold=5
    )
    for tick in DBobject.data.iterrows():
        timestamp, data = tick
        close_price = data['close_price']
        trade_singal = ma_strategy.run(close_price)
        evaluator.collect(trade_singal, tick)
        print(tick)
    evaluator.eval()


if __name__ == '__main__':
    main()