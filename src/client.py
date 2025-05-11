

class backtest_client:
    def __init__(self, markets, wallet) -> None:
        self.markets = markets
        self.wallet = wallet

    def send_trade(self, trade_request):
        pass

    def get_tick(self, symbol):
        return self.markets.get(symbol).get_tick()

    def get_asset(self):
        return self.wallet.get_asset()

    def get_balance(self):
        pass


class trader:
    def __init__(self, client) -> None:
        self.client = client

    def send_trade(self, trade_request):
        trade_response = self.client.send_trade(trade_request)
