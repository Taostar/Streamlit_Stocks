import yfinance as yf
import pandas as pd
from typing import Optional
from app.core.cache import cached


CURRENCY_PAIRS = {
    "USD/CAD": "CAD=X",
    "CAD/CNY": "CADCNY=X",
    "USD/CNY": "CNY=X",
    "BTC/USD": "BTC-USD",
}


@cached(cache_type="exchange")
def load_exchange_rate_data(pair: str, period: str = "1y") -> Optional[dict]:
    """
    Load exchange rate data from Yahoo Finance API.

    Args:
        pair: Currency pair name (e.g., "USD/CAD")
        period: Time period for data retrieval (default: "1y")

    Returns:
        Dict with exchange rate data or None on error
    """
    try:
        ticker = CURRENCY_PAIRS.get(pair)
        if not ticker:
            return None

        data = yf.download(ticker, period=period, progress=False)

        if data.empty:
            return None

        # Extract Close prices - handle MultiIndex columns
        if isinstance(data.columns, pd.MultiIndex):
            close_cols = [col for col in data.columns if col[0] == "Close"]
            if close_cols:
                close_prices = data[close_cols[0]].values.tolist()
            else:
                return None
        else:
            if "Close" in data.columns:
                close_prices = data["Close"].values.tolist()
            else:
                return None

        dates = [d.strftime("%Y-%m-%d") for d in data.index]

        # Calculate metrics
        start_price = close_prices[0]
        current_price = close_prices[-1]

        # Calculate daily change
        if len(close_prices) >= 2:
            daily_change_pct = (
                (close_prices[-1] - close_prices[-2]) / close_prices[-2]
            ) * 100
        else:
            daily_change_pct = 0.0

        # Calculate YTD change
        ytd_change_pct = ((current_price - start_price) / start_price) * 100

        return {
            "pair": pair,
            "dates": dates,
            "close_prices": close_prices,
            "current_rate": current_price,
            "daily_change_pct": daily_change_pct,
            "ytd_change_pct": ytd_change_pct,
        }

    except Exception as e:
        print(f"Error loading exchange rate data: {e}")
        return None


def get_available_pairs() -> list[str]:
    """Return list of available currency pairs."""
    return list(CURRENCY_PAIRS.keys())
