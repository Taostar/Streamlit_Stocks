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

@st.cache_data
def load_performance_csv():
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
        
        max_date = result_df['date'].max()
        
        return result_df, max_date  # Return DataFrame and None instead of file path
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching performance data from API: {e}")
        return pd.DataFrame(), None
    except json.JSONDecodeError:
        st.error("Error decoding JSON response from API.")
        return pd.DataFrame(), None
    except Exception as e:
        st.error(f"Unexpected error loading performance data: {e}")
        return pd.DataFrame(), None

def get_latest_performance_file(folder_path=PERFORMANCE_DATA_FOLDER):
    """Gets the latest performance data CSV file from the specified folder based on filename timestamp."""
    if not folder_path or not os.path.isdir(folder_path):
        st.warning(f"Performance data folder not found or not configured: '{folder_path}'")
        return None

    # Regex to find files with a timestamp like YYYYMMDD_HHMMSS
    pattern = re.compile(r'performance_data_OneDay_(\d{8}_\d{6}).*\.csv')
    files_with_dates = []

    for f in os.listdir(folder_path):
        match = pattern.search(f)
        if match:
            try:
                # Extract timestamp string and convert to datetime object
                timestamp_str = match.group(1)
                dt_obj = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                files_with_dates.append((dt_obj, os.path.join(folder_path, f)))
            except ValueError:
                # Ignore files with malformed date strings
                continue

    if not files_with_dates:
        st.warning(f"No valid performance CSV files found in '{folder_path}'. Looked for pattern 'performance_data_OneDay_YYYYMMDD_HHMMSS.csv'")
        return None

    # Find the file with the most recent date
    latest_file = max(files_with_dates, key=lambda item: item[0])
    return latest_file[1] # Return the file path

if __name__ == '__main__':
    # Test functions (optional)
    holdings, metrics = fetch_portfolio_data()
    if holdings and metrics:
        print("Portfolio Holdings:")
        print(pd.DataFrame(holdings).head())
        print("\nPortfolio Metrics:")
        print(metrics)

    print("\nAttempting to load latest performance data...")
    perf_df, latest_file = load_performance_csv()
    if latest_file:
        print(f"Loaded from: {latest_file}")
        print("\nPerformance Data:")
        print(perf_df.head())
    else:
        print("Could not find or load a performance file.")
