import requests
from collections import deque
import statistics
import time
from datetime import datetime

from pprint import pprint
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


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


def rolling_window_price_change_stats(symbols=None, windowSize='1m'):
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


def get_usdt_ticker(symbols=None):
    new_ticker_price = []
    ticker_price = get_binance_ticker_price(symbols=symbols)
    for coin in ticker_price:
        # if coin['symbol'].endswith('USDT'):
        new_ticker_price.append(coin)
    return new_ticker_price



def get_symbols_string(symbols: list):
    symbols = ','.join(symbols)
    symbols: str = f'[{symbols}]'
    return symbols

def main():
    max_num_coin = 3000
    cal_length = 5
    cal_length = max(2, cal_length)

    ticker_prices = get_usdt_ticker()
    symbols = []
    keep_symbol = ['BTCUSDT', 'ETHUSDT', 'ORDIUSDT', 'BONKUSDT', 'BSWUSDT', 
                   'MLNUSDT', 'DCRUSDT', 'OPUSDT', 'ASTRUSDT', 'NFPUSDT', 'SKLUSDT']
    # keep_symbol = ['OPUSDT', 'BTCUSDT']
    keep_symbol = None
    for idx, coin in enumerate(ticker_prices):
        if keep_symbol is not None:
            if coin['symbol'] not in keep_symbol:
                continue
        if idx > max_num_coin-1:
            break
        symbol = coin['symbol']
        symbols.append(f'"{symbol}"')
    # symbols = [f""{coin['symbol']}"" for coin in ticker_prices]
    symbols = get_symbols_string(symbols)
    prices, volumes = {}, {}
    diff, diff_vol = {}, {}
    axes = {}
    timestamp = []

    # MA diff
    time_periords = [7, 25, 99]
    # time_periords = [7, 8, 9]
    warm_up = max(time_periords)
    diif_rate = [1.001, 1.001]
    growth = 1
    acc_steps = 5
    MA_diff = MADiff(time_periords, diif_rate, growth, acc_steps)
    
    idx = 0
    max_earn = {}
    th = 10
    # fig, ax = plt.subplots(1, 1)
    colors = plt.cm.tab10.colors
    while True:
        # price_data = get_usdt_ticker(symbols)
        data = rolling_window_price_change_stats(symbols)
        if data is None:
            continue
        # print(idx)
        if idx == 0:
            for coin in data:
                axes[coin['symbol']] = plt.subplots(1,1)
        for coin in data:
            if coin['symbol'] not in volumes:
                volumes[coin['symbol']] = deque(maxlen=200)
            else:
                cur_volume = float(coin['volume'])
                volumes[coin['symbol']].append(cur_volume)

            if coin['symbol'] not in prices:
                prices[coin['symbol']] = deque(maxlen=200)
            else:
                cur_pcp = float(coin['openPrice'])
                prices[coin['symbol']].append(cur_pcp)

            if idx <= cal_length or idx <= warm_up:
                continue

            coin_prices = list(prices[coin['symbol']])
            cur_price = coin_prices[-1]
            mean_price = sum(coin_prices[:cal_length]) / len(coin_prices[:cal_length])
            std_price = statistics.stdev(coin_prices)

            coin_volumes = list(volumes[coin['symbol']])
            cur_volume = coin_volumes[-1]
            mean_volume = sum(coin_volumes[:cal_length]) / len(coin_volumes[:cal_length])
            std_volume = statistics.stdev(coin_volumes)

            if coin['symbol'] not in diff:
                diff[coin['symbol']] = []
            else:
                ratio = (cur_price - mean_price) / std_price if std_price != 0 else 0
                diff[coin['symbol']].append(ratio)

            if coin['symbol'] not in diff_vol:
                diff_vol[coin['symbol']] = []
            else:
                ratio = (cur_volume - mean_volume) / std_volume if std_volume != 0 else 0
                diff_vol[coin['symbol']].append(ratio)

            judge_ma_diff = MA_diff.run(coin_prices, coin['symbol'])
            if judge_ma_diff:
                send_msg(f"judge_ma_diff {datetime.now()} {coin['symbol']}: cur: {cur_price}")
        idx += 1
        timestamp.append(datetime.now())
        time.sleep(60)


if __name__ == '__main__':
    # main()
    main()
    # a = [10.272, 8.267, 9.786]
    # b = 10.747
    # m = statistics.mean(a)
    # std = statistics.stdev(a)
    # th = m + 3*std
    # print(b, th, m, std)

    # # Example usage
    # symbol_to_check = 'BTCUSDT'
    # ticker_price = get_binance_ticker_price()
    # new_ticker_price = []
    # last_ticker = None
    # for coin in ticker_price:
    #     if coin['symbol'].endswith('USDT'):
    #         # ticker_price = coin['price']
    #         new_ticker_price.append(coin)
    #         # if last_ticker is None:
    #         #     last_ticker = new_ticker_price
            
    # if ticker_price is not None:
    #     print(f"The current price of {symbol_to_check} is: {ticker_price}")
    # else:
    #     print("Failed to retrieve ticker price.")
