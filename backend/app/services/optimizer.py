# backend/app/services/optimizer.py
import numpy as np
from scipy.optimize import minimize

class PortfolioOptimizer:
    def __init__(self, model_loader, simulator):
        self.model_loader = model_loader
        self.simulator = simulator

    def evaluate_portfolio(self, prices, weights, stock_indices):
        """Return Sharpe for one simulated price path."""
        selected = prices[:, stock_indices]                   # (T, k)
        port_values = np.dot(selected, weights)               # (T,)
        rets = np.diff(port_values) / port_values[:-1]        # (T-1,)
        return float(np.mean(rets) / (np.std(rets) + 1e-8))

    def path_total_return(self, prices, weights, stock_indices):
        selected = prices[:, stock_indices]
        port_values = np.dot(selected, weights)
        return float(port_values[-1] / port_values[0] - 1.0)

    def optimize_weights(self, simulated_paths, stock_indices):
        """Find weights that maximize Sharpe ratio."""
        n = len(stock_indices)

        def objective(weights):
            return -np.mean([
                self.evaluate_portfolio(path, weights, stock_indices)
                for path in simulated_paths
            ])

        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = [(0, 1) for _ in range(n)]
        init_w = np.ones(n) / n

        res = minimize(objective, init_w, bounds=bounds, constraints=constraints)
        return res.x

    def optimize(self, *, tickers=None, total_capital=None, simulated_paths=None, stock_indices=None, n_paths: int = 6, horizon: int = 75, custom_weights=None):
        """Wrapper so routes can call with tickers/total_capital."""
        # Resolve indices
        if stock_indices is None:
            if not tickers:
                raise ValueError("Either `stock_indices` or `tickers` must be provided.")
            if hasattr(self.model_loader, "get_stock_indices"):
                stock_indices = self.model_loader.get_stock_indices(tickers)
            else:
                # fallback: map from all_tickers list
                idx_map = {t: i for i, t in enumerate(self.model_loader.asll_tickers)}
                try:
                    stock_indices = [idx_map[t] for t in tickers]
                except KeyError as e:
                    raise ValueError(f"Unknown ticker in request: {e.args[0]}")

        # Get simulations
        if simulated_paths is None:
            sim = self.simulator
            if hasattr(sim, "simulate_paths"):
                simulated_paths = sim.simulate_paths(
                    stock_indices=stock_indices,
                    n_paths=n_paths,
                    horizon=horizon,
                    total_capital=total_capital,
                )
            elif hasattr(sim, "run_simulations"):
                simulated_paths = sim.run_simulations(n_paths, horizon)
            elif hasattr(sim, "run"):
                simulated_paths = sim.run(
                    stock_indices=stock_indices,
                    n_paths=n_paths,
                    horizon=horizon,
                    total_capital=total_capital,
                )
            else:
                raise RuntimeError("Simulator must implement simulate_paths/run_simulations/run.")

        # Optimize weights
        weights = self.optimize_weights(simulated_paths, stock_indices)

        # Metrics
        per_path_sharpe = np.array([
            self.evaluate_portfolio(path, weights, stock_indices)
            for path in simulated_paths
        ])
        per_path_total_ret = np.array([
            self.path_total_return(path, weights, stock_indices)
            for path in simulated_paths
        ])

        sharpe = float(np.mean(per_path_sharpe))
        expected_return = float(np.mean(per_path_total_ret))
        expected_volatility = float(np.std(per_path_total_ret, ddof=1)) if len(per_path_total_ret) > 1 else 0.0

        # Map weights back to tickers the user asked for
        if tickers is None:
            tickers = [self.model_loader.all_tickers[i] for i in stock_indices]
        allocations = {t: float(w) for t, w in zip(tickers, weights)}

        frontier = []  # keep empty unless you compute it

        # Compute growth data for visualization
        growth_data = {}
        initial_capital = total_capital if total_capital else 10000  # default capital
        
        print(f"DEBUG: Computing growth data with initial_capital={initial_capital}")
        print(f"DEBUG: simulated_paths shape: {len(simulated_paths)} paths")
        print(f"DEBUG: stock_indices: {stock_indices}")
        print(f"DEBUG: weights: {weights}")
        
        # Always include optimized portfolio growth (as percentage)
        optimized_growth = self.compute_growth(
            simulated_paths, stock_indices, weights, initial_capital
        )
        # Convert to percentage growth from initial value
        optimized_pct_growth = ((optimized_growth / optimized_growth[0]) - 1) * 100
        growth_data["optimized"] = optimized_pct_growth.tolist()
        print(f"DEBUG: optimized_growth length: {len(optimized_growth)}")
        
        # Include custom weight portfolio if provided
        if custom_weights is not None:
            if len(custom_weights) != len(stock_indices):
                raise ValueError(f"Custom weights length ({len(custom_weights)}) must match number of stocks ({len(stock_indices)})")
            
            # Normalize custom weights to sum to 1
            custom_weights_array = np.array(custom_weights)
            if np.sum(custom_weights_array) == 0:
                raise ValueError("Custom weights cannot all be zero")
            
            normalized_custom_weights = custom_weights_array / np.sum(custom_weights_array)
            
            custom_growth = self.compute_growth(
                simulated_paths, stock_indices, normalized_custom_weights, initial_capital
            )
            # Convert to percentage growth from initial value
            custom_pct_growth = ((custom_growth / custom_growth[0]) - 1) * 100
            growth_data["custom"] = custom_pct_growth.tolist()
            print(f"DEBUG: custom_growth length: {len(custom_growth)}")
        
        print(f"DEBUG: growth_data keys: {growth_data.keys()}")

        result = {
            "allocations": allocations,
            "expected_return": expected_return,
            "expected_volatility": expected_volatility,
            "sharpe": sharpe,
            "frontier": frontier,
            "growth_data": growth_data,
        }
        
        print(f"DEBUG: Final result keys: {result.keys()}")
        print(f"DEBUG: growth_data in result: {'growth_data' in result}")
        print(f"DEBUG: growth_data sample: {list(result['growth_data']['optimized'])[:5]}...")
        
        return result

    def compute_growth(self, paths, stock_indices, weights, initial_capital):
        """Calculate portfolio value over time."""
        portfolio_values = []
        for path in paths:
            selected = path[:, stock_indices]
            values = np.dot(selected, weights)
            scaled = initial_capital * (values / values[0])
            portfolio_values.append(scaled)
        """path = paths[0]  # or np.random.choice(len(paths))
        selected = path[:, stock_indices]
        values = np.dot(selected, weights)
        scaled = initial_capital * (values / values[0])
        return scaled"""
        return np.mean(portfolio_values, axis=0)

    def generate_report(self, selected_tickers, total_capital, custom_weights=None):
        """Legacy report flow (still works)."""
        stock_indices = self.model_loader.get_stock_indices(selected_tickers)
        simulated_paths = self.simulator.run_simulations(500, 60)
        optimal_weights = self.optimize_weights(simulated_paths, stock_indices)

        allocations = {
            t: float(w) * float(total_capital)
            for t, w in zip(selected_tickers, optimal_weights)
        }

        growth_data = {
            "optimized": self.compute_growth(simulated_paths, stock_indices, optimal_weights, total_capital),
            "equal": self.compute_growth(simulated_paths, stock_indices, np.ones(len(stock_indices))/len(stock_indices), total_capital),
        }
        if custom_weights:
            growth_data["custom"] = self.compute_growth(simulated_paths, stock_indices, np.array(custom_weights), total_capital)

        return {
            "optimal_weights": dict(zip(selected_tickers, map(float, optimal_weights))),
            "capital_allocations": allocations,
            "growth_data": growth_data,
        }