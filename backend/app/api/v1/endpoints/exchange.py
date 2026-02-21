from fastapi import APIRouter, HTTPException
from app.api.v1.schemas.common import ExchangeRateData
from app.services.exchange_service import load_exchange_rate_data, get_available_pairs

router = APIRouter(prefix="/exchange-rates", tags=["exchange-rates"])


@router.get("", response_model=list[str])
async def get_available_currency_pairs():
    """Get list of available currency pairs."""
    return get_available_pairs()


@router.get("/{pair}", response_model=ExchangeRateData)
async def get_exchange_rate(pair: str):
    """
    Get exchange rate data for a currency pair.

    Args:
        pair: Currency pair name (e.g., "USD/CAD", "CAD/CNY", "USD/CNY", "BTC/USD")
    """
    available_pairs = get_available_pairs()
    if pair not in available_pairs:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid currency pair. Available pairs: {available_pairs}",
        )

    data = load_exchange_rate_data(pair)

    if data is None:
        raise HTTPException(
            status_code=503, detail=f"Unable to fetch exchange rate data for {pair}"
        )

    return ExchangeRateData(
        pair=data["pair"],
        dates=data["dates"],
        close_prices=data["close_prices"],
        current_rate=data["current_rate"],
        daily_change_pct=data["daily_change_pct"],
        ytd_change_pct=data["ytd_change_pct"],
    )
