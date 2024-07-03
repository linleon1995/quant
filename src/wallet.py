from dataclasses import dataclass, field
from typing import List, Dict
from collections import deque
from datetime import datetime


@dataclass
class Coin:
    symbol: str
    number: float = 0.0
    avg_price: float = 0.0

    def __add__(self, coin: 'Coin') -> 'Coin':
        self.number += coin.number
        self.avg_price = (self.number * self.avg_price + coin.number * coin.avg_price) / self.number
        return self

@dataclass
class Response:
    status: str
    msg: str = ''


@dataclass
class ActionStatus:
    success: str = 'success'
    fail: str = 'fail'
    

    
# TODO: add timestamp?
@dataclass
class TradeRequest:
    action: str
    number: float
    symbol: str
    price: float
    bridgecoin_name: str = 'USDT'
    bridgecoin_price: float = 1


@dataclass
class Asset:
    coins: Dict[str, Coin] = field(default_factory=dict)

    def deposit(self, coin: Coin):
        storeged_coin = self.coins.get(coin.symbol) 
        if storeged_coin is not None:
            self.coins[coin.symbol] = self.coins[coin.symbol] + coin
        else:
            # setattr(self, coin.symbol, coin.number)
            self.coins[coin.symbol] = coin

    def withdraw(self, coin: Coin):
        stored_coin = self.coins.get(coin.symbol)
        ori_balance = stored_coin.number
        if stored_coin is not None:
            if stored_coin.number < coin.number:
                raise ValueError(f'Not enough to withdraw {coin.number} {coin.symbol} for current balance {ori_balance}')
            else:
                stored_coin.number -= coin.number
        else:
            raise ValueError('No coin')
        
    def get_coin(self, symbol: str) -> Coin:
        return self.coins.get(symbol)
    
    def get_coin_balance(self, symbol: str) -> float:
        coin = self.coins.get(symbol)
        if coin is not None:
            return coin.number
        else:
            return 0.0
        
    def get_balance(self) -> dict:
        return self.coins
    
    def check_balance(self, symbol: str, number: int) -> bool:
        stored_coin = self.coins.get(symbol)
        if stored_coin is not None:
            return stored_coin.number >= number
        else:
            return False
    

class BaseWallet:
    def __init__(self):
        self.asset = Asset()
        self.trade_history = deque(maxlen=1000)

    # TODO: deposit without coin object
    # def deposit(self, coin, symbol, number)
    def deposit(self, coin: Coin) -> dict:
        try:
            self.asset.deposit(coin)
            return Response(status=ActionStatus.success)
        except Exception:
            return Response(status=ActionStatus.fail)
        
    def get_coin_balance(self, symbol: str) -> float:
        coin = self.asset.coins.get(symbol)
        if coin is not None:
            return coin.number
        else:
            return 0.0
        
    def add_trade(self, trade_signal: TradeRequest):
        if trade_signal.action == 'buy':
            if self.asset.check_balance(symbol=trade_signal.bridgecoin_name, number=trade_signal.price * trade_signal.number):
                self.asset.withdraw(Coin(symbol=trade_signal.bridgecoin_name, number=trade_signal.price * trade_signal.number))
                coin = Coin(symbol=trade_signal.symbol, number=trade_signal.number)
                try:
                    self.asset.deposit(coin)
                    self.trade_history.append(trade_signal)
                    return Response(status=ActionStatus.success)
                except Exception as e:
                    return Response(status=ActionStatus.fail)
            else:
                return Response(status=ActionStatus.fail)
        elif trade_signal.action == 'sell':
            if self.asset.check_balance(symbol=trade_signal.symbol, number=trade_signal.number):
                self.asset.withdraw(Coin(symbol=trade_signal.symbol, number=trade_signal.number))
                coin = Coin(symbol=trade_signal.bridgecoin_name, number=trade_signal.price * trade_signal.number)
                try:
                    self.asset.deposit(coin)
                    self.trade_history.append(trade_signal)
                    return Response(status=ActionStatus.success)
                except Exception as e:
                    return Response(status=ActionStatus.fail)
            else:
                return Response(status=ActionStatus.fail)
        else:
            raise ValueError(f'Invalid action: {trade_signal.action}')