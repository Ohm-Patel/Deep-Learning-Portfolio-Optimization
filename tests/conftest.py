# tests/conftest.py
import pytest
import numpy as np
from unittest.mock import MagicMock

@pytest.fixture
def mock_model_loader():
    class MockModelLoader:
        def __init__(self):
            self.model = MagicMock()
            self.scaler = MagicMock()
            self.initial_window = np.array([[0.1, 0.2], [0.2, 0.3]])
            self.close_cols = ["AAPL_close", "MSFT_close"]
            self.all_tickers = ["AAPL", "MSFT"]
            
            # Configure scaler behavior
            self.scaler.inverse_transform = MagicMock(
                side_effect=lambda x: x * 100  # Simple scaling for testing
            )
        
        def get_stock_indices(self, selected_tickers):
            return [0, 1]  # Both stocks
    
    return MockModelLoader()

@pytest.fixture
def mock_simulator(mock_model_loader):
    class MockSimulator:
        def run_simulations(self, n_simulations, n_days):
            # Return fixed paths for testing
            return [
                np.array([[100, 200], [105, 210], [110, 220]]),
                np.array([[101, 201], [106, 211], [111, 221]])
            ]
    
    return MockSimulator()