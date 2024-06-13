import pytest

from src.wallet import BaseWallet, Coin, TradeData, Asset

@pytest.fixture
def mock_wallet():
    return BaseWallet()

@pytest.fixture
def mock_asset():
    return Asset()

def test_coin():
    c1 = Coin('USDT', 1000)
    c2 = Coin('USDT', 2000)
    c3 = c1 + c2
    assert c1 is c3
    assert c1 is not c2
    assert c3.number == 3000


# def test_withdraw(mock_wallet):
#     mock_wallet.withdraw()

def test_base_function(mock_wallet):
    pass

def test_deposit(mock_wallet):
    usdt = Coin(symbol='USDT', number=10000)
    response = mock_wallet.deposit(usdt)
    assert mock_wallet.asset.coins['USDT'] == usdt
    assert response.status == 'success'
    
def test_trade_new(mock_wallet):
    usdt = Coin(symbol='USDT', number=100000)
    response = mock_wallet.deposit(usdt)
    eth = Coin(symbol='ETH', number=2)
    response = mock_wallet.deposit(eth)
    
    trade_signal = TradeData(altcoin_name='ETH', altcoin_price=3000, 
                             bridgecoin_name='USDT', bridgecoin_price=1, 
                             action='buy', number=1.0)
    trade_response = mock_wallet.add_trade(trade_signal)

    assert trade_response.status == 'success'
    assert mock_wallet.get_balance('USDT') == 97000
    assert mock_wallet.get_balance('ETH') == 3
    
    trade_signal = TradeData(altcoin_name='BTC', altcoin_price=70000, 
                             bridgecoin_name='USDT', bridgecoin_price=1, 
                             action='sell', number=1.0)
    trade_response = mock_wallet.add_trade(trade_signal)
    assert trade_response.status == 'fail'
    assert mock_wallet.get_balance('USDT') == 97000
    assert mock_wallet.get_balance('ETH') == 3


def test_asset_get_balance(mock_asset):
    usdt = Coin(symbol='USDT', number=1000)
    eth = Coin(symbol='ETH', number=1.2)
    mock_asset.deposit(usdt)
    mock_asset.deposit(eth)
    balance = mock_asset.get_balance()
    assert isinstance(balance, dict)
    assert balance['USDT'].number == 1000
    assert balance['ETH'].number == 1.2
    
    eth = Coin(symbol='ETH', number=1.3)
    mock_asset.deposit(eth)
    assert balance['ETH'].number == 2.5


def test_asset_add_coin(mock_asset):
    usdt = Coin(symbol='USDT', number=1000)
    mock_asset.deposit(usdt)
    usdt_coin = mock_asset.get_coin('USDT')
    assert usdt_coin.number == 1000



def test_trade(mock_wallet):
    response = mock_wallet.deposit(100000, 'BTC')
    assert mock_wallet.total_value == 100000
 
    assert mock_wallet.amount('BTC') is None
    mock_wallet.buy(1, 'BTC', 'USDT', 70000)
    assert mock_wallet.amount('BTC') == 1
    assert mock_wallet.value('BTC') == 70000
    assert mock_wallet.amount('USDT') == 30000
    assert mock_wallet.value('USDT') == 1

    assert mock_wallet.total_value == 100000
    assert isinstance(mock_wallet.portfolio, dict)
    # assert mock_wallet.portfolio.
    assert mock_wallet.profit == 0
    
    assert mock_wallet.roi == 0
    assert mock_wallet.profit == 0

    mock_wallet.sell(0.5, 'BTC', 'USDT', 80000)
    assert mock_wallet.amount('BTC') == 0.5
    assert mock_wallet.price('BTC') == 80000
    assert mock_wallet.value('BTC') == 40000
    assert mock_wallet.amount('USDT') == 70000
    assert mock_wallet.price('USDT') == 1
    assert mock_wallet.value('USDT') == 70000
    assert mock_wallet.roi == 0.1
    assert mock_wallet.profit == 10000
    assert mock_wallet.coin_profit('BTC') == 5000
    assert mock_wallet.coin_roi('BTC') == 1/7

    mock_wallet.update_price('BTCUSDT', 90000)
    assert mock_wallet.roi == 0.15
    assert mock_wallet.profit == 15000
    assert mock_wallet.coin_profit('BTC') == 10000
    assert mock_wallet.coin_roi('BTC') == 2/7

    # cost?
    # update_multi_price

