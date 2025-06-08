import pytest
from typing import List, Any, Dict

from src.strategy.strategy_executor import StrategyExecutor
from src.data_process.product_state import ProductState
from tests.mocks import MockStrategy


@pytest.fixture
def executor_with_strategies():
    """Set up for test methods."""
    executor = StrategyExecutor()
    mock_strategy1 = MockStrategy(name="Strat1")
    mock_strategy2 = MockStrategy(name="Strat2", signals_to_return=[{"action": "buy", "product": "BTCUSD"}])
    return executor, mock_strategy1, mock_strategy2


class TestStrategyExecutor:

    # Test Strategy Registration and ProductState Creation
    def test_register_single_strategy_single_product(self, executor_with_strategies):
        executor, mock_strategy1, _ = executor_with_strategies
        executor.register_strategy(mock_strategy1, ["BTCUSD"])
        assert "BTCUSD" in executor.strategies
        assert mock_strategy1 in executor.strategies["BTCUSD"]
        assert "BTCUSD" in executor.product_states
        assert isinstance(executor.product_states["BTCUSD"], ProductState)

    def test_register_single_strategy_multiple_products(self, executor_with_strategies):
        executor, mock_strategy1, _ = executor_with_strategies
        executor.register_strategy(mock_strategy1, ["BTCUSD", "ETHUSD"])
        assert mock_strategy1 in executor.strategies["BTCUSD"]
        assert mock_strategy1 in executor.strategies["ETHUSD"]
        assert "BTCUSD" in executor.product_states
        assert "ETHUSD" in executor.product_states
        assert isinstance(executor.product_states["BTCUSD"], ProductState)
        assert isinstance(executor.product_states["ETHUSD"], ProductState)

    def test_register_multiple_strategies_single_product(self, executor_with_strategies):
        executor, mock_strategy1, mock_strategy2 = executor_with_strategies
        executor.register_strategy(mock_strategy1, ["BTCUSD"])
        executor.register_strategy(mock_strategy2, ["BTCUSD"])
        assert len(executor.strategies["BTCUSD"]) == 2
        assert mock_strategy1 in executor.strategies["BTCUSD"]
        assert mock_strategy2 in executor.strategies["BTCUSD"]

    # Test get_product_state
    def test_get_product_state_existing(self, executor_with_strategies):
        executor, mock_strategy1, _ = executor_with_strategies
        executor.register_strategy(mock_strategy1, ["BTCUSD"])  # Creates the state
        ps = executor.get_product_state("BTCUSD")
        assert isinstance(ps, ProductState)
        assert ps.product_id == "BTCUSD"

    def test_get_product_state_new(self, executor_with_strategies):
        executor, _, _ = executor_with_strategies
        ps = executor.get_product_state("ETHUSD")  # Should create on demand
        assert "ETHUSD" in executor.product_states
        assert isinstance(ps, ProductState)
        assert ps.product_id == "ETHUSD"

    # Test on_market_data Basic Operation
    def test_on_market_data_updates_product_state(self, executor_with_strategies):
        executor, mock_strategy1, _ = executor_with_strategies
        executor.register_strategy(mock_strategy1, ["BTCUSD"])
        market_data = {"price": 50000, "timestamp": 1234567890}
        executor.on_market_data("BTCUSD", market_data)
        product_state = executor.product_states["BTCUSD"]
        assert product_state.get_market_data('latest_data') == market_data

    def test_on_market_data_calls_strategy_initialize_and_handle_data(self, executor_with_strategies):
        executor, mock_strategy1, _ = executor_with_strategies
        executor.register_strategy(mock_strategy1, ["BTCUSD"])
        market_data = {"price": 51000}

        # Initial call to on_market_data
        executor.on_market_data("BTCUSD", market_data)
        assert mock_strategy1.initialize_called_with is not None
        # Check if it's an empty dict as passed by StrategyExecutor
        assert mock_strategy1.initialize_called_with == {}
        assert len(mock_strategy1.handle_data_calls) == 1
        call_args = mock_strategy1.handle_data_calls[0]
        assert call_args['product_id'] == "BTCUSD"
        assert call_args['data'] == market_data
        assert call_args['product_state_type'] == ProductState
        assert call_args['product_state_id'] == "BTCUSD"

        # Second call to ensure initialize is not called again
        market_data2 = {"price": 51500}
        executor.on_market_data("BTCUSD", market_data2)
        # initialize_called_with should remain the same, not called again
        assert mock_strategy1.initialize_called_with == {}
        assert len(mock_strategy1.handle_data_calls) == 2 # handle_data called again
        call_args2 = mock_strategy1.handle_data_calls[1]
        assert call_args2['data'] == market_data2


    def test_on_market_data_routes_to_correct_strategy(self, executor_with_strategies):
        executor, mock_strategy1, mock_strategy2 = executor_with_strategies
        executor.register_strategy(mock_strategy1, ["BTCUSD"])
        executor.register_strategy(mock_strategy2, ["ETHUSD"])

        # Data for BTCUSD
        executor.on_market_data("BTCUSD", {"price": 52000})
        assert len(mock_strategy1.handle_data_calls) == 1
        assert len(mock_strategy2.handle_data_calls) == 0
        assert mock_strategy1.initialize_called_with is not None # Strat1 initialized
        assert mock_strategy2.initialize_called_with is None # Strat2 not yet

        # Data for ETHUSD
        executor.on_market_data("ETHUSD", {"price": 4000})
        assert len(mock_strategy1.handle_data_calls) == 1  # Unchanged
        assert len(mock_strategy2.handle_data_calls) == 1
        assert mock_strategy2.initialize_called_with is not None # Strat2 initialized now

    def test_on_market_data_collects_signals(self, executor_with_strategies):
        executor, _, mock_strategy2 = executor_with_strategies
        executor.register_strategy(mock_strategy2, ["BTCUSD"])  # mock_strategy2 returns a signal
        signals = executor.on_market_data("BTCUSD", {"price": 53000})
        assert len(signals) == 1
        assert signals[0] == {"action": "buy", "product": "BTCUSD"}

    def test_on_market_data_no_strategies_for_product(self, executor_with_strategies):
        executor, _, _ = executor_with_strategies
        # Market data for a product with no registered strategies
        signals = executor.on_market_data("DOGEUSD", {"price": 0.5})
        # ProductState should still be created
        assert "DOGEUSD" in executor.product_states
        assert isinstance(executor.product_states["DOGEUSD"], ProductState)
        # No signals should be generated
        assert len(signals) == 0

    # Test Chain Mode Placeholder
    def test_run_chain_mode_for_product_raises_not_implemented(self, executor_with_strategies):
        executor, _, _ = executor_with_strategies
        with pytest.raises(NotImplementedError):
            executor.run_chain_mode_for_product("BTCUSD", {"price": 123})
