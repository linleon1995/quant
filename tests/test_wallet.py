import pytest


def mock_wallet():
    pass

def test_withdraw(mock_wallet):
    mock_wallet.withdraw()


def test_deposit(mock_wallet):
    response = mock_wallet.deposit(100000, 'BTC')
    assert response['status'] == 'success'
    

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

