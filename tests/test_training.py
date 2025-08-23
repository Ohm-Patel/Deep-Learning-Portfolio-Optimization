# tests/test_training.py
import sys
import os
import pytest
import pandas as pd
import numpy as np

# Add necessary paths to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, os.path.join(project_root, "training"))

from data_utils import load_and_preprocess_data, create_sequences

def test_data_loading(tmp_path):
    """Test data loading and preprocessing"""
    # Create test CSV
    test_csv = tmp_path / "test_data.csv"
    test_csv.write_text("""timestamp,empty,AAPL_close,MSFT_close,INVALID
2023-01-01,,150.0,300.0,100
2023-01-02,,151.0,302.0,100
2023-01-03,,149.0,299.0,100""")
    
    df, close_cols = load_and_preprocess_data(str(test_csv))
    
    # Assertions
    assert len(df.columns) == 2
    assert 'AAPL_close' in close_cols
    assert 'MSFT_close' in close_cols
    assert 'INVALID' not in close_cols
    assert df.index[0].strftime('%Y-%m-%d') == '2023-01-01'
    assert df.iloc[0,0] == 150.0
    assert df.iloc[1,1] == 302.0

def test_sequence_creation():
    """Test sequence generation logic"""
    test_data = np.array([[1.0, 2.0], [2.0, 3.0], [3.0, 4.0], [4.0, 5.0]])
    X, y = create_sequences(test_data, sequence_length=2)
    
    # Assertions
    assert len(X) == 2
    assert len(y) == 2
    assert np.array_equal(X[0], np.array([[1.0, 2.0], [2.0, 3.0]]))
    assert np.array_equal(y[0], np.array([3.0, 4.0]))
    assert np.array_equal(X[1], np.array([[2.0, 3.0], [3.0, 4.0]]))
    assert np.array_equal(y[1], np.array([4.0, 5.0]))