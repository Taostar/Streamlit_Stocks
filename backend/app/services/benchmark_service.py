import pandas as pd
from typing import Optional
from app.core.cache import cached


@cached(cache_type="benchmark")
def calculate_normalized_benchmark_data(
    performance_df: pd.DataFrame, portfolio_metrics: dict
) -> Optional[dict]:
    """
    Calculate normalized benchmark comparison data (Portfolio vs QQQ vs VOO).

    Args:
        performance_df: DataFrame with historical price data
        portfolio_metrics: Dict with portfolio metrics including Symbols and Allocations

    Returns:
        Dict with normalized benchmark data or None on error
    """
    try:
        if performance_df.empty or not portfolio_metrics:
            return None

        df = performance_df.copy()
        df = df.sort_values(by=["symbol", "date"]).reset_index(drop=True)
        df["date"] = pd.to_datetime(df["date"])

        # Pivot the DataFrame
        prices_df = df.pivot(index="date", columns="symbol", values="close")
        prices_df = prices_df.ffill().bfill()

        # Get symbol allocations
        symbols_allocs = dict(
            zip(portfolio_metrics["Symbols"], portfolio_metrics["Allocations"])
        )
        symbols_allocs = {k: float(v.strip("%")) for k, v in symbols_allocs.items()}

        # Get sorted symbols present in both prices and allocations
        available_symbols = [s for s in prices_df.columns if s in symbols_allocs]
        sorted_portfolio = {symbol: symbols_allocs[symbol] for symbol in available_symbols}
        allocations = [float(alloc) for alloc in sorted_portfolio.values()]

        # Calculate normalized allocated positions
        portfolio_symbols_df = prices_df[available_symbols]
        normalized_allocs_positions = (
            portfolio_symbols_df / portfolio_symbols_df.iloc[0] * allocations
        )
        normalized_allocs_positions = normalized_allocs_positions.sum(axis=1)

        # Get benchmark data (QQQ and VOO)
        benchmark_columns = []
        for benchmark in ["QQQ", "VOO"]:
            if benchmark in prices_df.columns:
                benchmark_columns.append(benchmark)

        if not benchmark_columns:
            return None

        normalized_benchmark_data = prices_df[benchmark_columns].copy()
        normalized_benchmark_data = (
            normalized_benchmark_data / normalized_benchmark_data.iloc[0] * 100
        )
        normalized_benchmark_data["Portfolio"] = normalized_allocs_positions

        # Convert to JSON-serializable format
        dates = [d.strftime("%Y-%m-%d") for d in normalized_benchmark_data.index]

        return {
            "dates": dates,
            "portfolio": normalized_benchmark_data["Portfolio"].tolist(),
            "qqq": normalized_benchmark_data.get("QQQ", pd.Series([0])).tolist(),
            "voo": normalized_benchmark_data.get("VOO", pd.Series([0])).tolist(),
        }

    except Exception as e:
        print(f"Error calculating normalized benchmark data: {e}")
        return None
