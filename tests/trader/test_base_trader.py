import pytest
from abc import ABC, abstractmethod
from src.trader.base_trader import BaseTrader

class TestBaseTrader:

    def test_inheritance_without_implementation(self):
        """
        Tests that a class inheriting from BaseTrader without
        implementing abstract methods raises TypeError upon instantiation.
        """
        class IncompleteTrader(BaseTrader):
            pass
        with pytest.raises(TypeError):
            IncompleteTrader()

    def test_inheritance_with_partial_implementation(self):
        """
        Tests that a class inheriting from BaseTrader with only partial
        implementation of abstract methods still raises TypeError upon instantiation.
        """
        class PartiallyCompleteTrader(BaseTrader):
            def buy(self, symbol: str, amount: float):
                return super().buy(symbol, amount)
            # Missing sell, get_balance, get_positions
        with pytest.raises(TypeError):
            PartiallyCompleteTrader()

    def test_inheritance_with_full_implementation(self):
        """
        Tests that a class inheriting from BaseTrader and implementing
        all abstract methods can be instantiated.
        """
        class CompleteTrader(BaseTrader):
            def buy(self, symbol: str, amount: float):
                pass
            def sell(self, symbol: str, amount: float):
                pass
            def get_balance(self) -> float:
                return 0.0
            def get_positions(self) -> dict:
                return {}

        try:
            CompleteTrader()
        except TypeError:
            pytest.fail("CompleteTrader should be instantiable but raised TypeError.")

    def test_abstract_methods_signature(self):
        """
        Checks if abstract methods are defined in BaseTrader.
        This is more of a structural check.
        """
        assert hasattr(BaseTrader, 'buy') and getattr(BaseTrader.buy, '__isabstractmethod__', False)
        assert hasattr(BaseTrader, 'sell') and getattr(BaseTrader.sell, '__isabstractmethod__', False)
        assert hasattr(BaseTrader, 'get_balance') and getattr(BaseTrader.get_balance, '__isabstractmethod__', False)
        assert hasattr(BaseTrader, 'get_positions') and getattr(BaseTrader.get_positions, '__isabstractmethod__', False)
