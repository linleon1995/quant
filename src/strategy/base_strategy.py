from abc import ABC, abstractmethod
from typing import List, Any
from statemachine import State, StateMachine

from src.data_process.data_structure import GeneralTickData

# TODO: Refine Signal type, e.g. using a dataclass with fields like type: str and details: dict
Signal = Any


class Strategy(ABC):
    """
    Interface for trading strategies.
    """

    def initialize(self, config: dict) -> None:
        """
        Initializes the strategy with the given configuration.
        This method is called once before the strategy starts handling data.
        Args:
            config: A dictionary containing configuration parameters for the strategy.
        """
        pass

    @abstractmethod
    def handle_data(self, product_id: str, data: Any, product_state: 'ProductState') -> List[Signal]:
        """
        Processes incoming market data and generates trading signals.
        Args:
            product_id: The identifier of the product.
            data: The incoming market data.
            product_state: The current state of the product.
        Returns:
            A list of trading signals.
        """
        pass


# Keep Strategy stateless and make sure StrategyExecuter taking good care of it.
# Legacy component
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
    break_last_low = (
        s3.to(s0, cond='sell_complete')
        | s3.to(s3, unless='sell_complete')
    )
    run = steady | rampup | buy | break_last_low

    def __init__(self, data_queue: GeneralTickData):
        self.data_queue = data_queue
        self.stable_count = 0
        super(TestStateMachine, self).__init__()
        # self.allow_event_without_transition = True

    def receive(self, price, timestamp, trade_result=None):
        print('receive')
        self.data_queue.put_tick(tick=price, unix_time=timestamp)
        self.run()
    
    def receive_trade_response(self, trade_response):
        if trade_response.result == 'buy success':
            self.buy_success = True
        elif trade_response.result == 'sell success':
            self.sell_success = True
        else:
            raise ValueError('Invalid trade response.')

    # TODO: std, time range to decide, consider Bollinger Bands
    def price_stable(self):
        if not self.data_queue.ticks:
            return False
        latest_price = self.data_queue.ticks[-1]

        # Check if bollinger_band attribute exists and has the required sub-attributes
        if hasattr(self.data_queue, 'bollinger_band') and \
           hasattr(self.data_queue.bollinger_band, 'upper_bound') and \
           hasattr(self.data_queue.bollinger_band, 'lower_bound'):
            upper_bound = self.data_queue.bollinger_band.upper_bound
            lower_bound = self.data_queue.bollinger_band.lower_bound
            if latest_price < upper_bound and latest_price > lower_bound: # Corrected condition: price should be WITHIN bounds
                self.stable_count += 1
            else:
                self.stable_count = 0
        else:
            # If no bollinger_band data, cannot determine stability based on it.
            # Option: treat as not stable, or use another logic. For now, not stable.
            self.stable_count = 0
            # Or, if some default behavior is desired without BB:
            # self.stable_count += 1 # Example: assume stable if no BB info

        if self.stable_count > 120: # Hardcoded, was previously stable_length in test
            return True
        else:
            return False
    
    def price_rising(self):
        if not self.data_queue.ticks or len(self.data_queue.ticks) < 2: # Need at least two points for a slope
            return False
        # This is a placeholder for slope. GeneralTickData doesn't have 'slope'.
        # Assuming self.data_queue.moving_average_data_pool might be used.
        # For example, compare short MA to long MA, or check slope of an MA.
        # Let's use a simple price change for now if slope is not available.
        if hasattr(self.data_queue, 'slope'): # Ideal case
            if self.data_queue.slope > 0.1:
                return True
        elif len(self.data_queue.ticks) >= 2: # Fallback to simple price change
             if self.data_queue.ticks[-1] > self.data_queue.ticks[-2]: # Price increased
                 return True
        return False
    
    def buy_complete(self):
        self.buy_success = False
        return True
    
    def sell_complete(self):
        self.sell_success = False
        return True
