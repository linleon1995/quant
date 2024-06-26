from datetime import datetime

from tqdm import tqdm

from src.create_backtest_database import ArcticDBOperator
from src.strategies import naive_strategy
# from src.strategies import base_strategy, moving_average
from src.eval.evaluator import Evaluator
from src.wallet import BaseWallet, Coin


def main():
    symbol = 'WIFUSDT'

    arctic_ops = ArcticDBOperator(url="lmdb://database", lib_name='Binance')
    DBobject = arctic_ops.read(data_name=symbol, date_range=(datetime(2024, 1, 1, 0, 0), datetime(2024, 4, 15, 16, 17)))
    evaluator = Evaluator()
    # strategy = base_strategy.TestStateMachine(
    #     symbol=symbol,
    #     maxlen=1440,
    #     ma_range_list=[7, 25, 99]
    # )
    strategy = naive_strategy.NaiveStrategy(buy_rate=0.0, sell_rate=0.04) # TODO: add symbol?
    trader = None
    wallet = BaseWallet()
    usdt = Coin('USDT', 10)
    wallet.deposit(usdt)
    for tick in tqdm(DBobject.data.iterrows()):
        timestamp, data = tick
        # TODO: str close_price?
        close_price = data['close_price']
        trade_request = strategy.add_tick(price=float(close_price), 
                                          symbol=symbol,
                                        #  timestamp=timestamp,
                                         )
        # TODO: trade fee
        # trade_response = trader.trade(trade_request)
        trade_response = trade_request
        # strategy.push_trade_response(trade_response)
        if trade_response is not None:
            wallet.add_trade(trade_request)
            print(timestamp, wallet.asset.coins)
    # evaluator.eval(wallet)
    # pass


if __name__ == '__main__':
    main()