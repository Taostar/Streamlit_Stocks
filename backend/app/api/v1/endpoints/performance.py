from fastapi import APIRouter, HTTPException
from app.api.v1.schemas.common import CandlestickData
from app.services.external_api import load_performance

router = APIRouter(prefix="/performance", tags=["performance"])


@router.get("/symbols", response_model=list[str])
async def get_available_symbols():
    """Get list of available symbols."""
    performance_df = await load_performance()

    if performance_df.empty:
        raise HTTPException(status_code=503, detail="Unable to fetch performance data")

    return sorted(performance_df["symbol"].unique().tolist())


@router.get("/{symbol}", response_model=CandlestickData)
async def get_symbol_performance(symbol: str):
    """
    Get OHLCV data for a specific symbol (for candlestick chart).

    Args:
        symbol: Stock/ETF symbol
    """
    performance_df = await load_performance()

    if performance_df.empty:
        raise HTTPException(status_code=503, detail="Unable to fetch performance data")

    # Filter for the requested symbol
    symbol_data = performance_df[performance_df["symbol"] == symbol].copy()

    if symbol_data.empty:
        raise HTTPException(
            status_code=404, detail=f"No performance data found for symbol: {symbol}"
        )

    # Sort by date
    symbol_data["date"] = symbol_data["date"].astype(str)
    symbol_data = symbol_data.sort_values("date")

    return CandlestickData(
        symbol=symbol,
        dates=symbol_data["date"].tolist(),
        open=symbol_data["open"].tolist(),
        high=symbol_data["high"].tolist(),
        low=symbol_data["low"].tolist(),
        close=symbol_data["close"].tolist(),
        volume=symbol_data["volume"].astype(int).tolist(),
    )
