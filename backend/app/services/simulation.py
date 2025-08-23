import numpy as np

class MonteCarloSimulator:
    def __init__(self, model_loader):
        self.model_loader = model_loader
    
    def simulate_path(self, n_days=30, noise_std=0.01):
        """Generate single price path"""
        window = self.model_loader.initial_window.copy()
        path = []
        
        for _ in range(n_days):
            # Predict next day
            pred = self.model_loader.model.predict(window[np.newaxis, :, :])[0]
            # Add randomness
            pred += np.random.normal(0, noise_std, size=pred.shape)
            path.append(pred)
            # Update window
            window = np.vstack([window[1:], pred])
        
        # Convert to actual prices
        return self.model_loader.scaler.inverse_transform(np.array(path))
    
    def run_simulations(self, n_simulations=1, n_days=60):
        """Run multiple simulations"""
        return [self.simulate_path(n_days) for _ in range(n_simulations)]