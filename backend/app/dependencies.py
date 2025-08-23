# app/dependencies.py
import joblib
import numpy as np
import json
import os
import tensorflow as tf
from tensorflow import keras
from functools import lru_cache

if os.path.exists("artifacts/model.keras"):
    model = tf.keras.models.load_model("artifacts/model.keras", compile=False)
elif os.path.exists("artifacts/model_fixed.h5"):
    from tensorflow.keras.utils import custom_object_scope
    from tensorflow.keras.mixed_precision import Policy
    with custom_object_scope({"DTypePolicy": Policy, "Policy": Policy}):
        model = tf.keras.models.load_model("artifacts/model_fixed.h5", compile=False)
else:
    from tensorflow.keras.utils import custom_object_scope
    from tensorflow.keras.mixed_precision import Policy
    with custom_object_scope({"DTypePolicy": Policy, "Policy": Policy}):
        model = tf.keras.models.load_model("artifacts/model.h5", compile=False)


class ModelLoader:
    def __init__(self):
        print("Loading model artifacts...")
        
        # Load pre-trained assets with error handling
        try:
            # Try loading with compile=False to avoid optimizer/version issues
            print("Attempting to load model...")
            self.model = keras.models.load_model("artifacts/model.h5", compile=False)
            print("Model loaded successfully!")
            
            # Manually compile the model
            self.model.compile(
                optimizer='adam',
                loss='mean_squared_error'
            )
            
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Attempting alternative loading method...")
            
            try:
                # Alternative loading method
                import h5py
                self.model = tf.keras.models.load_model(
                    "artifacts/model.h5", 
                    compile=False,
                    custom_objects={
                        'InputLayer': tf.keras.layers.InputLayer
                    }
                )
                self.model.compile(
                    optimizer='adam',
                    loss='mean_squared_error'
                )
                print("Model loaded with alternative method!")
                
            except Exception as e2:
                print(f"Alternative method also failed: {e2}")
                raise Exception(f"Could not load model. Try retraining with updated script. Original error: {e}")
        
        # Load other artifacts
        try:
            self.scaler = joblib.load("artifacts/scaler.pkl")
            print("Scaler loaded successfully!")
        except Exception as e:
            print(f"Error loading scaler: {e}")
            raise
            
        try:
            self.initial_window = np.load("artifacts/initial_window.npy")
            print("Initial window loaded successfully!")
        except Exception as e:
            print(f"Error loading initial window: {e}")
            raise
        
        # Load ticker information
        try:
            if os.path.exists("artifacts/tickers.json"):
                with open("artifacts/tickers.json") as f:
                    ticker_data = json.load(f)
                    self.all_tickers = ticker_data["all_tickers"]
                    self.close_cols = ticker_data["close_cols"]
                print(f"Loaded {len(self.all_tickers)} tickers: {self.all_tickers}")
            else:
                # Fallback: create a default ticker list
                print("Warning: tickers.json not found. Using default tickers.")
                self.all_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'JNJ', 'V']
                self.close_cols = [f"{ticker}_close" for ticker in self.all_tickers]
                
        except Exception as e:
            print(f"Error loading tickers: {e}")
            raise
    
    def get_stock_indices(self, selected_tickers):
        """Get indices for user-selected stocks"""
        indices = []
        for ticker in selected_tickers:
            col = f"{ticker}_close"
            if col in self.close_cols:
                indices.append(self.close_cols.index(col))
            else:
                print(f"Warning: {ticker} not found in available stocks: {self.all_tickers}")
        
        if not indices:
            raise ValueError(f"None of the selected stocks {selected_tickers} are available. Available stocks: {self.all_tickers}")
            
        return indices
    

@lru_cache(maxsize=1)
def get_model_loader() -> ModelLoader:
    return ModelLoader()