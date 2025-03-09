import time
from dataclasses import fields
from datetime import datetime, timedelta

import pandas as pd
import pytz
from tqdm import tqdm

from src.binance_api import BinanceAPI
from src.create_backtest_database import ArcticDBOperator
from src.data_process.data_structure import BinanceTick


# TODO: complete the input, output, and testing
def format_kline_data(data):
    if data is not None or len(data) != 0:
        tick_fields = [field.name for field in fields(class_or_instance=BinanceTick)]
        data = pd.DataFrame(data=data, columns=tick_fields)
        start_timestamp_ms = data.iloc[0]['open_time']
        start_timestamp_sec = start_timestamp_ms / 1000
        end_timestamp_ms= data.iloc[-1]['open_time']
        end_timestamp_ms = end_timestamp_ms / 1000

        data["open_datetime"] = pd.to_datetime(data["open_time"], unit="ms")
        data = data.set_index(keys="open_datetime")
    return data


def write_coin_kline_into_database(binance_api, arctic_ops, symbol, start_time, end_time=None):
    # TODO: timezone problem (API get data in UTC, but the time is in local time), so we
    # need to convert the time to UTC time before sending to API
    start_time_in_day = int(start_time.timestamp()) * 1000
    binance_date_data = binance_api.get_klines(symbol=symbol, startTime=start_time_in_day)
    start_unix_time_ms = binance_date_data[0][0]
    actual_start_time = datetime.fromtimestamp(start_unix_time_ms/1000)
    start_time = actual_start_time
    if end_time is None:
        end_time = datetime.now()

    current_date = start_time
    print(f'{current_date} - [{symbol}] - second - {start_time} -> {end_time}')
    while current_date <= end_time:
        st = time.time()
        start_time_in_day = int(current_date.timestamp()) * 1000
        binance_date_data = binance_api.get_klines(symbol=symbol, startTime=start_time_in_day)
        # TODO: make the exception right when out of time range or no data return
        if binance_date_data is None or len(binance_date_data) == 0:
            break
        
        formated_binance_date_data = format_kline_data(binance_date_data)
        arctic_ops.add(symbol, formated_binance_date_data)

        current_date += timedelta(minutes=len(formated_binance_date_data))
        elapsed_time = time.time() - st
        print(f'[{symbol}] - {current_date} - elapsed time: {elapsed_time:.2f} s')
    print(f'[{symbol}] - finish')


def main():
    old_coin_list = [
        'ADAUSDT', 'WIFUSDT', 'ATAUSDT', 'PEPEUSDT', 'ETHUSDT', 'BTCUSDT', 'BNBUSDT', 'NEIROUSDT', 
        'PNUTUSDT', 'DOGEUSDT', 'TRUMPUSDT'
    ]
    binance_api = BinanceAPI()
    coin_list = binance_api.get_symbols()
    coin_list = [symbol for symbol in coin_list if 'USDT' in symbol and 'UP' not in symbol and 'DOWN' not in symbol]
    coin_list = set(coin_list) - set(old_coin_list)
    # ticker_prices = binance_api.get_usdt_ticker(bridge='USDT')
    # coin_list2 = [coin['symbol'] for coin in ticker_prices]

    start_time = datetime(year=2000, month=1, day=1, hour=0, minute=0)
    # end_time = datetime(2025, 3, 1, 0, 0)
    # end_time = None

    total_time = {}
    # TODO: 若存在資料庫，則不用再寫入，若部分資料缺失，則透過API補上
    # backtest_data: generator = manager.get_dataset(symbol='BTCUSDT', start_time=start_time, end_time=end_time)
    arctic_ops = ArcticDBOperator(url="lmdb://arctic_database", lib_name='Binance')

    # Write data into database
    error_coin = []
    for symbol in tqdm(coin_list):
        st = time.time()
        try:
            write_coin_kline_into_database(binance_api=binance_api, arctic_ops=arctic_ops, 
                                           symbol=symbol, start_time=start_time)
        except Exception as e:
            error_coin.append(symbol)
            print(e)
        elapsed_time = time.time() - st
        total_time[symbol] = elapsed_time

    print(f'Error coin: {error_coin}')


if __name__ == '__main__':
    main()