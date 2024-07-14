import pytest

from src.wallet import Asset


@pytest.fixture
def mock_asset():
    asset = Asset()
    asset.deposit(symbol='USDT', number=10000, cost=1.0)
    return asset


def test_deposit(mock_asset):
    assert mock_asset.get_balance(symbol='USDT') == 10000


def test_withdraw(mock_asset):
    mock_asset.withdraw(symbol='USDT', number=5000)
    assert mock_asset.get_balance(symbol='USDT') == 5000
    with pytest.raises(ValueError):
        mock_asset.withdraw(symbol='USDT', number=6000)


def test_get_balance(mock_asset):
    mock_asset.deposit(symbol='ETH', number=1.2, cost=3000)
    assert mock_asset.get_balance() == {'USDT': 10000, 'ETH': 1.2}
    assert mock_asset.get_balance(symbol='USDT') == 10000
    assert mock_asset.get_balance(symbol='ETH') == 1.2
    assert mock_asset.get_balance(symbol='BTC') == 0.0


def test_is_balance_enough(mock_asset):
    assert mock_asset.is_balance_enough(symbol='USDT', number=5000)
    assert not mock_asset.is_balance_enough(symbol='USDT', number=15000)
    assert not mock_asset.is_balance_enough(symbol='ETH', number=1.0)

def test_get_cost(mock_asset):
    assert mock_asset.get_cost(symbol='USDT') == 1
    assert mock_asset.get_cost(symbol='ETH') is None
    mock_asset.deposit(symbol='ETH', number=1.0, cost=3000)
    assert mock_asset.get_cost(symbol='ETH') == 3000
    mock_asset.deposit(symbol='ETH', number=1.0, cost=2000)
    assert mock_asset.get_cost(symbol='ETH') == 2500



# def test_asset_get_balance(mock_asset):
#     usdt = Coin(symbol='USDT', number=1000)
#     eth = Coin(symbol='ETH', number=1.2)

#     # deposit, new coin
#     mock_asset.deposit(usdt)
#     mock_asset.deposit(eth)
#     balance = mock_asset.get_balance()
#     assert isinstance(balance, dict)
#     assert balance['USDT'].number == 1000
#     assert balance['ETH'].number == 1.2
    
#     # deposit, add to existing coin
#     eth = Coin(symbol='ETH', number=1.3)
#     mock_asset.deposit(eth)
#     assert mock_asset.get_coin_balance(symbol='ETH') == 2.5

#     # withdraw, subtract from existing coin
#     eth = Coin(symbol='ETH', number=1.0)
#     mock_asset.withdraw(eth)
#     assert mock_asset.get_coin_balance(symbol='ETH') == 1.5

#     # withdraw, not enough coin
#     eth = Coin(symbol='ETH', number=2)
#     try:
#         mock_asset.withdraw(eth)
#     except ValueError as e:
#         assert mock_asset.get_coin_balance(symbol='ETH') == 1.5

#     # withdraw, just enough coin
#     eth = Coin(symbol='ETH', number=1.5)
#     mock_asset.withdraw(eth)
#     assert mock_asset.get_coin_balance(symbol='ETH') == 0.0


# def test_asset_add_coin(mock_asset):
#     usdt = Coin(symbol='USDT', number=1000)
#     mock_asset.deposit(usdt)
#     usdt_coin = mock_asset.get_coin('USDT')
#     assert usdt_coin.symbol == 'USDT'
#     assert usdt_coin.number == 1000

#     usdt_number = mock_asset.get_coin_balance('USDT')
#     assert usdt_number == 1000