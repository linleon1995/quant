import requests
from collections import deque
import statistics
import time
from datetime import datetime

from pprint import pprint
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


class MADiff:
    def __init__(self, time_periords, diff_rate, growth, acc_steps):
        self.time_periords = time_periords
        self.diff_rate = diff_rate
        self.growth = growth
        self.acc_steps = acc_steps
        self.achieve_count = 0
        self.last_sma_data = {}

    def run(self, data, symbol):
        judge, sma_data = self.cal_ma_diff(data)
        if judge:
            self.achieve_count += 1
            if symbol not in self.last_sma_data:
                self.last_sma_data[symbol] = sma_data
                growing = [True]
            else:
                growing = []
                for cur_sma, last_sma in zip(sma_data, self.last_sma_data[symbol]):
                    growing.append(cur_sma > last_sma*self.growth)
            if self.achieve_count >= self.acc_steps and all(growing):
                self.achieve_count = 0
                return True
        else:
            self.achieve_count = 0
        return False

    def cal_ma_diff(self, data):
        sma_data = {}
        for t in self.time_periords:
            sma = np.mean(data[-t:])
            sma_data[t] = sma
        
        sma_data = [sma_data[key] for key in sorted(sma_data.keys(), reverse=True)]

        last_sma = sma_data[0]
        judge = []
        for sma, r in zip(sma_data[1:], self.diff_rate):
            judge.append(sma > r*last_sma)
            last_sma = sma
        # print(sma_data)
        return all(judge), sma_data


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


TOKEN = '6041794044:AAHdd2S1CSR9CVhr-TrduVETEUJr3uxbqxU'
def send_msg(message_text):
    bot_token = TOKEN
    chat_id = "1745246461"

    # Set the API endpoint URL
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    # Set the payload data
    payload = {
        'chat_id': chat_id,
        'text': message_text
    }

    # Send the POST request
    response = requests.post(url, data=payload)

    # Print the response content
    print(response.text)

def get_symbols_string(symbols: list):
    symbols = ','.join(symbols)
    symbols: str = f'[{symbols}]'
    return symbols

def main2():
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
            # # if volumes[-1] > 1e7:
            # # if cur_price > mean_price+1*std_price:
            # #     send_msg(f"1 {datetime.now()} {coin['symbol']}: cur: {cur_price} th: {mean_price}")
            # if std_price < 1e-2:
            #     continue
            # # if cur_price > mean_price+3*std_price:
            # #     send_msg(f"3 {datetime.now()} {coin['symbol']}: cur: {cur_price} th: {mean_price}")
            # if cur_price > mean_price+5*std_price:
            #     send_msg(f"5 {datetime.now()} {coin['symbol']}: cur: {cur_price} th: {mean_price}")
            # if cur_price > mean_price+7*std_price:
            #     send_msg(f"7 {datetime.now()} {coin['symbol']}: cur: {cur_price} th: {mean_price}")
            # # if mean_price > 9*mean_price:
            # #     send_msg(f"9 {datetime.now()} {coin['symbol']}: cur: {cur_price} th: {mean_price}")
            # # if mean_price > 11*mean_price:
            # #     send_msg(f"11 {datetime.utcfromtimestamp(coin['openTime']/1000)} {coin['symbol']}: cur: {cur_price} th: {mean_price}")

        # if idx > cal_length+1:

        #     for i, (symbol, diff_data) in enumerate(diff.items()):
        #         coin_prices = list(prices[symbol])
        #         axes[symbol][1].plot(timestamp[cal_length+1:], coin_prices[cal_length+1:], label='price', color=colors[0])
        #         axes[symbol][1].plot(timestamp[cal_length+1:], diff_data, label='price_ratio', color=colors[1])

        #     for i, (symbol, diff_v) in enumerate(diff_vol.items()):
        #         axes[symbol][1].plot(timestamp[cal_length+1:], diff_v, label='volume_ratio', color=colors[2])
        #         if idx == cal_length+2:
        #             axes[symbol][1].set_title(symbol)
        #             axes[symbol][1].legend(loc='best')
        #             axes[symbol][1].grid()
        #             myFmt = mdates.DateFormatter('%H:%M')
        #             axes[symbol][1].xaxis.set_major_formatter(myFmt)
    
        #         axes[symbol][0].savefig(f'mean_diff_{symbol}.png')

        idx += 1
        timestamp.append(datetime.now())
        time.sleep(60)


