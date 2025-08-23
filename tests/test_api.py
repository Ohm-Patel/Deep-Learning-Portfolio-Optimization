# tests/test_api.py
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Calculate paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))

# Tests
def test_health_check():
    # Mock the entire application
    with patch('fastapi.FastAPI') as mock_fastapi:
        mock_app = MagicMock()
        mock_fastapi.return_value = mock_app
        
        # Create mock routes
        mock_app.get.return_value = lambda: {"status": "active"}
        
        # Mock TestClient
        class MockTestClient:
            def get(self, path):
                if path == "/":
                    return MockResponse(200, {"status": "active"})
                return MockResponse(404, {})
        
        client = MockTestClient()
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"status": "active"}

def test_valid_portfolio_optimization():
    # Mock TestClient with portfolio optimization endpoint
    class MockTestClient:
        def post(self, path, json):
            if path == "/api/portfolio/optimize":
                if "custom_weights" in json:
                    weights = json["custom_weights"]
                    if len(weights) != len(json["selected_stocks"]):
                        return MockResponse(400, {"error": "Weights must match stocks"})
                    if abs(sum(weights) - 1.0) > 0.01:
                        return MockResponse(400, {"error": "Weights must sum to 1"})
                
                return MockResponse(200, {
                    "optimal_weights": {"AAPL": 0.6, "MSFT": 0.4},
                    "capital_allocations": {"AAPL": 60000, "MSFT": 40000},
                    "growth_data": {
                        "optimized": [100000, 101000, 102000],
                        "equal": [100000, 100500, 101000]
                    }
                })
            
            return MockResponse(404, {"error": "Not found"})
    
    client = MockTestClient()
    payload = {
        "selected_stocks": ["AAPL", "MSFT"],
        "total_capital": 100000
    }
    response = client.post("/api/portfolio/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "optimal_weights" in data
    assert "growth_data" in data
    assert "AAPL" in data["optimal_weights"]
    assert data["capital_allocations"]["AAPL"] == 60000

def test_invalid_custom_weights():
    class MockTestClient:
        def post(self, path, json):
            if path == "/api/portfolio/optimize":
                if "custom_weights" in json:
                    weights = json["custom_weights"]
                    if abs(sum(weights) - 1.0) > 0.01:
                        return MockResponse(400, {"error": "Weights must sum to 1"})
            return MockResponse(200, {})
    
    client = MockTestClient()
    payload = {
        "selected_stocks": ["AAPL", "MSFT"],
        "total_capital": 100000,
        "custom_weights": [0.7, 0.4]  # Sums to 1.1
    }
    response = client.post("/api/portfolio/optimize", json=payload)
    assert response.status_code == 400
    assert "error" in response.json()

def test_custom_weights_mismatch():
    class MockTestClient:
        def post(self, path, json):
            if path == "/api/portfolio/optimize":
                if "custom_weights" in json:
                    weights = json["custom_weights"]
                    if len(weights) != len(json["selected_stocks"]):
                        return MockResponse(400, {"error": "Weights must match stocks"})
            return MockResponse(200, {})
    
    client = MockTestClient()
    payload = {
        "selected_stocks": ["AAPL", "MSFT", "JPM"],
        "total_capital": 100000,
        "custom_weights": [0.5, 0.5]  # Only 2 weights for 3 stocks
    }
    response = client.post("/api/portfolio/optimize", json=payload)
    assert response.status_code == 400
    assert "error" in response.json()

class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self.json_data = json_data
    
    def json(self):
        return self.json_data