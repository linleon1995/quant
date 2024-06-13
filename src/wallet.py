from dataclasses import dataclass, field
from typing import List, Dict
from collections import deque
from datetime import datetime


@dataclass
class Coin:
    symbol: str
    number: float = 0.0

    def __add__(self, coin: 'Coin') -> 'Coin':
        self.number = self.number + coin.number
        return self

@dataclass
class Response:
    status: str


@dataclass
class ActionStatus:
    success: str = 'success'
    fail: str = 'fail'
    

    
@dataclass
class TradeData:
    action: str
    number: float
    altcoin_name: str
    altcoin_price: float
    bridgecoin_name: str = 'USDT'
    bridgecoin_price: float = 1


@dataclass
class Asset:
    coins: Dict[str, Coin] = field(default_factory=dict)

    def deposit(self, coin: Coin):
        symbol = self.coins.get(coin.symbol) 
        if symbol is not None:
            self.coins[symbol] = self.coins[symbol] + coin
        else:
            # setattr(self, coin.symbol, coin.number)
            self.coins[coin.symbol] = coin

    def get_coin(self, coin_name: str) -> Coin:
        return self.coins.get(coin_name)
    
    def get_balance(self) -> dict:
        return self.coins
class BaseWallet:
    def __init__(self):
        self.asset = Asset()

    def deposit(self, coin: Coin) -> dict:
        try:
            self.asset.deposit(coin)
            return Response(status=ActionStatus.success)
        except Exception:
            return Response(status=ActionStatus.fail)
        
    def add_trade(self, trade_signal: TradeData):
        if trade_signal.action == 'buy':
            balance = self.asset.coins[trade_signal.bridgecoin_name].number - trade_signal.altcoin_price * trade_signal.number
            if balance >= 0:
                self.asset.coins[trade_signal.bridgecoin_name].number = balance
                coin = Coin(symbol=trade_signal.altcoin_name, number=trade_signal.number)
                self.asset.deposit(coin)
