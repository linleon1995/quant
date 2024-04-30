
# Keep Strategy stateless and make sure StrategyExecuter taking good care of it.
class StrategyExecuter:
    def run(self, tic):
        self.collect(tic)
        trade_signal = self.strategy()
        return trade_signal

    def collect(self):
        pass

    def strategy(self):
        pass

