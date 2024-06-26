from dataclasses import dataclass, field

from src.wallet import TradeRequest

@dataclass
class OneStock:
    symbol: str
    # number: list
    # prices: list
    trade_history: list = field(default_factory=list)

    @property
    def avg_cost(self):
        return sum([trade_data.altcoin_price for trade_data in self.trade_history]) / len(self.trade_history)
    
    @property
    def number(self):
        return sum([trade_data.number for trade_data in self.trade_history])



# TODO: 假設前提為無資金假設，所有的交易都可以被完成，考慮這種情況的策略表現
class Evaluator:
    def __init__(self):
        self.init_money = {'USDT': 10000}
        self.stocks = {}

    def collect(self):
        pass

    def eval(self, wallet):
        pass

    def add_trade(self, trade_data: TradeRequest):
        if trade_data.action == 'buy':
            if trade_data.symbol not in self.stocks:
                self.stocks[trade_data.symbol] = OneStock(symbol=trade_data.symbol)
            
            self.stocks[trade_data.symbol].trade_history.append(trade_data)
