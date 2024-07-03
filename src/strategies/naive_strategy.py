from src.wallet import TradeRequest

class NaiveStrategy:
    def __init__(self, buy_rate: float, sell_rate: float):
        self.buy_rate = buy_rate
        self.sell_rate = sell_rate
        self.last_price = None
        self.state = 'init'

    def add_tick(self, symbol: str, price: float):
        if self.last_price is None:
            self.last_price = price
            return None

        if self.state == 'init' or self.state == 'sell':
            if price > self.last_price * (1 + self.buy_rate):
                self.last_price = price
                self.state = 'buy'
                return TradeRequest(action=self.state, number=1, symbol=symbol, price=price)
        elif self.state == 'buy':
            if price < self.last_price * (1 - self.sell_rate):
                self.last_price = price
                self.state = 'sell'
                return TradeRequest(action=self.state, number=1, symbol=symbol, price=price)
            
        self.last_price = price
        return None
    