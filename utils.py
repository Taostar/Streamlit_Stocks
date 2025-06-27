import requests
import pandas as pd
import streamlit as st
import json
import os
import re
from datetime import datetime

# --- Configuration Loading ---
def load_config():
    """Loads configuration from config.json."""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Configuration file (config.json) not found. Please create it.")
        return {}
    except json.JSONDecodeError:
        st.error("Error decoding config.json. Please check its format.")
        return {}

config = load_config()
API_URL = config.get("API_URL")
PERFORMANCE_DATA_FOLDER = config.get("PERFORMANCE_DATA_FOLDER")

@st.cache_data(ttl=300) # Cache data for 5 minutes
def fetch_portfolio_data():
    """Fetches portfolio data from the Questrade API endpoint."""
    try:
        if not API_URL:
            st.error("API_URL is not configured in config.json.")
            return None, None
        response = requests.get(f"{API_URL}/accounts/holdings")
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        data = response.json()
        # Basic validation of the expected structure
        if "portfolio_holdings" not in data or "portfolio_metrics" not in data:
            st.error("Portfolio data from API is not in the expected format.")
            return None, None
        return data["portfolio_holdings"], data["portfolio_metrics"]
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching portfolio data from API: {e}")
        return None, None
    except json.JSONDecodeError:
        st.error("Error decoding JSON response from API.")
        return None, None


