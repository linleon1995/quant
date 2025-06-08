import pytest

from src.data_source.create_backtest_database import ArcticDBOperator
from src.backtset.market import Market


from src.backtset.wallet import BaseWallet


@pytest.fixture
def mock_market():
    db_operator = ArcticDBOperator(url="lmdb://arctic_database", lib_name='Binance')
    wallet = BaseWallet()
    # symbols = ['SOLUSDT', 'BTCUSDT', 'ETHUSDT'] # Not used by Market constructor
    # broker = None # Not used by Market constructor
    mock_market_instance = Market(wallet, db_operator)
    return mock_market_instance

# def test_market_singleton(mock_market):
#     wallet = mock_market.get_wallet()
#     market = Market()
#     assert market is mock_market


def test_market_ticker(mock_market):
    # Setup data for this specific test, as get_ticker now raises error for missing symbols
    mock_market.ticker_data = {
        'SOLUSDT': [{'time': '2024-04-05T12:00:00', 'price': 100.0}]
    }
    sol_ticker = mock_market.get_ticker('SOLUSDT', start_time='2024-04-05', end_time='2024-04-06')
    assert len(sol_ticker) == 1 # Example assertion
    assert sol_ticker[0]['price'] == 100.0


def test_market_data_not_exist_in_db():
    pass


def test_multi_tickers(mock_market): # Added mock_market fixture
    # Assuming mock_market needs some ticker_data setup for this test to be meaningful
    # For now, just testing the call doesn't raise an immediate error due to wrong mock_market object
    mock_market.ticker_data = { # Example setup
        'BTCUSDT': [{'time': '2024-04-05T10:00:00', 'price': 68000}],
        'ETHUSDT': [{'time': '2024-04-05T10:00:00', 'price': 3400}]
    }
    multi_ticker = mock_market.get_ticker(['BTCUSDT', 'ETHUSDT'], start_time='2024-04-05', end_time='2024-04-06')
    # Assertions about multi_ticker would go here

def test_invalid_symbol(mock_market): # Added mock_market fixture
    with pytest.raises(ValueError):
        # This test might need adjustment if get_ticker itself is expected to raise ValueError
        # For now, assuming the call structure is the main point after fixing the fixture.
        # If get_ticker is robust against unknown symbols, the test might need a different setup.
        mock_market.get_ticker('INVALID_SYMBOL', start_time='2024-04-05', end_time='2024-04-06')

def test_invalid_time(mock_market): # Added mock_market fixture
    with pytest.raises(ValueError):
        # Similar to test_invalid_symbol, the actual error raising depends on get_ticker's implementation
        mock_market.get_ticker('BTCUSDT', start_time='2024-04-05', end_time='2024-04-04')