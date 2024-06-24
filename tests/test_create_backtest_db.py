from src.strategies.base_strategy import StrategyExecuter


def get_data():
    pass
    # btc_1m_prices = ArcticDBOperator.get_data(market='Binanece',
    #                                         instrument='USD-M',
    #                                         tag='perceptual',
    #                                         pair='BTCUSDT',
    #                                         start=datetime(2024, 4, 5, 1, 16),
    #                                         end=datetime(2024, 4, 5, 2, 17),
    #                                         freq='1min')


def test_write_data():
    StrategyExecuter()