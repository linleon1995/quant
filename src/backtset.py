from datetime import datetime

from src.create_backtest_database import ArcticDBOperator
from src.strategies import base_strategy, moving_average


# TODO: 假設前提為無資金假設，所有的交易都可以被完成，考慮這種情況的策略表現
class Evaluator:
    def __init__(self):
        self.init_money = {'USDT': 10000}

    def collect(self):
        pass

    def eval(self):
        pass


def main():
    symbol = 'WIFUSDT'

    arctic_ops = ArcticDBOperator(url="lmdb:///Leon/SideProject/quant", lib_name='Binance')
    DBobject = arctic_ops.read(data_name=symbol, date_range=(datetime(2024, 4, 1, 0, 0), datetime(2024, 4, 15, 16, 17)))
    evaluator = Evaluator()
    strategy = base_strategy.TestStateMachine(
        symbol=symbol,
        maxlen=1440,
        ma_range_list=[7, 25, 99]
    )
    trader = None
    wallet = None
    for tick in DBobject.data.iterrows():
        timestamp, data = tick
        close_price = data['close_price']
        trade_request = strategy.receive(price=close_price, 
                                         timestamp=timestamp)
        trade_response, trade_result = trader.trade(trade_request)
        strategy.push_trade_response(trade_response)
        wallet.push_trade_result(trade_result)
    evaluator.eval(wallet.init_asset, wallet.trade_history)


if __name__ == '__main__':
    main()