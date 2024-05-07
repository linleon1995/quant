from statemachine import StateMachine, State

from src.data_process.data_structure import MAMeta


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


class TestStateMachine(StateMachine):
    s0 = State(initial=True)
    s1 = State()
    s2 = State()
    s3 = State()

    steady = (
        s0.to(s1, cond='price_stable')
        | s0.to(s0, unless='price_stable')
    )
    rampup = (
        s1.to(s2, cond='price_rising')
        | s1.to(s0, unless='price_stable')
        | s1.to(s1, cond='price_stable')
    )
    buy = (
        s2.to(s3, cond='buy_complete')
        | s2.to(s2, unless='buy_complete')
    )
    sell = (
        s3.to(s0, cond='sell_complete')
        | s3.to(s3, unless='sell_complete')
    )
    run = steady | rampup | buy | sell

    def __init__(self, data_queue: MAMeta):
        self.data_queue = data_queue
        super(TestStateMachine, self).__init__()
        # self.allow_event_without_transition = True

    def receive(self, price, timestamp, trade_result=None):
        print('receive')
        self.data_queue.put_tick(tick=price, unix_time=timestamp)
        self.run()
    
    def price_stable(self):
        return len(self.data_queue.ticks) > 2
    
    def price_rising(self):
        return len(self.data_queue.ticks) == 4
    
    def buy_complete(self):
        return len(self.data_queue.ticks) == 5
    
    def sell_complete(self):
        return len(self.data_queue.ticks) == 6
