from dataclasses import dataclass, field
from collections import deque

from src.wallet import TradeRequest, BaseWallet

@dataclass
class OneStock:
    symbol: str
    # number: list
    # prices: list
    trade_history: list = field(default_factory=list)

    @property
    def avg_cost(self):
        return sum([trade_data.price for trade_data in self.trade_history]) / len(self.trade_history)
    
    @property
    def number(self):
        return sum([trade_data.number for trade_data in self.trade_history])

@dataclass
class EvalResult:
    avg_roi: float
    max_roi: float
    min_roi: float
    trade_times: int
    win_rate: float
    start_timestamp: str = None
    end_timestamp: str = None


# TODO: 假設前提為無資金假設，所有的交易都可以被完成，考慮這種情況的策略表現
class Evaluator:
    def __init__(self):
        self.init_money = {'USDT': 10000}
        self.stocks = {}

    def collect(self):
        pass

    def group_symbol(self, trade_history: deque):
        group_trade_history = {}
        for trade in trade_history:
            if group_trade_history.get(trade.symbol) is None:
                group_trade_history[trade.symbol] = []
            group_trade_history[trade.symbol].append(trade)
        return group_trade_history

    def eval(self, wallet: BaseWallet) -> EvalResult:
        if len(wallet.trade_history) == 0:
            return None
        
        total_profit = 0
        max_profit = float('-inf')
        min_profit = float('inf')
        win_count = 0
        total_trades_value = 0

        trade_history = self.group_symbol(wallet.trade_history)
        balance = {symbol: 0 for symbol in trade_history}
        for symbol, trade_history in trade_history.items():
            for trade in trade_history:
                if trade.action == 'buy':
                    balance[symbol] += trade.number
                elif trade.action == 'sell':
                    balance[symbol] -= trade.number
                    




        for trade in wallet.trade_history:
            if trade.symbol not in self.stocks:
                self.stocks[trade.symbol] = OneStock(symbol=trade.symbol)


            trade_value = trade.number * trade.price
            if trade.action == 'buy':
                total_trades_value += trade_value
            elif trade.action == 'sell':
                total_trades_value -= trade_value
                profit = trade_value - (trade.number * trade.bridgecoin_price)
                total_profit += profit
                max_profit = max(max_profit, profit)
                min_profit = min(min_profit, profit)
                if profit > 0:
                    win_count += 1

        if min_profit == float('inf') or max_profit == float('-inf'):
            return None
        
        trade_times = len(wallet.trade_history)
        avg_roi = (total_profit / total_trades_value) * 100 if total_trades_value > 0 else 0
        win_rate = (win_count / trade_times) * 100 if trade_times > 0 else 0

        # # Assuming trade history has timestamps for start and end trades
        # start_timestamp = wallet.trade_history[0].timestamp if wallet.trade_history else None
        # end_timestamp = wallet.trade_history[-1].timestamp if wallet.trade_history else None

        return EvalResult(
            avg_roi=avg_roi,
            max_roi=max_profit,
            min_roi=min_profit,
            trade_times=trade_times,
            win_rate=win_rate
        )

    def add_trade(self, trade_data: TradeRequest):
        if trade_data.action == 'buy':
            if trade_data.symbol not in self.stocks:
                self.stocks[trade_data.symbol] = OneStock(symbol=trade_data.symbol)
            
            self.stocks[trade_data.symbol].trade_history.append(trade_data)
