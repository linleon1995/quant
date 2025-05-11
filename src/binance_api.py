import time
from datetime import datetime, timedelta, timezone
from typing import List

import requests


class BinanceAPI:
    def __init__(self, base_url='https://api.binance.com') -> None:
        self.base_url = base_url

    def get_symbols(self) -> list:
        url = f'{self.base_url}/api/v3/exchangeInfo'
        response = requests.get(url=url)
        if response.status_code == 200:
            data = response.json()
            symbols = [symbol['symbol'] for symbol in data['symbols']]
            return symbols
        else:
            print("Error:", response.status_code)
            return []
        
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

    def get_earliest_kline_timestamp(self, symbol, interval="1d"):
        # Start from 2017-01-01 00:00:00 UTC (Binance start date)
        start_time = int(datetime(2017, 1, 1).timestamp() * 1000)
        end_time = int(time.time() * 1000)

        earliest = None

        # Binary search to find earliest available Kline
        while start_time <= end_time:
            mid_time = (start_time + end_time) // 2
            url = f"{self.base_url}/api/v3/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "startTime": mid_time,
                "limit": 1
            }
            r = requests.get(url, params=params)
            data = r.json()

            if isinstance(data, list) and len(data) > 0:
                # Data found, move end_time left
                earliest = data[0][0]
                end_time = mid_time - 1
            else:
                # No data, move start_time right
                start_time = mid_time + 1
            time.sleep(0.2)  # Avoid rate limit

        if earliest:
            dt_utc = datetime.fromtimestamp(earliest / 1000, tz=timezone.utc)
            dt_local = dt_utc.astimezone(timezone(timedelta(hours=8)))
            return dt_local
            # 假設 earliest 是毫秒時間戳
        else:
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

