import pandas as pd
from typing import Optional
from app.core.cache import cached


@cached(cache_type="correlation")
def calculate_portfolio_correlation(
    holdings_df: pd.DataFrame, performance_df: pd.DataFrame
) -> tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[float]]:
    """
    Calculate the weighted correlation matrix for stocks in the portfolio.

    Args:
        holdings_df: DataFrame with portfolio holdings including percentage weights
        performance_df: DataFrame with historical price data

    Returns:
        Tuple of (correlation_matrix, weighted_correlation_matrix, portfolio_weighted_correlation)
    """
    try:
        if performance_df.empty or holdings_df.empty:
            return None, None, None

        performance_df = performance_df.copy()
        performance_df["date"] = pd.to_datetime(performance_df["date"])

        # Filter performance data for the last year
        current_date = performance_df["date"].max()
        one_year_ago = current_date - pd.DateOffset(years=1)
        yearly_perf_df = performance_df[performance_df["date"] >= one_year_ago]

        # Get portfolio symbols from holdings
        portfolio_symbols = holdings_df["symbol"].unique().tolist()

        # Filter for symbols in both the holdings and performance data
        valid_symbols = [
            symbol
            for symbol in portfolio_symbols
            if symbol in yearly_perf_df["symbol"].values
        ]

        if len(valid_symbols) < 2:
            return None, None, None

        # Create a price DataFrame with dates as index and symbols as columns
        price_data = {}
        common_dates = None

        for symbol in valid_symbols:
            symbol_data = yearly_perf_df[yearly_perf_df["symbol"] == symbol]
            price_series = symbol_data.set_index("date")["close"]
            price_data[symbol] = price_series

            if common_dates is None:
                common_dates = set(price_series.index)
            else:
                common_dates = common_dates.intersection(set(price_series.index))

        # Only use dates common to all symbols
        common_dates = sorted(list(common_dates))
        if len(common_dates) < 30:
            return None, None, None

        # Create the price DataFrame
        price_df = pd.DataFrame(index=common_dates)
        for symbol in valid_symbols:
            price_df[symbol] = price_data[symbol].reindex(common_dates)

        # Calculate daily returns (percentage change)
        returns_df = price_df.pct_change().dropna()

        # Calculate the correlation matrix
        correlation_matrix = returns_df.corr()

        # Get weights for each symbol
        weights = {}
        total_weight = 0
        for symbol in valid_symbols:
            symbol_row = holdings_df[holdings_df["symbol"] == symbol].iloc[0]
            weight = (
                float(symbol_row["percentage"])
                if isinstance(symbol_row["percentage"], str)
                else float(symbol_row.get("percentage", 0))
            )
            weights[symbol] = weight / 100
            total_weight += weight / 100

        # Normalize weights to sum to 1.0
        if total_weight > 0:
            for symbol in weights:
                weights[symbol] /= total_weight

        # Calculate the weighted correlation matrix
        weighted_corr_matrix = pd.DataFrame(0.0, index=valid_symbols, columns=valid_symbols)
        for i in valid_symbols:
            for j in valid_symbols:
                weighted_corr_matrix.at[i, j] = (
                    correlation_matrix.at[i, j] * weights[i] * weights[j]
                )

        # Calculate portfolio weighted correlation
        portfolio_weighted_corr = weighted_corr_matrix.values.sum()

        return correlation_matrix, weighted_corr_matrix, portfolio_weighted_corr

    except Exception as e:
        print(f"Error calculating portfolio correlation: {e}")
        return None, None, None


def correlation_matrix_to_json(
    corr_matrix: pd.DataFrame,
) -> dict:
    """
    Convert correlation matrix to JSON-serializable format with lower triangle masked.

    Args:
        corr_matrix: Pandas DataFrame correlation matrix

    Returns:
        Dict with symbols and masked values (upper triangle set to None)
    """
    symbols = corr_matrix.columns.tolist()
    values = []

    for i, row_symbol in enumerate(symbols):
        row = []
        for j, col_symbol in enumerate(symbols):
            if j > i:
                # Upper triangle - mask with None
                row.append(None)
            else:
                row.append(round(corr_matrix.at[row_symbol, col_symbol], 4))
        values.append(row)

    return {"symbols": symbols, "values": values}
