import pytest
from src.wallet import BaseWallet, Coin, TradeRequest, Asset

@pytest.fixture
def mock_wallet():
    return BaseWallet()

@pytest.fixture
def mock_asset():
    return Asset()


def test_get_cost(mock_wallet):
    mock_wallet.deposit(Coin('USDT', 1000))
    mock_wallet.update_price(symbol='USDT', price=1)
    assert mock_wallet.get_cost(symbol='USDT') == 1000

    mock_wallet.deposit(Coin('ETH', 1.5))
    mock_wallet.update_price(symbol='ETH', price=3000)
    assert mock_wallet.get_cost(symbol='ETH') == 4500

    assert mock_wallet.get_cost(symbol='BTC') is None
    mock_wallet.deposit(Coin('BTC', 1.5))
    assert mock_wallet.get_cost(symbol='BTC') is None
    mock_wallet.update_price(symbol='BTC', price=40000)
    assert mock_wallet.get_cost(symbol='BTC') == 60000


def test_check_balance(mock_wallet):
    mock_wallet.deposit(Coin('USDT', 1000))
    assert mock_wallet.check_balance('USDT', 1000)
    assert not mock_wallet.check_balance('USDT', 1001)


def test_get_balance(mock_wallet):
    mock_wallet.deposit(Coin('USDT', 1000))
    assert mock_wallet.get_coin_balance('USDT') == 1000
    mock_wallet.deposit(Coin('USDT', 1000))
    assert mock_wallet.get_coin_balance('USDT') == 2000


def test__add_trade(mock_wallet):
    mock_wallet.deposit(Coin('USDT', 10000))
    trade_signal = TradeRequest(symbol='ETH', price=3000, 
                             bridgecoin_name='USDT', bridgecoin_price=1, 
                             action='buy', number=1.0)
    mock_wallet._add_trade(trade_signal)
    assert mock_wallet.get_coin_balance('USDT') == 7000
    assert mock_wallet.get_coin_balance('ETH') == 1


def test_coin():
    c1 = Coin('USDT', 1000)
    c2 = Coin('USDT', 2000)
    c3 = c1 + c2
    assert c1 is c3
    assert c1 is not c2
    assert c3.number == 3000


def test_deposit(mock_wallet):
    usdt = Coin(symbol='USDT', number=10000)
    response = mock_wallet.deposit(usdt)
    assert mock_wallet.asset.coins['USDT'] == usdt
    assert response.status == 'success'
    
def test_trade(mock_wallet):
    usdt = Coin(symbol='USDT', number=100000)
    response = mock_wallet.deposit(usdt)
    eth = Coin(symbol='ETH', number=2)
    response = mock_wallet.deposit(eth)
    
    # success
    trade_signal = TradeRequest(symbol='ETH', price=3000, 
                             bridgecoin_name='USDT', bridgecoin_price=1, 
                             action='buy', number=1.0)
    trade_response = mock_wallet.add_trade(trade_signal)
    assert trade_response.status == 'success'
    assert mock_wallet.get_coin_balance('USDT') == 97000
    assert mock_wallet.get_coin_balance('ETH') == 3
    
    # fail, not enough money
    trade_signal = TradeRequest(symbol='BTC', price=70000, 
                             bridgecoin_name='USDT', bridgecoin_price=1, 
                             action='sell', number=1.0)
    trade_response = mock_wallet.add_trade(trade_signal)
    assert trade_response.status == 'fail'
    assert mock_wallet.get_coin_balance('USDT') == 97000
    assert mock_wallet.get_coin_balance('ETH') == 3

    # fail, no coin
    trade_signal = TradeRequest(symbol='BNB', price=3000, 
                             bridgecoin_name='USDT', bridgecoin_price=1, 
                             action='sell', number=4.0)
    trade_response = mock_wallet.add_trade(trade_signal)
    assert trade_response.status == 'fail'
    assert mock_wallet.get_coin_balance('USDT') == 97000
    assert mock_wallet.get_coin_balance('ETH') == 3
    assert mock_wallet.get_coin_balance('BNB') == 0

    # edge case
    trade_signal = TradeRequest(symbol='ETH', price=4000,
                             bridgecoin_name='USDT', bridgecoin_price=1, 
                             action='sell', number=3.0)
    trade_response = mock_wallet.add_trade(trade_signal)
    assert trade_response.status == 'success'
    assert mock_wallet.get_coin_balance('USDT') == 109000
    assert mock_wallet.get_coin_balance('ETH') == 0



# def test_trade(mock_wallet):
#     response = mock_wallet.deposit(100000, 'BTC')
#     assert mock_wallet.total_value == 100000
 
#     assert mock_wallet.amount('BTC') is None
#     mock_wallet.buy(1, 'BTC', 'USDT', 70000)
#     assert mock_wallet.amount('BTC') == 1
#     assert mock_wallet.value('BTC') == 70000
#     assert mock_wallet.amount('USDT') == 30000
#     assert mock_wallet.value('USDT') == 1

#     assert mock_wallet.total_value == 100000
#     assert isinstance(mock_wallet.portfolio, dict)
#     # assert mock_wallet.portfolio.
#     assert mock_wallet.profit == 0
    
#     assert mock_wallet.roi == 0
#     assert mock_wallet.profit == 0

#     mock_wallet.sell(0.5, 'BTC', 'USDT', 80000)
#     assert mock_wallet.amount('BTC') == 0.5
#     assert mock_wallet.price('BTC') == 80000
#     assert mock_wallet.value('BTC') == 40000
#     assert mock_wallet.amount('USDT') == 70000
#     assert mock_wallet.price('USDT') == 1
#     assert mock_wallet.value('USDT') == 70000
#     assert mock_wallet.roi == 0.1
#     assert mock_wallet.profit == 10000
#     assert mock_wallet.coin_profit('BTC') == 5000
#     assert mock_wallet.coin_roi('BTC') == 1/7

#     mock_wallet.update_price('BTCUSDT', 90000)
#     assert mock_wallet.roi == 0.15
#     assert mock_wallet.profit == 15000
#     assert mock_wallet.coin_profit('BTC') == 10000
#     assert mock_wallet.coin_roi('BTC') == 2/7

#     # cost?
#     # update_multi_price

