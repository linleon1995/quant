from datetime import datetime
from pprint import pprint

import arcticdb as adb
from tqdm import tqdm

from new_strategy import DynamicBreakoutTrader
from src.create_backtest_database import ArcticDBOperator
from src.eval.evaluator import Evaluator
from src.strategies import naive_strategy
from src.wallet import BaseWallet, Coin


def main():
    coin_list = [
        'ADAUSDT', 'WIFUSDT', 'ATAUSDT', 'PEPEUSDT', 'ETHUSDT', 'BTCUSDT', 'BNBUSDT', 
        'NEIROUSDT', 'PNUTUSDT', 'DOGEUSDT', 'TRUMPUSDT', 'VOXELUSDT'
    ]
    coin_list = None

    total_earn = {}
    total_trades = {}
    # arctic_ops = ArcticDBOperator(url="lmdb://arctic_database", lib_name='BinanceSpot')
    lib = adb.Arctic("lmdb://arctic_database")['BinanceSpot']
    if coin_list is None:
        coin_list = lib.list_symbols()
        
    for symbol in tqdm(coin_list):
        print(f'Backtesting {symbol}')
        USDT_balance = 10000
        lookback = 14*24*60
        lookback = 60
        start_time = datetime(year=2025, month=1, day=1, hour=0, minute=0)
        end_time = datetime(year=2025, month=3, day=30, hour=0, minute=0)

        DBobject = lib.read(symbol, date_range=(start_time, end_time))
        strategy = DynamicBreakoutTrader(lookback=lookback)

        wallet = BaseWallet()
        usdt = Coin(symbol='USDT', number=USDT_balance, cost=1)
        wallet.deposit(coin=usdt)
        for tick in tqdm(DBobject.data.iterrows()):
            strategy.on_tick(*tick)

        print(strategy.positions)
        earn_sum = sum([trade['earn'] for trade in strategy.trade_records])
        print(f'Total earn: {100*earn_sum:.2f} %')
        total_earn[symbol] = earn_sum
        total_trades[symbol] = strategy.trade_records
        pprint(total_earn)
    total_earn_sum = sum([earn for earn in total_earn.values()])
    print(f'Avg earn: {100*total_earn_sum/len(total_earn):.2f} %')
    print('finish')

if __name__ == '__main__':
    main()