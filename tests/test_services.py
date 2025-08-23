# tests/test_services.py
import sys
import os
import pytest
import numpy as np

# Add necessary paths to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, os.path.join(project_root, "backend/app/services"))

from optimizer import PortfolioOptimizer
from simulation import MonteCarloSimulator

def test_monte_carlo_simulator(mock_model_loader):
    """Test Monte Carlo simulation"""
    # Configure mock model prediction
    mock_model_loader.model.predict.return_value = np.array([[0.15, 0.25]])
    
    simulator = MonteCarloSimulator(mock_model_loader)
    path = simulator.simulate_path(n_days=2, noise_std=0.0)
    
    # Assertions
    assert path.shape == (2, 2)
    assert np.array_equal(path, np.array([[15.0, 25.0], [15.0, 25.0]]))

def test_portfolio_optimizer(mock_model_loader, mock_simulator):
    """Test portfolio optimizer"""
    optimizer = PortfolioOptimizer(mock_model_loader, mock_simulator)
    report = optimizer.generate_report(["AAPL", "MSFT"], 100000)
    
    # Assertions
    assert "optimal_weights" in report
    assert "capital_allocations" in report
    assert "growth_data" in report
    
    weights = list(report["optimal_weights"].values())
    assert sum(weights) == pytest.approx(1.0, abs=0.01)
    assert report["capital_allocations"]["AAPL"] == pytest.approx(weights[0] * 100000)
    assert report["capital_allocations"]["MSFT"] == pytest.approx(weights[1] * 100000)
    
    assert len(report["growth_data"]["optimized"]) == 3
    assert len(report["growth_data"]["equal"]) == 3
    assert report["growth_data"]["optimized"][0] == 100000