from datetime import datetime

from tqdm import tqdm

from src.create_backtest_database import ArcticDBOperator
from src.strategies import naive_strategy
# from src.strategies import base_strategy, moving_average
from src.eval.evaluator import Evaluator
from src.wallet import BaseWallet, Coin

# Market在回測中扮演封裝DB操作跟模擬交易市場的腳色，所以包含了DB_operator跟Broker
# 給予要求的時間範圍跟對象，返回資料的generator (ticker)，其中也包含了寫入DB的過程
# 實際交易中，Market應該對應到交易所的API，每次要求資料時都會向交易所發送請求，所以ticker應該是要一個高級的封裝對象
# 抽象get_data, get_index等方法


def main():

    # Trader
    N = 100
    trade_ratio = 0.1
    strategy = naive_strategy.NaiveStrategy(buy_rate=0.0, sell_rate=0.04, trade_unit=trade_ratio*N) # TODO: add symbol?
    trader = Trader(strategy)

    # Wallet
    wallet = BaseWallet()
    usdt = Coin('USDT', N, cost=1)
    wallet.deposit(usdt)

    # Market
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
    broker = Broker()
    market = Market(symbols, broker)

    for symbol in symbols:
        ticker = market.get_ticker(symbol)
        for tick in ticker:
            timestamp, data = tick
            # TODO: str close_price?
            close_price = data['close_price']
            trade_request = trader.add_tick(price=float(close_price), 
                                            symbol=symbol,
                                            #  timestamp=timestamp,
                                            )
            if trade_request is not None:
                trade_response = market.add_trade(trade_request)
                # market.add_trade(trade_response)
                if trade_response is not None:
                    print(timestamp, f'{trade_request.action} {trade_request.number} {trade_request.price}')
                    wallet.add_trade(trade_response)
                    trade_metrics = trader.get_trade_metrics()
                    if  trade_request.action == 'sell':
                        print(wallet.get_coin_balance('USDT'))
                        print(timestamp, f'{trade_metrics.average_return*100:.2f} %')


if __name__ == '__main__':
    main()