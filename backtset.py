from datetime import datetime

from tqdm import tqdm

from src.create_backtest_database import ArcticDBOperator
from src.eval.evaluator import Evaluator
from src.strategies import naive_strategy
from src.wallet import BaseWallet, Coin


def main():
    symbol = 'WIFUSDT'
    USDT_balance = 10000

    arctic_ops = ArcticDBOperator(url="lmdb://arctic_database", lib_name='Binance')
    DBobject = arctic_ops.read(data_name=symbol, 
                               start_time=datetime(year=2024, month=1, day=1, hour=0, minute=0), 
                               end_time=datetime(year=2024, month=6, day=15, hour=16, minute=17))
    evaluator = Evaluator()

    # strategy = base_strategy.TestStateMachine(
    #     symbol=symbol,
    #     maxlen=1440,
    #     ma_range_list=[7, 25, 99]
    # )
    trade_ratio = 0.1
    strategy = naive_strategy.NaiveStrategy(buy_rate=0.0, sell_rate=0.04, trade_unit=trade_ratio*USDT_balance) # TODO: add symbol?

    wallet = BaseWallet()
    usdt = Coin(symbol='USDT', number=USDT_balance, cost=1)
    wallet.deposit(coin=usdt)
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
        # trade_response = trade_request
        # strategy.push_trade_response(trade_response)
        if trade_request is not None:
            trade_response, trade_metrics = wallet.add_trade(trade_signal=trade_request)
            if trade_metrics is not None:
                print(timestamp, f'{trade_request.action} {trade_request.number} {trade_request.price}')
                if  trade_request.action == 'sell':
                    print(timestamp, f'{trade_metrics.average_return*100:.2f} %')
    print('finish')

if __name__ == '__main__':
    main()