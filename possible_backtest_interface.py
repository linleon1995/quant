
from backtest import BackTest



if __name__ == '__main__':
    backtester = BackTester(
        strategy='strategy_1',
        start_date='2018-01-01',
        end_date='2018-12-31',
        initial_capital=100000,
        commission=0.001,
        slippage=0.001,
        benchmark='000300.XSHG',
        universe=['000300.XSHG'],
        freq='d',
        refresh_rate=1,
        market='Binance',
        alert=['Telegram'],
    )
    backtester.run()