import requests
from collections import deque
import statistics
import time
from datetime import datetime

from pprint import pprint
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

from src import load_config
from src import binance_api
from src import PriceDataProcesser
from src import Telegram_bot
from src.utils import seconds_to_time_string
from strategies import mean_average



def get_symbols(ticker_prices, max_num_coin):
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
    return symbols
    

# def main():
#     # config = load_config()
#     price_proc = PriceDataProcesser()
#     ma_strategy = mean_average_strategy.Strategy()

#     raw_data = binance_api.get_binance_raw_data()
#     proc_data = price_proc(raw_data)
#     singal = ma_strategy.run(proc_data)
#     Telegram_bot.send_msg('')
    

def main():
    # config
    maxlen = 100
    max_num_coins = 500
    cal_length = 5
    # time_interval = 60
    # interval_str = seconds_to_time_string(time_interval)
    interval_str = '1m'
    time_interval = 60
    cal_length = max(2, cal_length)

    ticker_prices = binance_api.get_usdt_ticker(bridge='USDT')
    symbols = [coin['symbol'] for idx, coin in enumerate(ticker_prices)]
    print(len(symbols))
    symbol_groups = binance_api.get_symbols_string(symbols, maxlen=maxlen, max_num_coins=max_num_coins, exclude_keys=['UPUSDT'])
    # symbols = None
    
    prices, volumes = {}, {}
    diff, diff_vol = {}, {}
    axes = {}
    timestamp = []

    # MA diff
    ma_time_periords = [7, 25, 99]
    queue_max_len = int(1.5*max(ma_time_periords))
    # time_periords = [7, 8, 9]
    warm_up = max(ma_time_periords)
    diif_rate = [1.001, 1.001]
    growth = 1
    acc_steps = 5
    ma_strategy = mean_average.Strategy(ma_time_periords, diif_rate, growth, acc_steps)
    
    idx = 0
    max_earn = {}
    th = 10
    # fig, ax = plt.subplots(1, 1)
    colors = plt.cm.tab10.colors
    while True:
        # price_data = get_usdt_ticker(symbols)
        start_time = time.time()
        for symbols in symbol_groups:
            data = binance_api.rolling_window_price_change_stats(symbols, windowSize=interval_str)
            if data is None:
                continue
            # # print(idx)
            # if idx == 0:
            #     for coin in data:
            #         axes[coin['symbol']] = plt.subplots(1,1)
            for coin in data:
                if coin['symbol'] not in volumes:
                    volumes[coin['symbol']] = deque(maxlen=queue_max_len)
                else:
                    cur_volume = float(coin['volume'])
                    volumes[coin['symbol']].append(cur_volume)

                if coin['symbol'] not in prices:
                    prices[coin['symbol']] = deque(maxlen=queue_max_len)
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

                ma_signal = ma_strategy.run(coin_prices, coin['symbol'])
                if ma_signal:
                    Telegram_bot.send_msg(f"{datetime.now()} - ma_signal - {coin['symbol']}: cur: {cur_price}")
        end_time = time.time()
        idx += 1
        timestamp.append(datetime.now())
        time.sleep(max(0.01, time_interval-(end_time-start_time)))


if __name__ == '__main__':
    main()