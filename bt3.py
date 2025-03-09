from datetime import datetime
from pprint import pprint

from tqdm import tqdm

from new_strategy import DynamicBreakoutTrader
from src.create_backtest_database import ArcticDBOperator
from src.eval.evaluator import Evaluator
from src.strategies import naive_strategy
from src.wallet import BaseWallet, Coin


def main():
    coin_list = [
        'ADAUSDT', 'WIFUSDT', 'ATAUSDT', 'PEPEUSDT', 'ETHUSDT', 'BTCUSDT', 'BNBUSDT', 'NEIROUSDT', 'PNUTUSDT', 'DOGEUSDT', 'TRUMPUSDT'
    ]
    # coin_list = [
    #     'PEPEUSDT'
    # ]

    total_earn = {}
    for symbol in coin_list:
        print(f'Backtesting {symbol}')
        USDT_balance = 10000
        lookback = 14*24*60
        lookback = 8*60
        start_time = datetime(year=2020, month=1, day=1, hour=0, minute=0)
        end_time = datetime(year=2025, month=3, day=1, hour=0, minute=0)

        arctic_ops = ArcticDBOperator(url="lmdb://arctic_database", lib_name='Binance')
        DBobject = arctic_ops.read(data_name=symbol, 
                                start_time=start_time, 
                                end_time=end_time)

        strategy = DynamicBreakoutTrader(lookback=lookback)

        wallet = BaseWallet()
        usdt = Coin(symbol='USDT', number=USDT_balance, cost=1)
        wallet.deposit(coin=usdt)
        for tick in tqdm(DBobject.data.iterrows()):
            strategy.on_tick(*tick)

        print(strategy.positions)
        earn_sum = sum([trade['earn'] for trade in strategy.trade_records])
        print(f'Total earn: {100*earn_sum:.2f} %')
        total_earn[symbol] = {'earn': earn_sum, 'trade_records': strategy.trade_records}
        pprint(total_earn)
    
    print('finish')

if __name__ == '__main__':
    main()