from typing import List

import requests
from collections import deque
import statistics
import time
from datetime import datetime

from pprint import pprint
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import requests
from typing import List

class BinanceAPI:
    def __init__(self, base_url='https://api.binance.com'):
        self.base_url = base_url

    # TODO: take care the exceptiion of return data more than 1000 counts.
    def get_klines(self, symbol='BTCUSDT', interval='1m', startTime=None, endTime=None, timeZone='8', limit=1440):
        url = f'{self.base_url}/api/v3/klines'
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': startTime,
            'endTime': endTime,
            'timeZone': timeZone,
            'limit': limit
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print("Error:", response.status_code)
            return None

    def get_ticker_price(self, symbol: str = None, symbols: List = None):
        url = f'{self.base_url}/api/v3/ticker/price'
        params = {
            'symbol': symbol,
            'symbols': symbols,
        }
        # if symbols is not None:
        #     url = f'{self.base_url}/api/v3/ticker/price?symbols={symbols}'
        # elif symbol is not None:
        #     url = f'{self.base_url}/api/v3/ticker/price?symbol={symbol}'
        # else:
        #     url = f'{self.base_url}/api/v3/ticker/price'
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None

    def rolling_window_price_change_stats(self, symbols, windowSize='1m'):
        symbols_string = self._get_symbols_string(symbols, maxlen=len(symbols), max_num_coins=len(symbols))
        symbols_string = symbols_string[0]
        url = f'{self.base_url}/api/v3/ticker?symbols={symbols_string}&windowSize={windowSize}'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None

    def get_usdt_ticker(self, symbols=None, bridge=None):
        new_ticker_price = []
        ticker_price = self.get_ticker_price(symbols=symbols)
        for coin in ticker_price:
            if coin['symbol'].endswith(bridge):
                new_ticker_price.append(coin)
        return new_ticker_price

    @staticmethod
    def _get_symbols_string(symbols: List, maxlen, max_num_coins, exclude_keys=None) -> List:
        if exclude_keys is not None:
            new_symbols = []
            for symbol in symbols:
                exclude_judge = []
                for key in exclude_keys:
                    exclude_judge.append(key not in symbol)
                if all(exclude_judge):
                    new_symbols.append(symbol)
            symbols = new_symbols

        symbol_groups = []
        maxlen = maxlen or len(symbols)
        max_num_coins = min(max_num_coins, len(symbols))
        for i in range(0, max_num_coins, maxlen):
            symbol_str = []
            for symbol in symbols[i:i+maxlen]:
                symbol_str.append(f'"{symbol}"')
            symbol_str = ','.join(symbol_str)
            symbol_str: str = f'[{symbol_str}]'
            symbol_groups.append(symbol_str)
        return symbol_groups


if __name__ == '__main__':
        
    # Example usage
    binance_api = BinanceAPI()
    # klines_data = binance_api.get_klines(symbol='BTCUSDT', startTime=1710832400000, endTime=1710839400000)
    klines_data = binance_api.get_klines(symbol='BTCUSDT')
    print(klines_data)

    # symbols_string = binance_api.get_symbols_string(symbols=['BTCUSDT', 'ETHUSDT'], maxlen=2, max_num_coins=2)
    # print(symbols_string)
    rolling_window_price = binance_api.rolling_window_price_change_stats(symbols=['BTCUSDT', 'ETHUSDT'])
    print(rolling_window_price)

    # binance_api.get_ticker_price(symbol='BTCUSDT')