@st.cache_data(ttl=3600) # Cache data for 6 hours
def load_performance():
    """Fetches performance data from API and converts to pandas DataFrame."""
    try:
        if not API_URL:
            st.error("API_URL is not configured in config.json.")
            return pd.DataFrame(), None
        
        response = requests.get(f"{API_URL}/market/data")
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        
        # Convert the JSON response to a pandas DataFrame
        data = response.json()
        df = pd.DataFrame(data)
        
        # Explode the 'data' column to create a row for each item in the list
        df = df.explode('data')
        
        # Extract the symbol before normalizing
        symbols = df['symbol'].reset_index(drop=True)
        
        # Normalize the nested JSON in the 'data' column
        normalized_data = pd.json_normalize(df['data'])
        
        # Add the symbol column back to the normalized data
        result_df = pd.concat([symbols, normalized_data], axis=1)

        return result_df  # Return DataFrame and None instead of file path
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching performance data from API: {e}")
        return pd.DataFrame()
    except json.JSONDecodeError:
        st.error("Error decoding JSON response from API.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Unexpected error loading performance data: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def calculate_portfolio_correlation(holdings_df, performance_df):
    """
    Calculate the weighted correlation matrix for stocks in the portfolio.
    
    Args:
        holdings_df (pandas.DataFrame): DataFrame with portfolio holdings including percentage weights
        performance_df (pandas.DataFrame): DataFrame with historical price data
    
    Returns:
        tuple: (correlation_matrix, weighted_correlation_matrix, portfolio_weighted_correlation)
    """
    try:
        if performance_df.empty or holdings_df.empty:
            # st.warning("Empty performance or holdings data. Cannot calculate portfolio correlation.")
            return None, None, None

        # Ensure date column is in datetime format
        performance_df['date'] = pd.to_datetime(performance_df['date'])
        
        # Filter performance data for the last year
        current_date = performance_df['date'].max()
        one_year_ago = current_date - pd.DateOffset(years=1)
        yearly_perf_df = performance_df[performance_df['date'] >= one_year_ago]
        
        # Get portfolio symbols from holdings
        portfolio_symbols = holdings_df['symbol'].unique().tolist()
        
        # Filter for symbols in both the holdings and performance data
        valid_symbols = [symbol for symbol in portfolio_symbols if symbol in yearly_perf_df['symbol'].values]
        
        if len(valid_symbols) < 2:
            # st.warning("Need at least 2 valid symbols with performance data to calculate correlations.")
            return None, None, None
            
        # Create a price DataFrame with dates as index and symbols as columns
        price_data = {}
        common_dates = None
        
        for symbol in valid_symbols:
            symbol_data = yearly_perf_df[yearly_perf_df['symbol'] == symbol]
            price_series = symbol_data.set_index('date')['close']
            price_data[symbol] = price_series
            
            if common_dates is None:
                common_dates = set(price_series.index)
            else:
                common_dates = common_dates.intersection(set(price_series.index))
        
        # Only use dates common to all symbols
        common_dates = sorted(list(common_dates))
        if len(common_dates) < 30:  # Require at least 30 days of common data
            # st.warning(f"Insufficient common price data across all symbols (only {len(common_dates)} days).")
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
            symbol_row = holdings_df[holdings_df['symbol'] == symbol].iloc[0]
            weight = float(symbol_row['percentage']) if isinstance(symbol_row['percentage'], str) else float(symbol_row.get('percentage', 0))
            weights[symbol] = weight / 100  # Convert from percentage to decimal
            total_weight += weight / 100
        
        # Normalize weights to sum to 1.0 (in case some symbols were excluded)
        if total_weight > 0:
            for symbol in weights:
                weights[symbol] /= total_weight
        
        # Calculate the weighted correlation matrix
        weighted_corr_matrix = pd.DataFrame(0.0, index=valid_symbols, columns=valid_symbols)
        for i in valid_symbols:
            for j in valid_symbols:
                weighted_corr_matrix.at[i, j] = correlation_matrix.at[i, j] * weights[i] * weights[j]
        
        # Calculate portfolio weighted correlation (sum all weighted correlations)
        portfolio_weighted_corr = weighted_corr_matrix.values.sum()
        
        return correlation_matrix, weighted_corr_matrix, portfolio_weighted_corr
        
    except Exception as e:
        st.error(f"Error calculating portfolio correlation: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None, None, None

@st.cache_data(ttl=3600)
def calculate_market_value_changes(holdings_df, performance_df):
    """
    Calculate market value changes for different time periods and add them as columns to holdings_df.
    
    Args:
        holdings_df (pandas.DataFrame): DataFrame with portfolio holdings including quantity and market value
        performance_df (pandas.DataFrame): DataFrame with historical price data
    
    Returns:
        tuple: (updated holdings_df with new columns, previous_day_change_percentage as float)
    """
    try:
        if holdings_df.empty or performance_df.empty:
            # st.warning("Empty holdings or performance data. Cannot calculate market value changes.")
            return holdings_df.copy(), None
        
        # Make a copy of the holdings dataframe to avoid modifying the original
        result_df = holdings_df.copy()
        
        # Ensure date column is datetime
        performance_df['date'] = pd.to_datetime(performance_df['date'])
        
        # Simply use the most recent date in the performance data as our reference point
        # This is the most reliable approach since market data might have delays
        latest_date = performance_df['date'].max()
        
        # Print the reference date (can be seen when running outside of Streamlit)
        print(f"Using {latest_date} as reference date for market value calculations")

        # Calculate target dates for different time periods
        prev_day_target = latest_date - pd.Timedelta(days=1)  # Previous transaction day
        week_target = latest_date - pd.Timedelta(days=7)      # 1 week ago
        month_target = latest_date - pd.Timedelta(days=30)    # 1 month ago
        six_month_target = latest_date - pd.Timedelta(days=180)  # 6 months ago
        year_target = latest_date - pd.Timedelta(days=365)    # 1 year ago
        
        # Dictionary to store previous transaction day's total market value (CAD)
        prev_day_market_value_cad = 0.0
        current_day_market_value_cad = 0.0
        cad_exchange_sample = result_df[result_df['currency'] == 'USD'].sample(1)
        cad_exchange_rate = cad_exchange_sample['current_market_value_CAD']/cad_exchange_sample['current_market_value']
        cad_exchange_rate = float(cad_exchange_rate.iloc[0])

        # Process each symbol in the holdings
        for idx, row in result_df.iterrows():
            symbol = row['symbol']
            quantity = float(row['quantity'])

            currency = row['currency']
            current_price = float(row['current_price'])
            current_market_value_local = float(row['current_market_value'])
            current_market_value_cad = float(row['current_market_value_CAD'])
            
            # Add current market value (CAD) to total
            current_day_market_value_cad += current_market_value_cad
            
            # Filter performance data for this symbol
            symbol_perf = performance_df[performance_df['symbol'] == symbol].sort_values('date', ascending=False)
            
            if symbol_perf.empty:
                # No performance data for this symbol, fill with NaN
                result_df.at[idx, 'Market Value 1 Day (%)'] = float('nan')
                result_df.at[idx, 'Market Value 1 WK (%)'] = float('nan')
                result_df.at[idx, 'Market Value 1 Month (%)'] = float('nan')
                result_df.at[idx, 'Market Value 6 Months (%)'] = float('nan')
                result_df.at[idx, 'Market Value 1 Year (%)'] = float('nan')
                continue
            
            # Get the current day's closing price
            current_day_data = symbol_perf[symbol_perf['date'] == latest_date]
            if current_day_data.empty and len(symbol_perf) > 0:
                # If there's no data for the latest date, use the most recent available
                current_day_data = symbol_perf.iloc[0:1]
            
            # Function to find the closest date to a target date
            def find_closest_date(target_date):
                # Find the closest date that's <= target_date
                valid_dates = symbol_perf[symbol_perf['date'] <= target_date]
                if not valid_dates.empty:
                    return valid_dates.iloc[0]
                return None
            
            # Find closest dates for each period
            prev_day_data = find_closest_date(prev_day_target)
            week_ago_data = find_closest_date(week_target)
            month_ago_data = find_closest_date(month_target)
            six_month_ago_data = find_closest_date(six_month_target)
            year_ago_data = find_closest_date(year_target)
            # Calculate market value changes
            if prev_day_data is not None:
                if current_price != current_day_data['close'].item():
                    prev_price = float(current_day_data['close'].item())
                else:
                    prev_price = float(prev_day_data['close'])
                prev_market_value = prev_price * quantity
                if currency == "USD":
                    prev_market_value_cad = prev_market_value * cad_exchange_rate
                else:
                    prev_market_value_cad = prev_market_value
                change_1d = (current_market_value_local - prev_market_value) / prev_market_value if prev_market_value > 0 else 0
                result_df.at[idx, 'Market Value 1 Day (%)'] = change_1d  # Convert to percentage
                # Add to previous day total for portfolio calculation
                prev_day_market_value_cad += prev_market_value_cad
            else:
                result_df.at[idx, 'Market Value 1 Day (%)'] = float('nan')
            
            if week_ago_data is not None:
                week_price = float(week_ago_data['close'])
                week_market_value = week_price * quantity
                change_1w = (current_market_value_local - week_market_value) / week_market_value if week_market_value > 0 else 0
                result_df.at[idx, 'Market Value 1 WK (%)'] = change_1w
            else:
                result_df.at[idx, 'Market Value 1 WK (%)'] = float('nan')
            
            if month_ago_data is not None:
                month_price = float(month_ago_data['close'])
                month_market_value = month_price * quantity
                change_1m = (current_market_value_local - month_market_value) / month_market_value if month_market_value > 0 else 0
                result_df.at[idx, 'Market Value 1 Month (%)'] = change_1m
            else:
                result_df.at[idx, 'Market Value 1 Month (%)'] = float('nan')
            
            if six_month_ago_data is not None:
                six_month_price = float(six_month_ago_data['close'])
                six_month_market_value = six_month_price * quantity
                change_6m = (current_market_value_local - six_month_market_value) / six_month_market_value if six_month_market_value > 0 else 0
                result_df.at[idx, 'Market Value 6 Months (%)'] = change_6m
            else:
                result_df.at[idx, 'Market Value 6 Months (%)'] = float('nan')
            
            if year_ago_data is not None:
                year_price = float(year_ago_data['close'])
                year_market_value = year_price * quantity
                change_1y = (current_market_value_local - year_market_value) / year_market_value if year_market_value > 0 else 0
                result_df.at[idx, 'Market Value 1 Year (%)'] = change_1y
            else:
                result_df.at[idx, 'Market Value 1 Year (%)'] = float('nan')
        
        # Calculate portfolio-level change percentage for previous day
        portfolio_prev_day_change = (current_day_market_value_cad - prev_day_market_value_cad) / prev_day_market_value_cad if prev_day_market_value_cad > 0 else 0
        
        return result_df, portfolio_prev_day_change
    
    except Exception as e:
        st.error(f"Error calculating market value changes: {e}")
        import traceback
        st.error(traceback.format_exc())
        return holdings_df.copy(), None
        
if __name__ == '__main__':
    # Test functions (optional)
    holdings, metrics = fetch_portfolio_data()
    if holdings and metrics:
        print("Portfolio Holdings:")
        print(pd.DataFrame(holdings).head())
        print("\nPortfolio Metrics:")
        print(metrics)

    print("\nAttempting to load latest performance data...")
    perf_df, max_performance_date = load_performance()
    if max_performance_date:
        print(f"\nPerformance Data from {max_performance_date}:")
        print(perf_df.head())
    else:
        print("Could not load a performance from API.")

    # Test portfolio correlation
    print("\nCalculating portfolio correlation...")
    holdings_df = pd.DataFrame(holdings) if holdings else pd.DataFrame()
    perf_df_for_cv = perf_df if not perf_df.empty else pd.DataFrame()
    
    if not holdings_df.empty and not perf_df_for_cv.empty:
        correlation_matrix, weighted_corr_matrix, portfolio_weighted_corr = calculate_portfolio_correlation(holdings_df, perf_df_for_cv)
        if correlation_matrix is not None and weighted_corr_matrix is not None and portfolio_weighted_corr is not None:
            print("Portfolio Correlation Results:")
            print(f"\nPortfolio Weighted Correlation: {portfolio_weighted_corr:.4f}")
            print(f"\nPortfolio Weighted Correlation Matrix:\n{weighted_corr_matrix.iloc[:3, :3]}")
            print(f"\nPortfolio Correlation Matrix:\n{correlation_matrix.iloc[:3, :3]}")
        else:
            print("Could not calculate portfolio correlation.")
    else:
        print("Missing required data for portfolio correlation calculation.")
        
    # Test market value changes function
    print("\nCalculating market value changes...")
    if not holdings_df.empty and not perf_df.empty:
        updated_holdings, portfolio_day_change = calculate_market_value_changes(holdings_df, perf_df)
        if updated_holdings is not None and portfolio_day_change is not None:
            print("Market Value Changes Results:")
            print(f"Portfolio 1-Day Change: {portfolio_day_change*100:.2f}%")
            print(f"\nSample of holdings with market value changes (first 3):\n{updated_holdings.head(3)}")
        else:
            print("Could not calculate market value changes.")
    else:
        print("Missing required data for market value changes calculation.")
