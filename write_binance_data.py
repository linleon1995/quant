import time
from dataclasses import fields
from datetime import datetime, timedelta

import pandas as pd
import pytz

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
        
        # local_tz = pytz.timezone('Asia/Taipei')  # UTC+8 timezone
        # start_time = local_tz.localize(start_time).astimezone(pytz.utc)
        # end_time = local_tz.localize(end_time).astimezone(pytz.utc)

        # TODO: set_index will go wrong if some data missing, then the time and data length can not match.
        data = data.set_index(pd.date_range(start=start_time, end=end_time, freq='min'))
    return data


def write_coin_kline_into_database(arctic_ops, symbol, start_time, end_time=None):
    # TODO: timezone problem (API get data in UTC, but the time is in local time), so we
    # need to convert the time to UTC time before sending to API
    binance_api = BinanceAPI()

    # old_time = datetime(1980, 1, 1)
    start_time_in_day = int(start_time.timestamp()) * 1000
    binance_date_data = binance_api.get_klines(symbol=symbol, startTime=start_time_in_day)
    start_unix_time_ms = binance_date_data[0][0]
    start_time = datetime.fromtimestamp(start_unix_time_ms/1000)
    if end_time is None:
        end_time = datetime.now()

    current_date = start_time
    print(f'{current_date} - [{symbol}] - second - {start_time} -> {end_time}')
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

        formated_binance_date_data = format_kline_data(binance_date_data)
        arctic_ops.add(symbol, formated_binance_date_data)

        current_date += timedelta(minutes=len(formated_binance_date_data))
        elapsed_time = time.time() - st
        print(f'[{symbol}] - {current_date} - elapsed time: {elapsed_time:.2f} s')

def main():
    coin_list = [
        'ATAUSDT', 'PEPEUSDT', 'ETHUSDT', 'BTCUSDT', 'BNBUSDT', 'WIFUSDT', 'NEIROUSDT', 'PNUTUSDT'
    ]
    # coin_list = [
    #     'FTTUSDT', 'DOGEUSDT'
    # ]
    binance_api = BinanceAPI()
    ticker_prices = binance_api.get_usdt_ticker(bridge='USDT')
    coin_list = [coin['symbol'] for coin in ticker_prices]

    start_time = datetime(2024, 1, 1, 0, 0)
    end_time = datetime(2024, 10, 31, 0, 0)
    end_time = None
    total_time = {}
    # TODO: BinanceDataManager
    # 若存在資料庫，則不用再寫入，若部分資料缺失，則透過API補上
    # backtest_data: generator = manager.get_dataset(symbol='BTCUSDT', start_time=start_time, end_time=end_time)
    arctic_ops = ArcticDBOperator(url="lmdb://arctic_database", lib_name='Binance')

    # Write data into database
    error_coin = []
    for symbol in coin_list:
        st = time.time()
        try:
            write_coin_kline_into_database(arctic_ops, symbol=symbol, 
                                        start_time=start_time, end_time=end_time)
        except Exception as e:
            error_coin.append(symbol)
        elapsed_time = time.time() - st
        total_time[symbol] = elapsed_time

    # # Read data from database
    # arctic_obj = arctic_ops.read(data_name=coin_list[0], start_time=start_time, end_time=end_time)
    # print(arctic_obj.data)
    # print(total_time)
    print(error_coin)

if __name__ == '__main__':
    main()