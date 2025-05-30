import os
import onnxruntime
import numpy as np
import requests # For downloading the model
from pathlib import Path

from src.strategies.rl_base_strategy import RLStrategyBase
from src.data_process.data_structure import GeneralTickData # Assuming this is the expected input

# Define the model URL and local path
MODEL_URL = "https://huggingface.co/aai540-group3/diabetes-readmission/resolve/main/model.onnx"
MODEL_DIR = Path("models/rl_demo_model")
MODEL_PATH = MODEL_DIR / "model.onnx"

# Expected input feature dimension for the ONNX model.
# This needs to be determined by inspecting the model or its documentation.
# For aai540-group3/diabetes-readmission, it has many features.
# We'll use a placeholder dimension and then refine if possible by inspecting the model with onnxruntime.
# From preprocessing_config.json:
# numeric_features: 19
# binary_features: 4 (assume these are 0/1)
# medication_features: 21 (assume these are 0/1)
# interaction_features: 12 (likely numeric)
# ratio_features: 3 (likely numeric)
# categorical_features (one-hot encoded):
#   admission_type_id: 8 values -> 8 features
#   discharge_disposition_id: 26 values -> 26 features
#   admission_source_id: 25 values -> 25 features
#   level1_diag1: 9 values -> 9 features
#   Total categorical one-hot: 8 + 26 + 25 + 9 = 68
# lab_features:
#   a1cresult: mapped to numeric (e.g., 1 feature)
#   max_glu_serum: mapped to numeric (e.g., 1 feature)
# Total features approx: 19 + 4 + 21 + 12 + 3 + 68 + 2 = 129
# This is an estimate. The ONNX model's input metadata is the source of truth.
# Let's assume for now the model takes a flat float32 vector.
# We will confirm this when loading the model.
EXPECTED_INPUT_DIM = 129 # Placeholder, will be derived from model's input metadata

