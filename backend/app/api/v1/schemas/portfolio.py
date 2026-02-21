from pydantic import BaseModel
from typing import Optional


class PortfolioOverview(BaseModel):
    total_value_cad: float
    cumulative_return: float
    avg_daily_return: float
    sharpe_ratio: float
    weighted_correlation: Optional[float] = None
    prev_day_change: Optional[float] = None


class AllocationItem(BaseModel):
    symbol: str
    market_value_cad: float
    percentage: float
    currency: str
    current_price: float


class AllocationResponse(BaseModel):
    items: list[AllocationItem]
    total_value_cad: float
