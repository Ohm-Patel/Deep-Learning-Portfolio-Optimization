# backend/app/routes/portfolio.py
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, List, Optional

from app.dependencies import ModelLoader
from app.services.simulation import MonteCarloSimulator
from app.services.optimizer import PortfolioOptimizer
from app.utils.serialization import to_py

from fastapi import APIRouter, Depends
from app.dependencies import get_model_loader, ModelLoader
from app.services.simulation import MonteCarloSimulator
from app.services.optimizer import PortfolioOptimizer

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

class OptimizeRequest(BaseModel):
    selected_stocks: List[str]
    total_capital: float
    custom_weights: Optional[List[float]] = None

class OptimizeResponse(BaseModel):
    allocations: Dict[str, float]
    expected_return: float
    expected_volatility: float
    sharpe: float
    frontier: List[List[float]]
    growth_data: Dict[str, List[float]]

@router.post("/optimize", response_model=OptimizeResponse)
def optimize(req: OptimizeRequest, loader: ModelLoader = Depends(get_model_loader)):
    sim = MonteCarloSimulator(loader)
    opt = PortfolioOptimizer(loader, sim)
    raw = opt.optimize(
        tickers=req.selected_stocks, 
        total_capital=req.total_capital,
        custom_weights=req.custom_weights
    )
    clean = to_py(raw)
    return OptimizeResponse(**clean)