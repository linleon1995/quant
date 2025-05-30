from abc import ABC, abstractmethod

class BaseTrader(ABC):
    """
    Abstract base class for traders.
    This class serves as a template for all specific trader implementations.
    """

    @abstractmethod
    def buy(self, symbol: str, amount: float):
        """
        Buys a certain amount of a given symbol.
        """
        pass

    @abstractmethod
    def sell(self, symbol: str, amount: float):
        """
        Sells a certain amount of a given symbol.
        """
        pass

    @abstractmethod
    def get_balance(self) -> float:
        """
        Returns the current account balance.
        """
        pass

    @abstractmethod
    def get_positions(self) -> dict:
        """
        Returns the current open positions.
        """
        pass
