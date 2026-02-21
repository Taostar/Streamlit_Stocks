from pydantic import BaseModel
from typing import Optional


class CorrelationMatrix(BaseModel):
    symbols: list[str]
    values: list[list[Optional[float]]]  # 2D matrix, None for masked values
    weighted_correlation: float


class ExchangeRateData(BaseModel):
    pair: str
    dates: list[str]
    close_prices: list[float]
    current_rate: float
    daily_change_pct: float
    ytd_change_pct: float


class BenchmarkData(BaseModel):
    dates: list[str]
    portfolio: list[float]
    qqq: list[float]
    voo: list[float]


class CandlestickData(BaseModel):
    symbol: str
    dates: list[str]
    open: list[float]
    high: list[float]
    low: list[float]
    close: list[float]
    volume: list[int]


class HealthResponse(BaseModel):
    status: str = "ok"
