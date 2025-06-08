


# Assuming a singleton implementation for Market
class Market:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Market, cls).__new__(cls)
            # cls._instance._init()
        return cls._instance

    # def _init(self, wallet, db_operator):
    #     self.wallet = wallet
    #     self.db_operator = db_operator
    #     self.trades = []

    def __init__(self, wallet, db_operator):
        self.wallet = wallet
        self.db_operator = db_operator
        self.trades = []
        self.ticker_data = {} # Initialize ticker_data

    def get_wallet(self):
        return self.wallet

    def get_ticker(self, symbol_or_symbols, start_time, end_time):
        if start_time > end_time:
            raise ValueError("Start time cannot be after end time.")

        results = []
        symbols_to_query = []

        if isinstance(symbol_or_symbols, str):
            symbols_to_query = [symbol_or_symbols]
        elif isinstance(symbol_or_symbols, list):
            symbols_to_query = symbol_or_symbols
        else:
            raise TypeError("Symbol must be a string or a list of strings.")

        for symbol_str in symbols_to_query:
            if symbol_str not in self.ticker_data:
                # If a specific symbol (or one in a list) is not found, raise ValueError.
                raise ValueError(f"Symbol {symbol_str} not found in ticker_data.")

            ticks = self.ticker_data.get(symbol_str, []) # Should always find it now due to check above
            results.extend([tick for tick in ticks
                            if start_time <= tick['time'] <= end_time])

        return results


    def add_trade(self, symbol, trade_type, quantity, price):
        trade = {'symbol': symbol, 'type': trade_type, 'quantity': quantity, 'price': price}
        self.trades.append(trade)
        # Update wallet based on trade
        if trade_type == 'buy':
            self.wallet.adjust_balance(-price * quantity)
        elif trade_type == 'sell':
            self.wallet.adjust_balance(price * quantity)