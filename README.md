# Portfolio Optimizer

LSTM-powered portfolio optimization with Monte Carlo simulations for the **Dow 30**.

Pick stocks, optionally set custom weights, and get:
- Expected **60‑day growth** curve
- **Capital allocation** by ticker
- Summary stats: expected return, volatility, and Sharpe

> UI details: responsive layout for desktop → mobile, pie **stroke matches card border** (`#374151`), and pie tooltip is formatted like  
> `stock_name: percent_allocated% ($capital_allocated)`.

---

## ✨ Features

- Select from Dow‑30 tickers (no duplicates)
- Optional custom weights (validated to sum to **1.0**)
- LSTM (60‑day lookback with RobustScaler) → Monte Carlo path simulation
- Auto‑optimize weights for Sharpe, or respect user-provided weights
- Charts
  - **Growth** (line chart, 60 days)
  - **Capital Allocation** (pie with themed border + formatted tooltip)
- Clean dark UI, keyboard-friendly inputs, and clear error messages

---

## 🧱 Tech Stack

**Frontend**
- React (Vite)
- Recharts (LineChart, PieChart)
- lucide-react icons

**Backend**
- FastAPI (Python)
- NumPy / Pandas / SciPy
- scikit-learn (RobustScaler)
- TensorFlow/Keras (LSTM)

---

## 🚀 Quickstart

> **Prerequisites**: Node 18+, Python 3.10+, `pip`, and `venv`

### 1) Clone
```bash
git clone <your-repo-url> portfolio-optimizer
cd portfolio-optimizer
```

### 2) Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- Place your trained model weights under `backend/models/weights/*.h5` (or your chosen path).
- Ensure CORS allows your frontend origin (localhost:5173 by default for Vite).

### 3) Frontend
```bash
cd ../frontend
npm install
# Optional: set API base via env
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
npm run dev
```

Open the printed localhost URL (Vite defaults to `http://localhost:5173`).

> Ensure your `index.html` includes:
```html
<meta name="viewport" content="width=device-width, initial-scale=1" />
```

---

## 🔌 API

### `POST /api/portfolio/optimize`

**Request body**
```json
{
  "selected_stocks": ["AAPL", "MSFT", "NVDA"],
  "total_capital": 10000,
  "custom_weights": [0.34, 0.33, 0.33]   // optional; omit for auto-optimization
}
```

**Response**
```json
{
  "allocations": { "AAPL": 0.34, "MSFT": 0.33, "NVDA": 0.33 },
  "expected_return": 0.12,
  "expected_volatility": 0.18,
  "sharpe": 0.67,
  "growth_data": {
    "optimized": [0.0, 0.15, 0.22, ...],
    "custom":    [0.0, 0.11, 0.18, ...]
  }
}
```

**cURL**
```bash
curl -X POST http://localhost:8000/api/portfolio/optimize \
  -H "Content-Type: application/json" \
  -d '{"selected_stocks":["AAPL","MSFT","NVDA"],"total_capital":10000}'
```

---

## ⚙️ Configuration

- **Frontend API base**: `VITE_API_BASE_URL` (defaults to `http://localhost:8000` if hardcoded in the component).
- **Model/scaler**: Persist and load the scaler that matches your training pipeline. Feature order, lookback window, and preprocessing must match at inference.

---

## 📁 Suggested Repo Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/portfolio.py
│   │   ├── services/optimizer.py
│   │   └── models/
│   │       ├── loader.py
│   │       └── weights/*.h5
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/PortfolioOptimizer.jsx
│   │   └── main.jsx
│   ├── index.html
│   └── package.json
└── README.md
```

---

## 🧪 Testing

- **Backend**: unit tests for optimizer (deterministic seeds for Monte Carlo), API contract tests using FastAPI `TestClient`.
- **Frontend**: input validation tests + DOM/snapshot tests for charts and summaries.
- **Weights**: verify that custom weights either sum to 1.0 or are omitted for auto-optimization.

---

## 🛣️ Roadmap

- Constraints: per-asset caps, sector caps, min positions
- Save/load portfolios; export allocations (CSV/JSON)
- Multi-objective optimization (drawdown-aware)
- Training pipeline scripts + model registry
- CI (lint, type-check, tests) and Dockerization

---

## 📸 Screenshots

Add a screenshot under `docs/screenshot.png` and reference it here:

![App screenshot](docs/screenshot.png)

---

## 📝 License

MIT — see `LICENSE` for details.

---

## 🙌 Acknowledgments

- Recharts for charts
- FastAPI for a clean Python web API
- scikit-learn & TensorFlow for the modeling stack
