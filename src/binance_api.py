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


def get_binance_klines():
    url = 'https://api.binance.com/api/v3/klines'  # Replace 'https://api.example.com' with the actual API URL
    params = {
        'symbol': 'BTCUSDT',
        'interval': '1m',
        'startTime': 1710832400000,  # Provide the start time if needed
        'endTime': 1710839400000,    # Provide the end time if needed
        'timeZone': '8',    # Optional, default is UTC
        'limit': 1000       # Example limit, adjust as needed
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print("Error:", response.status_code)


def get_binance_ticker_price(symbol=None, symbols=None):
    if symbols is not None:
        url = f'https://api.binance.com/api/v3/ticker/price?symbols={symbols}'
    elif symbol is not None:
        url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}'
    else:
        url = f'https://api.binance.com/api/v3/ticker/price'

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}")
        return None


def rolling_window_price_change_stats(symbols, windowSize='1m'):
    spot_api_endpoint = 'https://api.binance.com'
    url = f'{spot_api_endpoint}/api/v3/ticker?symbols={symbols}&windowSize={windowSize}'
    # print(url)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # print(data)
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def get_usdt_ticker(symbols=None, bridge=None):
    new_ticker_price = []
    ticker_price = get_binance_ticker_price(symbols=symbols)
    for coin in ticker_price:
        if coin['symbol'].endswith(bridge):
            new_ticker_price.append(coin)
    return new_ticker_price



def get_symbols_string(symbols: list, maxlen, max_num_coins, exclude_keys=None) -> List:
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
    get_binance_klines()