class DemoRLStrategy(RLStrategyBase):
    def __init__(self, model_path: str = str(MODEL_PATH)):
        self.expected_input_dim = None # Will be set after model loading
        super().__init__(model_path) # Calls _load_model

    def _download_model_if_not_exists(self):
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        if not MODEL_PATH.exists():
            print(f"Downloading demo RL model from {MODEL_URL} to {MODEL_PATH}...")
            try:
                response = requests.get(MODEL_URL, stream=True)
                response.raise_for_status()
                with open(MODEL_PATH, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print("Model downloaded successfully.")
            except requests.exceptions.RequestException as e:
                print(f"Error downloading model: {e}")
                # Handle error appropriately, maybe raise it or use a fallback
                raise

    def _load_model(self, model_path: str) -> any:
        self._download_model_if_not_exists()
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Demo RL model not found at {MODEL_PATH} and download failed.")

        try:
            print(f"Loading ONNX model from: {model_path}")
            session = onnxruntime.InferenceSession(model_path)
            
            # Get input details
            input_meta = session.get_inputs()[0]
            self.expected_input_dim = input_meta.shape[-1] # Assuming (batch_size, num_features)
            print(f"Model loaded. Expected input name: {input_meta.name}, shape: {input_meta.shape}, type: {input_meta.type}")
            
            # If the shape is dynamic (None) for number of features, we might need a fixed size based on documentation.
            # For now, we rely on the last dimension of the shape.
            if not isinstance(self.expected_input_dim, int):
                 print(f"Warning: Could not dynamically determine input dimension from model shape {input_meta.shape}. Using predefined {EXPECTED_INPUT_DIM}")
                 self.expected_input_dim = EXPECTED_INPUT_DIM


            return session
        except Exception as e:
            print(f"Error loading ONNX model: {e}")
            # Handle error, e.g., by returning None or raising exception
            raise

    def get_observation(self, tick_data: GeneralTickData) -> np.ndarray:
        """
        Generates a dummy observation matching the model's expected input shape.
        In a real scenario, this would involve feature engineering from tick_data.
        """
        if self.model is None:
            raise ValueError("Model is not loaded.")
        if self.expected_input_dim is None:
            # This case should ideally be handled by _load_model ensuring expected_input_dim is set
            raise ValueError("Expected input dimension not set. Model loading might have failed or model metadata is unusual.")

        # Create a dummy observation vector of the correct shape and type (float32 is common for ONNX)
        # This part is purely for demonstration as we are not using actual financial features for this diabetes model.
        print(f"Generating dummy observation for model. Expected dimension: {self.expected_input_dim}")
        
        # Example: Create a feature vector based on latest price, volume, etc. from tick_data
        # For this demo, we just create zeros.
        # features = [
        #     tick_data.latest_price,
        #     tick_data.volume,
        #     # ... more features, up to self.expected_input_dim
        # ]
        # # Ensure the feature vector has the correct length
        # observation_vector = (features + [0.0] * self.expected_input_dim)[:self.expected_input_dim]

        observation_vector = np.zeros(self.expected_input_dim)
        
        return observation_vector.astype(np.float32).reshape(1, -1) # Reshape for batch size 1

    def generate_signal(self, observation: np.ndarray) -> str:
        """
        Generates a trading signal based on the dummy model's prediction.
        """
        if self.model is None:
            raise ValueError("Model is not loaded.")

        input_name = self.model.get_inputs()[0].name
        
        try:
            # Perform inference
            # Output is typically a list of arrays, one for each output of the model
            # For this classification model, it might be probabilities or class labels
            model_output = self.model.run(None, {input_name: observation})
            
            # Assuming the model outputs probabilities for 2 classes [prob_class_0, prob_class_1]
            # or just the predicted class label.
            # Let's inspect the first output.
            prediction = model_output[0] 
            print(f"Model output: {prediction}")

            # Interpret the prediction:
            # The config.json for aai540-group3/diabetes-readmission indicates:
            # "id2label": { "0": "NO_READMISSION", "1": "READMISSION" }
            # If prediction is probabilities, take argmax. If it's already a label, use it.
            if isinstance(prediction, np.ndarray) and prediction.ndim == 2: # e.g., [[prob0, prob1]]
                predicted_class = np.argmax(prediction, axis=1)[0]
            elif isinstance(prediction, np.ndarray) and prediction.ndim == 1 : # e.g. [label] for batch size 1
                 predicted_class = prediction[0]
            else: # if it's a scalar
                predicted_class = prediction

            if predicted_class == 1: # 'READMISSION'
                return "BUY" # Arbitrary mapping for demo
            else: # 'NO_READMISSION'
                return "SELL" # Arbitrary mapping for demo
            # Could also include "HOLD" based on confidence or other logic

        except Exception as e:
            print(f"Error during model inference or signal generation: {e}")
            return "HOLD" # Fallback signal

if __name__ == '__main__':
    # Example Usage (requires GeneralTickData to be defined and importable)
    print("Running DemoRLStrategy example...")
    try:
        strategy = DemoRLStrategy()
        
        # Create a dummy GeneralTickData object for testing
        # This needs to be adjusted based on how GeneralTickData is structured
        class MockGeneralTickData:
            def __init__(self, latest_price, volume):
                self.latest_price = latest_price
                self.volume = volume
                # Add any other fields that get_observation might hypothetically access
                # even if the current dummy get_observation doesn't use them.

        # Create a mock tick data instance
        # Values don't matter much as get_observation creates a dummy vector
        mock_data = MockGeneralTickData(latest_price=100.0, volume=1000.0)

        if strategy.model:
            print(f"Demo model loaded successfully. Input dimension: {strategy.expected_input_dim}")
            observation = strategy.get_observation(mock_data)
            print(f"Generated dummy observation: {observation.shape}")
            signal = strategy.generate_signal(observation)
            print(f"Generated signal: {signal}")
        else:
            print("Failed to load the demo model.")

    except Exception as e:
        print(f"An error occurred in the example: {e}")
