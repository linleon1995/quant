import pytest
from unittest.mock import MagicMock
from src.trader.binance_trader import BinanceTrader
from src.client.binance_api import BinanceAPI

@pytest.fixture
def trader():
    """Set up for each test."""
    trader_instance = BinanceTrader(api_key="test_key", api_secret="test_secret")
    # Mock the BinanceAPI client within BinanceTrader
    # We mock get_ticker_price as it's used by buy/sell
    trader_instance.api = MagicMock(spec=BinanceAPI)
    return trader_instance

class TestBinanceTrader:

    def mock_ticker_price(self, symbol):
        if symbol == "BTCUSDT":
            return {'price': '50000.00'}
        elif symbol == "ETHUSDT":
            return {'price': '2000.00'}
        return {'price': '1.00'} # Default for other symbols

    def test_initialization(self, trader):
        """Test trader initialization."""
        assert trader.api_key == "test_key"
        assert trader.get_balance() == {"USDT": 10000.0}
        assert trader.get_positions() == {}

    def test_buy_sufficient_funds(self, trader):
        """Test buying an asset with sufficient funds."""
        trader.api.get_ticker_price.side_effect = self.mock_ticker_price

        initial_balance = trader.get_balance()['USDT']
        buy_amount = 0.1
        price = 50000.0
        cost = buy_amount * price

        result = trader.buy("BTCUSDT", buy_amount, price=price)

        assert result["success"]
        assert trader.get_balance()['USDT'] == initial_balance - cost
        assert trader.get_positions().get("BTCUSDT") == buy_amount
        # trader.api.get_ticker_price was NOT called because price was provided


    def test_buy_sufficient_funds_market_order(self, trader):
        """Test buying an asset with sufficient funds using a market order."""
        trader.api.get_ticker_price.side_effect = self.mock_ticker_price

        initial_balance = trader.get_balance()['USDT']
        buy_amount = 0.05
        # Price will be fetched by get_ticker_price mock
        mocked_price = float(self.mock_ticker_price("BTCUSDT")['price'])
        cost = buy_amount * mocked_price

        result = trader.buy("BTCUSDT", buy_amount) # No price, so market order

        assert result["success"]
        assert trader.get_balance()['USDT'] == initial_balance - cost
        assert trader.get_positions().get("BTCUSDT") == buy_amount
        trader.api.get_ticker_price.assert_called_once_with(symbol="BTCUSDT")


    def test_buy_insufficient_funds(self, trader):
        """Test buying an asset with insufficient funds."""
        trader.api.get_ticker_price.side_effect = self.mock_ticker_price

        initial_balance = trader.get_balance()['USDT']
        buy_amount = 1 # BTC
        price = initial_balance + 1000 # Cost more than balance

        result = trader.buy("BTCUSDT", buy_amount, price=price)

        assert not result["success"]
        assert trader.get_balance()['USDT'] == initial_balance # Balance unchanged
        assert trader.get_positions().get("BTCUSDT") is None # No position opened

    def test_sell_sufficient_position(self, trader):
        """Test selling an asset with a sufficient position."""
        trader.api.get_ticker_price.side_effect = self.mock_ticker_price

        # First, establish a position
        trader._positions = {"BTCUSDT": 0.1}
        trader._balance = 5000.0 # Assume some balance remaining after a hypothetical previous buy

        initial_balance = trader.get_balance()['USDT']
        sell_amount = 0.05
        price = 51000.0
        proceeds = sell_amount * price

        result = trader.sell("BTCUSDT", sell_amount, price=price)

        assert result["success"]
        assert trader.get_balance()['USDT'] == initial_balance + proceeds
        assert trader.get_positions().get("BTCUSDT") == 0.1 - sell_amount
        # trader.api.get_ticker_price was NOT called because price was provided

    def test_sell_insufficient_position(self, trader):
        """Test selling an asset with an insufficient position."""
        trader.api.get_ticker_price.side_effect = self.mock_ticker_price

        initial_balance = trader.get_balance()['USDT']
        trader._positions = {"BTCUSDT": 0.1} # Current position
        sell_amount = 0.2 # Trying to sell more than owned

        result = trader.sell("BTCUSDT", sell_amount, price=51000.0)

        assert not result["success"]
        assert trader.get_balance()['USDT'] == initial_balance # Balance unchanged
        assert trader.get_positions().get("BTCUSDT") == 0.1 # Position unchanged

    def test_sell_full_position(self, trader):
        """Test selling the entire position of an asset."""
        trader.api.get_ticker_price.side_effect = self.mock_ticker_price

        trader._positions = {"BTCUSDT": 0.1}
        trader._balance = 5000.0
        initial_balance = trader.get_balance()['USDT']
        sell_amount = 0.1
        price = 51000.0
        proceeds = sell_amount * price

        result = trader.sell("BTCUSDT", sell_amount, price=price)

        assert result["success"]
        assert trader.get_balance()['USDT'] == initial_balance + proceeds
        assert trader.get_positions().get("BTCUSDT") is None # Position should be removed

    def test_get_balance_and_positions(self, trader):
        """Test retrieving balance and positions."""
        assert trader.get_balance() == {"USDT": 10000.0} # Initial balance from fixture setup
        trader._balance = 500.0 # Directly set the float balance
        assert trader.get_balance() == {"USDT": 500.0}

        assert trader.get_positions() == {} # Initial positions
        trader._positions = {"ETHUSDT": 10}
        assert trader.get_positions() == {"ETHUSDT": 10}

    def test_web3_placeholders(self, trader):
        """Test placeholder web3/Metamask functions."""
        assert trader.connect_metamask()
        assert trader.metamask_address == "mock_metamask_address_0x123"
        assert trader.get_web3_balance() == 1.5 # Mock ETH balance
        assert trader.get_web3_balance(token_address="0xabc") == 5.0 # Mock token balance
