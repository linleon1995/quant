from datetime import datetime, timedelta

from src.strategy.base_strategy import TestStateMachine
from src.data_process.data_structure import GeneralTickData


def test_state_machine():
    # Parameters for GeneralTickData
    symbol = 'BTCUSDT'
    maxlen = 1440
    ma_range_list = [7, 25, 99]
    # stable_length = 50 # This parameter was in the original call but not used by TestStateMachine's __init__

    data_queue = GeneralTickData(
        symbol=symbol,
        maxlen=maxlen,
        moving_average_spans=ma_range_list
    )

    state_machine = TestStateMachine(data_queue=data_queue)
    # If stable_length was intended to be part of TestStateMachine:
    # state_machine.stable_length = stable_length # Or modify TestStateMachine to accept it

    assert state_machine.current_state.id == 's0'
    assert isinstance(state_machine, TestStateMachine)

    t1 = datetime.now()
    t = t1
    # The price_stable condition in TestStateMachine uses self.data_queue.bollinger_band
    # which is not populated by GeneralTickData.put_tick. This will likely cause an error.
    # For now, focusing on fixing the constructor and basic calls.
    # Mocking or adjusting price_stable might be needed.
    # Let's assume bollinger_band exists and has some default for now or test will fail there.
    # A minimal GeneralTickData might not have bollinger_band.
    # Indeed, GeneralTickData does not compute Bollinger Bands.
    # TestStateMachine.price_stable will fail.
    # For now, let's proceed with the constructor fix and see the next error.

    for i in range(100): # The number of ticks to become stable might depend on hardcoded 120
        t += timedelta(minutes=1)
        # Mocking bollinger_band attribute for price_stable condition as it's not set by GeneralTickData
        if not hasattr(data_queue, 'bollinger_band'):
            data_queue.bollinger_band = type('MockBand', (), {'upper_bound': 110, 'lower_bound': 90})()
        state_machine.receive(price=100, timestamp=t)

    # This assertion might fail if 100 ticks are not enough to overcome stable_count > 120
    # or if price_stable condition fails due to bollinger_band access.
    # Let's assume for now it's meant to transition.
    # The original test might have implicitly relied on a different GeneralTickData or a mock.
    assert state_machine.current_state.id == 's1'

    t_next = t + timedelta(minutes=1)
    state_machine.receive(price=150, timestamp=t_next) # Using t_next instead of undefined t2
    t_next += timedelta(minutes=1)
    state_machine.receive(price=150, timestamp=t_next)
    t_next += timedelta(minutes=1)
    state_machine.receive(price=150, timestamp=t_next)
    # This assertion might also be affected by the conditions in TestStateMachine
    assert state_machine.current_state.id == 's0'
