import time
from datetime import datetime, timedelta
from dataclasses import fields

import pandas as pd

from src.binance_api import BinanceAPI
from src.create_backtest_database import ArcticDBOperator
from src.data_process.data_structure import BinanceTick



# TODO: functional format data
# TODO: functional time change
def format_kline_data(data):
    if data is not None or len(data) != 0:
        tick_fields = [field.name for field in fields(BinanceTick)]
        data = pd.DataFrame(data, columns=tick_fields)
        start_timestamp_ms = data.iloc[0]['open_time']
        start_timestamp_sec = start_timestamp_ms / 1000
        start_time = pd.to_datetime(start_timestamp_sec, unit='s')
        end_timestamp_ms= data.iloc[-1]['open_time']
        end_timestamp_ms = end_timestamp_ms / 1000
        end_time = pd.to_datetime(end_timestamp_ms, unit='s')
        # TODO: set_index will go wrong if some data missing, then the time and data length can not match.
        data = data.set_index(pd.date_range(start=start_time, end=end_time, freq='min'))
    return data


def write_coin_kline_into_database(symbol, start_time, end_time):
    binance_api = BinanceAPI()
    arctic_ops = ArcticDBOperator(url="lmdb://database", lib_name='Binance')

    old_time = datetime(1980, 1, 1)
    start_time_in_day = int(old_time.timestamp()) * 1000
    binance_date_data = binance_api.get_klines(symbol=symbol, startTime=start_time_in_day)
    start_unix_time_ms = binance_date_data[0][0]
    start_time = datetime.fromtimestamp(start_unix_time_ms/1000)
    end_time = datetime.now() + timedelta(minutes=1)

    current_date = start_time
    while current_date <= end_time:
        st = time.time()
        # next_date = current_date + timedelta(days=1)
        start_time_in_day = int(current_date.timestamp()) * 1000
        # end_time_in_day = int(next_date.timestamp()) * 1000
        
        binance_date_data = binance_api.get_klines(symbol=symbol, startTime=start_time_in_day)
        # TODO: make the exception right when out of time range or no data return
        if binance_date_data is None or len(binance_date_data) == 0:
            # print(f'Warning: data is {binance_date_data}')
            # continue
            break

        binance_date_data = format_kline_data(binance_date_data)
        arctic_ops.add(symbol, binance_date_data)

        current_date += timedelta(minutes=len(binance_date_data))
        elapsed_time = time.time() - st
        print(f'{current_date} - [{symbol}] - elapsed time {elapsed_time:.4f} second - {start_time} -> {end_time}')

def main():
    coin_list = [
        'ATAUSDT', 'PEPEUSDT', 'ETHUSDT', 'BTCUSDT', 'BNBUSDT'
    ]
    coin_list = [
        'WIFUSDT', 'BONKUSDT'
    ]
    total_time = {}
    for symbol in coin_list:
        st = time.time()
        write_coin_kline_into_database(symbol=symbol, start_time=None, end_time=None)
        elapsed_time = time.time() - st
        total_time[symbol] = elapsed_time

    arctic_ops = ArcticDBOperator(url="lmdb://database", lib_name='Binance')
    aa = arctic_ops.read(data_name='WIFUSDT', date_range=(datetime(2024, 4, 1, 0, 0), datetime(2024, 4, 15, 16, 17)))
    print(aa.data)
    print(total_time)

if __name__ == '__main__':
    main()