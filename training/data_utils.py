# training/data_utils.py
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler

def load_and_preprocess_data(file_path):
    """Load and clean the stock data"""
    df = pd.read_csv(file_path, index_col='timestamp', parse_dates=True)
    df = df.iloc[:, 1:]  # Remove empty first column
    df = df.ffill().bfill()  # Fill missing values
    
    # Use only _close columns
    close_cols = [col for col in df.columns if '_close' in col]
    df = df[close_cols]
    
    # Drop constant columns
    constant_cols = df.columns[df.nunique() <= 1]
    df = df.drop(columns=constant_cols)
    close_cols = [col for col in close_cols if col not in constant_cols]
    
    return df, close_cols

def create_sequences(data_scaled, sequence_length):
    """Create time-series sequences for LSTM"""
    X, y = [], []
    for i in range(sequence_length, len(data_scaled)):
        X.append(data_scaled[i-sequence_length:i])
        y.append(data_scaled[i])
    return np.array(X), np.array(y)