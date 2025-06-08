
from src.strategy.naive_strategy import NaiveStrategy


def test_naive_strategy():
    naive_strategy = NaiveStrategy(buy_rate=0.0, sell_rate=0.05, trade_unit=1.0)
    trade_request = naive_strategy.add_tick(symbol='ETHUSDT', price=3000)
    trade_request = naive_strategy.add_tick(symbol='ETHUSDT', price=3001)
    assert trade_request.action == 'buy'
    assert trade_request.symbol == 'ETHUSDT'
    assert trade_request.price == 3001
    assert trade_request.number == 1.0

    trade_request = naive_strategy.add_tick(symbol='ETHUSDT', price=4000)
    assert trade_request is not None
    assert trade_request.action == 'sell'
    assert trade_request.symbol == 'ETHUSDT'
    assert trade_request.price == 4000
    assert trade_request.number == 1.0
    
    # After selling, state is 'sell'. last_price is 4000.
    # Next tick price 50000. 50000 > 4000 * (1 + 0.0) is true. So it should buy again.
    trade_request = naive_strategy.add_tick(symbol='ETHUSDT', price=50000)
    assert trade_request is not None
    assert trade_request.action == 'buy'
    assert trade_request.symbol == 'ETHUSDT'
    assert trade_request.price == 50000

    # After buying at 50000. State is 'buy'. last_price is 50000.
    # Next tick price 47400. return_rate = (47400 - 50000) / 50000 = -2600/50000 = -0.052
    # This is NOT > sell_rate (0.05). So it should NOT sell.
    trade_request = naive_strategy.add_tick(symbol='ETHUSDT', price=47400)
    assert trade_request is None # No action, as sell condition not met
