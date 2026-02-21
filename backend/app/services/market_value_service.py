import pandas as pd
from typing import Optional
from app.core.cache import cached


@cached(cache_type="performance")
def calculate_market_value_changes(
    holdings_df: pd.DataFrame, performance_df: pd.DataFrame
) -> tuple[pd.DataFrame, Optional[float]]:
    """
    Calculate market value changes for different time periods.

    Args:
        holdings_df: DataFrame with portfolio holdings
        performance_df: DataFrame with historical price data

    Returns:
        Tuple of (updated holdings_df with change columns, prev_day_change_percentage)
    """
    try:
        if holdings_df.empty or performance_df.empty:
            return holdings_df.copy(), None

        result_df = holdings_df.copy()
        performance_df = performance_df.copy()
        performance_df["date"] = pd.to_datetime(performance_df["date"])

        latest_date = performance_df["date"].max()

        # Calculate target dates for different time periods
        prev_day_target = latest_date - pd.Timedelta(days=1)
        week_target = latest_date - pd.Timedelta(days=7)
        month_target = latest_date - pd.Timedelta(days=30)
        six_month_target = latest_date - pd.Timedelta(days=180)
        year_target = latest_date - pd.Timedelta(days=360)

        prev_day_market_value_cad = 0.0
        current_day_market_value_cad = 0.0

        # Get CAD exchange rate
        cad_exchange_sample = result_df[result_df["currency"] == "USD"].head(1)
        if not cad_exchange_sample.empty:
            cad_exchange_rate = float(
                cad_exchange_sample["current_market_value_CAD"].iloc[0]
                / cad_exchange_sample["current_market_value"].iloc[0]
            )
        else:
            cad_exchange_rate = 1.0

        for idx, row in result_df.iterrows():
            symbol = row["symbol"]
            quantity = float(row["quantity"])
            currency = row["currency"]
            current_price = float(row["current_price"])
            current_market_value_local = float(row["current_market_value"])
            current_market_value_cad = float(row["current_market_value_CAD"])

            current_day_market_value_cad += current_market_value_cad

            symbol_perf = performance_df[performance_df["symbol"] == symbol].sort_values(
                "date", ascending=False
            )

            if symbol_perf.empty:
                result_df.at[idx, "change_1d"] = None
                result_df.at[idx, "change_1w"] = None
                result_df.at[idx, "change_1m"] = None
                result_df.at[idx, "change_6m"] = None
                result_df.at[idx, "change_1y"] = None
                continue

            current_day_data = symbol_perf[symbol_perf["date"] == latest_date]
            if current_day_data.empty and len(symbol_perf) > 0:
                current_day_data = symbol_perf.iloc[0:1]

            def find_closest_date(target_date):
                valid_dates = symbol_perf[symbol_perf["date"] <= target_date]
                if not valid_dates.empty:
                    return valid_dates.iloc[0]
                return None

            prev_day_data = find_closest_date(prev_day_target)
            week_ago_data = find_closest_date(week_target)
            month_ago_data = find_closest_date(month_target)
            six_month_ago_data = find_closest_date(six_month_target)
            year_ago_data = find_closest_date(year_target)

            # Calculate 1-day change
            if prev_day_data is not None:
                if current_price != current_day_data["close"].item():
                    prev_price = float(current_day_data["close"].item())
                else:
                    prev_price = float(prev_day_data["close"])
                prev_market_value = prev_price * quantity
                if currency == "USD":
                    prev_market_value_cad = prev_market_value * cad_exchange_rate
                else:
                    prev_market_value_cad = prev_market_value
                change_1d = (
                    (current_market_value_local - prev_market_value) / prev_market_value
                    if prev_market_value > 0
                    else 0
                )
                result_df.at[idx, "change_1d"] = change_1d
                prev_day_market_value_cad += prev_market_value_cad
            else:
                result_df.at[idx, "change_1d"] = None

            # Calculate 1-week change
            if week_ago_data is not None:
                week_price = float(week_ago_data["close"])
                week_market_value = week_price * quantity
                change_1w = (
                    (current_market_value_local - week_market_value) / week_market_value
                    if week_market_value > 0
                    else 0
                )
                result_df.at[idx, "change_1w"] = change_1w
            else:
                result_df.at[idx, "change_1w"] = None

            # Calculate 1-month change
            if month_ago_data is not None:
                month_price = float(month_ago_data["close"])
                month_market_value = month_price * quantity
                change_1m = (
                    (current_market_value_local - month_market_value) / month_market_value
                    if month_market_value > 0
                    else 0
                )
                result_df.at[idx, "change_1m"] = change_1m
            else:
                result_df.at[idx, "change_1m"] = None

            # Calculate 6-month change
            if six_month_ago_data is not None:
                six_month_price = float(six_month_ago_data["close"])
                six_month_market_value = six_month_price * quantity
                change_6m = (
                    (current_market_value_local - six_month_market_value)
                    / six_month_market_value
                    if six_month_market_value > 0
                    else 0
                )
                result_df.at[idx, "change_6m"] = change_6m
            else:
                result_df.at[idx, "change_6m"] = None

            # Calculate 1-year change
            if year_ago_data is not None:
                year_price = float(year_ago_data["close"])
                year_market_value = year_price * quantity
                change_1y = (
                    (current_market_value_local - year_market_value) / year_market_value
                    if year_market_value > 0
                    else 0
                )
                result_df.at[idx, "change_1y"] = change_1y
            else:
                result_df.at[idx, "change_1y"] = None

        # Calculate portfolio-level change percentage
        portfolio_prev_day_change = (
            (current_day_market_value_cad - prev_day_market_value_cad)
            / prev_day_market_value_cad
            if prev_day_market_value_cad > 0
            else 0
        )

        return result_df, portfolio_prev_day_change

    except Exception as e:
        print(f"Error calculating market value changes: {e}")
        return holdings_df.copy(), None
