import unittest
from unittest.mock import patch, MagicMock
from src.trader.binance_trader import BinanceTrader
from src.client.binance_api import BinanceAPI

class TestBinanceTrader(unittest.TestCase):

    def setUp(self):
        """Set up for each test."""
        self.trader = BinanceTrader(api_key="test_key", api_secret="test_secret")
        # Mock the BinanceAPI client within BinanceTrader
        # We mock get_ticker_price as it's used by buy/sell
        self.trader.api = MagicMock(spec=BinanceAPI)

    def mock_ticker_price(self, symbol):
        if symbol == "BTCUSDT":
            return {'price': '50000.00'}
        elif symbol == "ETHUSDT":
            return {'price': '2000.00'}
        return {'price': '1.00'} # Default for other symbols

    def test_initialization(self):
        """Test trader initialization."""
        self.assertEqual(self.trader.api_key, "test_key")
        self.assertEqual(self.trader.get_balance(), {"USDT": 10000.0})
        self.assertEqual(self.trader.get_positions(), {})

    def test_buy_sufficient_funds(self):
        """Test buying an asset with sufficient funds."""
        self.trader.api.get_ticker_price.side_effect = self.mock_ticker_price

        initial_balance = self.trader.get_balance()['USDT']
        buy_amount = 0.1
        price = 50000.0
        cost = buy_amount * price

        result = self.trader.buy("BTCUSDT", buy_amount, price=price)

        self.assertTrue(result["success"])
        self.assertEqual(self.trader.get_balance()['USDT'], initial_balance - cost)
        self.assertEqual(self.trader.get_positions().get("BTCUSDT"), buy_amount)
        # self.trader.api.get_ticker_price was NOT called because price was provided


    def test_buy_sufficient_funds_market_order(self):
        """Test buying an asset with sufficient funds using a market order."""
        self.trader.api.get_ticker_price.side_effect = self.mock_ticker_price

        initial_balance = self.trader.get_balance()['USDT']
        buy_amount = 0.05
        # Price will be fetched by get_ticker_price mock
        mocked_price = float(self.mock_ticker_price("BTCUSDT")['price'])
        cost = buy_amount * mocked_price

        result = self.trader.buy("BTCUSDT", buy_amount) # No price, so market order

        self.assertTrue(result["success"])
        self.assertEqual(self.trader.get_balance()['USDT'], initial_balance - cost)
        self.assertEqual(self.trader.get_positions().get("BTCUSDT"), buy_amount)
        self.trader.api.get_ticker_price.assert_called_once_with(symbol="BTCUSDT")


    def test_buy_insufficient_funds(self):
        """Test buying an asset with insufficient funds."""
        self.trader.api.get_ticker_price.side_effect = self.mock_ticker_price

        initial_balance = self.trader.get_balance()['USDT']
        buy_amount = 1 # BTC
        price = initial_balance + 1000 # Cost more than balance

        result = self.trader.buy("BTCUSDT", buy_amount, price=price)

        self.assertFalse(result["success"])
        self.assertEqual(self.trader.get_balance()['USDT'], initial_balance) # Balance unchanged
        self.assertEqual(self.trader.get_positions().get("BTCUSDT"), None) # No position opened

    def test_sell_sufficient_position(self):
        """Test selling an asset with a sufficient position."""
        self.trader.api.get_ticker_price.side_effect = self.mock_ticker_price

        # First, establish a position
        self.trader._positions = {"BTCUSDT": 0.1}
        self.trader._balance = 5000.0 # Assume some balance remaining after a hypothetical previous buy

        initial_balance = self.trader.get_balance()['USDT']
        sell_amount = 0.05
        price = 51000.0
        proceeds = sell_amount * price

        result = self.trader.sell("BTCUSDT", sell_amount, price=price)

        self.assertTrue(result["success"])
        self.assertEqual(self.trader.get_balance()['USDT'], initial_balance + proceeds)
        self.assertEqual(self.trader.get_positions().get("BTCUSDT"), 0.1 - sell_amount)
        # self.trader.api.get_ticker_price was NOT called because price was provided

    def test_sell_insufficient_position(self):
        """Test selling an asset with an insufficient position."""
        self.trader.api.get_ticker_price.side_effect = self.mock_ticker_price

        initial_balance = self.trader.get_balance()['USDT']
        self.trader._positions = {"BTCUSDT": 0.1} # Current position
        sell_amount = 0.2 # Trying to sell more than owned

        result = self.trader.sell("BTCUSDT", sell_amount, price=51000.0)

        self.assertFalse(result["success"])
        self.assertEqual(self.trader.get_balance()['USDT'], initial_balance) # Balance unchanged
        self.assertEqual(self.trader.get_positions().get("BTCUSDT"), 0.1) # Position unchanged

    def test_sell_full_position(self):
        """Test selling the entire position of an asset."""
        self.trader.api.get_ticker_price.side_effect = self.mock_ticker_price

        self.trader._positions = {"BTCUSDT": 0.1}
        self.trader._balance = 5000.0
        initial_balance = self.trader.get_balance()['USDT']
        sell_amount = 0.1
        price = 51000.0
        proceeds = sell_amount * price

        result = self.trader.sell("BTCUSDT", sell_amount, price=price)

        self.assertTrue(result["success"])
        self.assertEqual(self.trader.get_balance()['USDT'], initial_balance + proceeds)
        self.assertIsNone(self.trader.get_positions().get("BTCUSDT")) # Position should be removed

    def test_get_balance_and_positions(self):
        """Test retrieving balance and positions."""
        self.assertEqual(self.trader.get_balance(), {"USDT": 10000.0})
        self.trader._balance = 500.0
        self.assertEqual(self.trader.get_balance(), {"USDT": 500.0})

        self.assertEqual(self.trader.get_positions(), {})
        self.trader._positions = {"ETHUSDT": 10}
        self.assertEqual(self.trader.get_positions(), {"ETHUSDT": 10})

    def test_web3_placeholders(self):
        """Test placeholder web3/Metamask functions."""
        self.assertTrue(self.trader.connect_metamask())
        self.assertEqual(self.trader.metamask_address, "mock_metamask_address_0x123")
        self.assertEqual(self.trader.get_web3_balance(), 1.5) # Mock ETH balance
        self.assertEqual(self.trader.get_web3_balance(token_address="0xabc"), 5.0) # Mock token balance

if __name__ == '__main__':
    unittest.main()
