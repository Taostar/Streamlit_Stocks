from pydantic import BaseModel
from typing import Optional


class HoldingItem(BaseModel):
    symbol: str
    currency: str
    quantity: int
    current_price: float
    market_value: float
    market_value_cad: float
    portfolio_pct: float
    change_1d: Optional[float] = None
    change_1w: Optional[float] = None
    change_1m: Optional[float] = None
    change_6m: Optional[float] = None
    change_1y: Optional[float] = None


class HoldingsResponse(BaseModel):
    holdings: list[HoldingItem]
    prev_day_change_pct: Optional[float] = None
