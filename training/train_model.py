# training/train_model.py
import numpy as np
import pandas as pd
import joblib
import json
import os
import tensorflow as tf
from sklearn.preprocessing import RobustScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow import keras

# Configuration - same as your original parameters
SEQUENCE_LENGTH = 60
TRAIN_TEST_SPLIT = 0.8
MODEL_LAYERS = [
    {'units': 120, 'return_sequences': True, 'dropout': 0.1},
    {'units': 170, 'return_sequences': True, 'dropout': 0.1},
    {'units': 50, 'return_sequences': False, 'dropout': 0.1}
]
LEARNING_RATE = 1e-5
BATCH_SIZE = 32
EPOCHS = 100
ARTIFACTS_DIR = "../backend/artifacts"

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

def build_model(input_shape, output_units):
    """Construct the LSTM model architecture"""
    model = Sequential()
    for i, layer_config in enumerate(MODEL_LAYERS):
        if i == 0:
            model.add(LSTM(units=layer_config['units'], 
                          return_sequences=layer_config['return_sequences'],
                          input_shape=input_shape))
        else:
            model.add(LSTM(units=layer_config['units'], 
                          return_sequences=layer_config['return_sequences']))
        model.add(Dropout(layer_config['dropout']))
    
    model.add(Dense(units=output_units, activation='relu'))
    return model

def train_model():
    """Main training function"""
    # Create artifacts directory
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    
    print("Loading and preprocessing data...")
    df, close_cols = load_and_preprocess_data('dow30_data.csv')
    
    # Save ticker metadata
    ticker_metadata = {
        "all_tickers": [col.split("_")[0] for col in close_cols],
        "close_cols": close_cols
    }
    with open(f'{ARTIFACTS_DIR}/tickers.json', 'w') as f:
        json.dump(ticker_metadata, f)
    
    print(f"Found {len(close_cols)} stocks: {', '.join(ticker_metadata['all_tickers'])}")
    
    # Scale data
    scaler = RobustScaler()
    data_scaled = scaler.fit_transform(df)
    joblib.dump(scaler, f'{ARTIFACTS_DIR}/scaler.pkl')
    
    # Create sequences
    X, y = create_sequences(data_scaled, SEQUENCE_LENGTH)
    
    # Train/test split
    split_idx = int(TRAIN_TEST_SPLIT * len(X))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Save the last test sequence for simulations
    initial_window = X_test[-1]
    np.save(f'{ARTIFACTS_DIR}/initial_window.npy', initial_window)
    
    # Build and train model
    print("Building model...")
    model = build_model((X_train.shape[1], X_train.shape[2]), len(close_cols))
    model.compile(optimizer=Adam(learning_rate=LEARNING_RATE), 
                  loss='mean_squared_error')
    
    callbacks = [
        EarlyStopping(monitor='loss', min_delta=1e-10, patience=10, verbose=1),
        ReduceLROnPlateau(monitor='loss', factor=0.5, patience=10, verbose=1)
    ]
    
    print("Training model...")
    history = model.fit(
        X_train, y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        validation_split=0.2,
        shuffle=True
    )
    
    # Save model
    model.save(f'{ARTIFACTS_DIR}/model.h5')
    
    # Evaluate model
    y_pred_scaled = model.predict(X_test)
    y_pred_actual = scaler.inverse_transform(y_pred_scaled)
    y_test_actual = scaler.inverse_transform(y_test)
    
    mae = np.mean(np.abs(y_test_actual - y_pred_actual))
    rmse = np.sqrt(np.mean((y_test_actual - y_pred_actual)**2))
    
    print("\nModel Evaluation:")
    print(f"MAE: ${mae:.2f}")
    print(f"RMSE: ${rmse:.2f}")
    
    # Save evaluation metrics
    with open(f'{ARTIFACTS_DIR}/metrics.json', 'w') as f:
        json.dump({"MAE": float(mae), "RMSE": float(rmse)}, f)
    
    print(f"\nArtifacts saved to {ARTIFACTS_DIR}")

if __name__ == "__main__":
    train_model()