def main():
    max_num_coin = 100
    cal_length = 5
    cal_length = max(2, cal_length)

    ticker_prices = get_usdt_ticker()
    symbols = []
    for idx, coin in enumerate(ticker_prices):
        if idx > max_num_coin-1:
            break
        symbol = coin['symbol']
        symbols.append(f'"{symbol}"')
    # symbols = [f""{coin['symbol']}"" for coin in ticker_prices]
    symbols = ','.join(symbols)
    symbols = f'[{symbols}]'
    priceChangePercent, volumes = {}, {}

    
    idx = 0
    max_earn = {}
    th = 10
    while True:
        data = rolling_window_price_change_stats(symbols=symbols, windowSize='15m')
        if data is None:
            continue
        # print(idx)
        for coin in data:
            if coin['symbol'] not in volumes:
                volumes[coin['symbol']] = deque(maxlen=20)
            else:
                cur_volume = float(coin['volume'])
                volumes[coin['symbol']].append(cur_volume)

            if coin['symbol'] not in priceChangePercent:
                priceChangePercent[coin['symbol']] = deque(maxlen=20)
            else:
                cur_pcp = float(coin['priceChangePercent'])
                priceChangePercent[coin['symbol']].append(cur_pcp)

            if idx <= cal_length:
                continue

            profits = list(priceChangePercent[coin['symbol']])
            cur_profit = profits[-1]
            mean_profit = 0
            for p in profits:
                mean_profit += max(0, p)
            mean_profit /= len(profits)

            # if volumes[-1] > 1e7:
            # if cur_profit > 1*mean_profit:
            #     send_msg(f"1 {datetime.utcfromtimestamp(coin['openTime']/1000)} {coin['symbol']}: cur: {cur_profit} th: {mean_profit}")
            # if cur_profit > 2*mean_profit:
            #     send_msg(f"2️⃣ {datetime.utcfromtimestamp(coin['openTime']/1000)} {coin['symbol']}: cur: {cur_profit} th: {mean_profit}")
            # if cur_profit > 3*mean_profit:
            #     # max_earn[coin['symbol']] = {'profit': cur_profit, 'timestamp': datetime.utcfromtimestamp(coin['openTime']/1000)}
            #     send_msg(f"3️⃣ {datetime.utcfromtimestamp(coin['openTime']/1000)} {coin['symbol']}: cur: {cur_profit} th: {mean_profit}")
            if cur_profit > 7*mean_profit:
                send_msg(f"7 {datetime.utcfromtimestamp(coin['openTime']/1000)} {coin['symbol']}: cur: {cur_profit} th: {mean_profit}")
            if cur_profit > 9*mean_profit:
                send_msg(f"9 {datetime.utcfromtimestamp(coin['openTime']/1000)} {coin['symbol']}: cur: {cur_profit} th: {mean_profit}")
            if cur_profit > 11*mean_profit:
                send_msg(f"11 {datetime.utcfromtimestamp(coin['openTime']/1000)} {coin['symbol']}: cur: {cur_profit} th: {mean_profit}")

            # # 计算平均值和标准差
            # pcp_seq = list(priceChangePercent[coin['symbol']])[-cal_length-1:-1]
            # mean_pcp = statistics.mean(pcp_seq)
            # std_pcp = statistics.stdev(pcp_seq)
            # th_pcp = mean_pcp + 3*std_pcp
            
            # vol_seq = list(volumes[coin['symbol']])[-cal_length-1:-1]
            # mean_vol = statistics.mean(vol_seq)
            # std_vol = statistics.stdev(vol_seq)
            # th_vol = mean_vol + 3*std_vol

            # # print(f'Mean: {mean_pcp:.4f}')
            # # print(f'Srd: {std_pcp:.4f}')
            # if cur_pcp > th_pcp and cur_volume > th_vol:
            #     print(f'buy {coin["symbol"]}')
            #     print(f'{coin["symbol"]} cur_pcp {cur_pcp} th_pcp {th_pcp} cur_vol {cur_volume} th_vol {th_vol}')
            # # else:
        
        # pprint(max_earn)
        idx += 1
        time.sleep(60)
    

if __name__ == '__main__':
    # main()
    main2()
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
