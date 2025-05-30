import abc
from src.data_process.data_structure import GeneralTickData # Assuming GeneralTickData is the relevant data structure

class RLStrategyBase(abc.ABC):
    def __init__(self, model_path: str):
        """
        Initializes the RL strategy base.
        
        Args:
            model_path (str): Path to the pre-trained RL model.
        """
        self.model_path = model_path
        self.model = self._load_model(model_path)

    @abc.abstractmethod
    def _load_model(self, model_path: str) -> any:
        """
        Loads the RL model from the specified path.
        This method should be implemented by subclasses to handle specific model types.
        """
        pass

    @abc.abstractmethod
    def get_observation(self, tick_data: GeneralTickData) -> any:
        """
        Transforms the incoming tick_data into an observation format suitable for the RL model.

        Args:
            tick_data (GeneralTickData): The current market data.

        Returns:
            any: The observation for the RL model.
        """
        pass

    @abc.abstractmethod
    def generate_signal(self, observation: any) -> str:
        """
        Generates a trading signal ('BUY', 'SELL', 'HOLD') based on the model's prediction.

        Args:
            observation (any): The observation processed by get_observation.

        Returns:
            str: The trading signal.
        """
        pass

    # Optional: A method to run the strategy for a given tick, similar to StrategyExecuter
    # This can be fleshed out more once the interaction model is clearer.
    def decide_action(self, tick_data: GeneralTickData) -> str:
        """
        Processes the latest tick data and decides on a trading action.
        """
        observation = self.get_observation(tick_data)
        signal = self.generate_signal(observation)
        return signal

if __name__ == '__main__':
    # This section can be used for basic testing or examples later
    print("RLStrategyBase defined. Subclasses should implement the abstract methods.")

    # Example of how a subclass might look (for illustration purposes):
    # class MySpecificRLStrategy(RLStrategyBase):
    #     def _load_model(self, model_path: str) -> any:
    #         # Replace with actual model loading logic, e.g., using joblib, tensorflow, pytorch
    #         print(f"Loading model from {model_path}")
    #         return "dummy_model" 
    #
    #     def get_observation(self, tick_data: GeneralTickData) -> any:
    #         # Replace with actual observation transformation
    #         print(f"Generating observation from {tick_data}")
    #         return {"price": tick_data.latest_price} # Example
    #
    #     def generate_signal(self, observation: any) -> str:
    #         # Replace with actual signal generation logic using the model
    #         print(f"Generating signal from {observation}")
    #         if observation.get("price", 0) > 100: # Dummy logic
    #             return "BUY"
    #         elif observation.get("price", 0) < 90:
    #             return "SELL"
    #         return "HOLD"
    #
    # # Example usage (will require GeneralTickData and a model path if uncommented)
    # # from src.data_process.data_structure import GeneralTickData
    # #
    # # class MockGeneralTickData: # Create a mock if GeneralTickData is complex
    # #     def __init__(self, latest_price):
    # #         self.latest_price = latest_price
    # #
    # # if __name__ == '__main__':
    # #     strategy = MySpecificRLStrategy(model_path="path/to/dummy/model")
    # #     mock_data = MockGeneralTickData(latest_price=105)
    # #     signal = strategy.decide_action(mock_data)
    # #     print(f"Generated signal: {signal}")
