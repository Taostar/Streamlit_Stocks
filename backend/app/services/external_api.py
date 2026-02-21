import httpx
import pandas as pd
from typing import Optional
from app.config import get_settings
from app.core.cache import cached


settings = get_settings()


@cached(cache_type="holdings")
async def fetch_portfolio_data() -> tuple[Optional[list], Optional[dict]]:
    """
    Fetches portfolio data from the external API endpoint.

    Returns:
        Tuple of (portfolio_holdings, portfolio_metrics) or (None, None) on error
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.EXTERNAL_API_URL}/accounts/holdings",
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

            if "portfolio_holdings" not in data or "portfolio_metrics" not in data:
                return None, None

            return data["portfolio_holdings"], data["portfolio_metrics"]
    except httpx.HTTPError as e:
        print(f"Error fetching portfolio data: {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected error fetching portfolio data: {e}")
        return None, None


@cached(cache_type="performance")
async def load_performance() -> pd.DataFrame:
    """
    Fetches performance data from API and converts to pandas DataFrame.

    Returns:
        DataFrame with columns: symbol, date, open, high, low, close, volume
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.EXTERNAL_API_URL}/market/data",
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

            df = pd.DataFrame(data)

            # Explode the 'data' column to create a row for each item in the list
            df = df.explode("data")

            # Extract the symbol before normalizing
            symbols = df["symbol"].reset_index(drop=True)

            # Normalize the nested JSON in the 'data' column
            normalized_data = pd.json_normalize(df["data"])

            # Add the symbol column back to the normalized data
            result_df = pd.concat([symbols, normalized_data], axis=1)

            return result_df
    except httpx.HTTPError as e:
        print(f"Error fetching performance data: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Unexpected error loading performance data: {e}")
        return pd.DataFrame()


async def get_holdings_dataframe() -> pd.DataFrame:
    """Get holdings data as a DataFrame."""
    holdings, _ = await fetch_portfolio_data()
    if holdings is None:
        return pd.DataFrame()
    return pd.DataFrame(holdings)


async def get_portfolio_metrics() -> Optional[dict]:
    """Get portfolio metrics."""
    _, metrics = await fetch_portfolio_data()
    return metrics
