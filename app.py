import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import fetch_portfolio_data, load_performance, API_URL, calculate_portfolio_correlation, calculate_market_value_changes
from datetime import datetime, timedelta
import os

st.set_page_config(layout="wide", page_title="Portfolio Dashboard")

st.title("📈 Portfolio Dashboard")

# --- Load Data ---
portfolio_holdings_data, portfolio_metrics_data = fetch_portfolio_data()
performance_df = load_performance()
max_performance_date = performance_df['date'].max()
min_performance_date = performance_df['date'].min()
if portfolio_holdings_data is None or portfolio_metrics_data is None:
    st.error("Failed to load portfolio data from API. Please check the API endpoint and your connection.")
    st.stop()

holdings_df = pd.DataFrame(portfolio_holdings_data)

# Formatting and Styling
def color_change(val):
    """
    Colors values based on intensity - green for positive, red for negative values.
    """
    if pd.isna(val) or val == 0:
        return ''
    
    if val > 0:
        # Gradient of green based on value intensity
        if val > 0.1:  # Strong positive
            color = '#006400'  # Dark green
        elif val > 0.05:  # Medium positive
            color = '#008000'  # Green
        else:  # Slight positive
            color = '#90EE90'  # Light green
    else:
        # Gradient of red based on value intensity
        if val < -0.1:  # Strong negative
            color = '#8B0000'  # Dark red
        elif val < -0.05:  # Medium negative
            color = '#FF0000'  # Red
        else:  # Slight negative
            color = '#FFA07A'  # Light red
    return f'color: {color}'

# --- Sidebar for Data Source Info (Optional) ---
st.sidebar.header("Data Sources")
st.sidebar.markdown(f"**Holdings ngrok endpoint:** `{API_URL}/accounts/holdings` & `{API_URL}/market/data`")
st.sidebar.markdown(f"**Performance History Range:** `F:{min_performance_date}T:{max_performance_date}`")
st.sidebar.markdown("---")
st.sidebar.header("Current Portfolio Metrics")
if portfolio_metrics_data:
    for key, value in portfolio_metrics_data.items():
        if isinstance(value, list) and key == "Allocations":
            # Allocations are better visualized, skip raw display here
            pass 
        elif isinstance(value, float):
            if "percentage" in key.lower() or "return" in key.lower() or "ratio" in key.lower() or "deviation" in key.lower():
                 st.sidebar.metric(label=key.replace('_', ' ').title(), value=f"{value:.2%}" if "return" in key.lower() or "percentage" in key.lower() else f"{value:.2f}")
            else:
                st.sidebar.metric(label=key.replace('_', ' ').title(), value=f"{value:,.2f}")
        else:
            st.sidebar.text(f"{key.replace('_', ' ').title()}: {', '.join(value)}")

# --- Main Page Layout ---

# Section 1: Overview Metrics & Allocation
st.header("Portfolio Overview")
if portfolio_metrics_data:
    total_value_cad = portfolio_metrics_data.get("Total Market Value (CAD)", 0)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Portfolio Value (CAD)", f"${total_value_cad:,.2f}")
    col2.metric("Cumulative Return", f"{portfolio_metrics_data.get('Cumulative Return', 0):.2%}")
    col3.metric("Average Daily Return", f"{portfolio_metrics_data.get('Average Daily Return', 0):.2%}")
    col4.metric("Sharpe Ratio", f"{portfolio_metrics_data.get('Sharpe Ratio', 0):.2f}")

col1, col2, col3, col4 = st.columns(4)
correlation_matrix, weighted_corr_matrix, portfolio_weighted_corr = calculate_portfolio_correlation(holdings_df, performance_df)
holdings_df, prev_day_change_percentage = calculate_market_value_changes(holdings_df, performance_df)
col1.metric("Portfolio Weighted Correlation", f"{portfolio_weighted_corr:.2f}")
col2.metric("Previous Day Change", f"{prev_day_change_percentage:.2%}")

if not holdings_df.empty:
    st.subheader("Asset Allocation (CAD Market Value)")
    # Ensure 'current_market_value_CAD' is numeric
    holdings_df['current_market_value_CAD'] = pd.to_numeric(holdings_df['current_market_value_CAD'], errors='coerce')
    holdings_df.dropna(subset=['current_market_value_CAD'], inplace=True)

    fig_allocation = px.pie(holdings_df, 
                              values='current_market_value_CAD', 
                              names='symbol', 
                            #   title='Portfolio Allocation by Symbol (CAD)',
                              hover_data=['percentage', 'currency', 'current_price'],
                              labels={'current_market_value_CAD':'Market Value (CAD)', 'symbol':'Symbol'})
    fig_allocation.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_allocation, use_container_width=True)
else:
    st.warning("No holdings data available to display allocation chart.")

# Section 2: Holdings Details
st.header("Current Holdings")
if not holdings_df.empty:
    # Select and rename columns for better display
    display_df = holdings_df[[
        'symbol', 'quantity', 'current_price',
        'current_market_value', 'currency', 'percentage',
        'Market Value 1 Day (%)', 'Market Value 1 WK (%)', 'Market Value 1 Month (%)',
        'Market Value 6 Months (%)', 'Market Value 1 Year (%)'
    ]].copy()
    # Convert quantity column to integer type
    display_df['quantity'] = display_df['quantity'].astype(int)
    col_map = {
        'symbol': 'Symbol',
        'currency': 'Currency',
        'quantity': 'Quantity',
        'current_price': 'Current Price',
        'current_market_value': 'Market Value',
        'percentage': 'Portfolio %',
        'Market Value 1 Day (%)': '1 Day (%)', 
        'Market Value 1 WK (%)': '1 WK (%)',
        'Market Value 1 Month (%)': '1 Month (%)',
        'Market Value 6 Months (%)': '6 Months (%)', 
        'Market Value 1 Year (%)': '1 Year (%)'
    }
    display_df.rename(columns=col_map, inplace=True)
    display_df = display_df[list(col_map.values())]

    market_value_cols = [col for col in display_df.columns if col.endswith('(%)')]

    formatters = {
        'Current Price': '{:,.2f}',
        'Market Value': '{:,.2f}',
        'Portfolio %': '{:.2f}%',
    }
    for col in market_value_cols:
        formatters[col] = '{:.2%}'

    styled_df = display_df.style.applymap(
        color_change, subset=market_value_cols
    ).format(formatters, na_rep='N/A')
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
else:
    st.warning("No holdings data to display.")

# Bar chart of holdings by market value
if not holdings_df.empty:
    st.subheader("Holdings by Market Value (CAD)")
    top_n = st.slider("Number of top holdings to display:", min_value=5, max_value=len(holdings_df), value=min(15, len(holdings_df)), key='top_n_slider')
    
    # Sort by market value and take top N
    sorted_holdings = holdings_df.sort_values(by='current_market_value_CAD', ascending=False).head(top_n)
    
    fig_bar_market_value = px.bar(sorted_holdings, 
                                    x='symbol', 
                                    y='current_market_value_CAD', 
                                    title=f'Top {top_n} Holdings by Market Value (CAD)',
                                    labels={'current_market_value_CAD':'Market Value (CAD)', 'symbol':'Symbol'},
                                    color='symbol')
    st.plotly_chart(fig_bar_market_value, use_container_width=True)
else:
    st.warning("No holdings data to display.")



# Section 3: Correlation Matrix Visualization
st.header("Portfolio Correlation Matrix")
st.markdown("Visualize the correlation between assets in your portfolio.")

if correlation_matrix is not None and not correlation_matrix.empty:
    # Use a more efficient rendering approach with Seaborn + Matplotlib
    import matplotlib.pyplot as plt
    import seaborn as sns
    from matplotlib.colors import LinearSegmentedColormap
    import numpy as np
    
    # Generate a correlation matrix visualization
    @st.cache_data(ttl=3600)  # Cache the figure for 1 hour to improve performance
    def generate_corr_heatmap(corr_matrix):
        # Create a custom color map that mimics the RdBu_r but is more efficient
        colors = ["#053061", "#2166ac", "#92c5de", "#f7f7f7", "#f4a582", "#d6604d", "#b2182b"]
        cmap = LinearSegmentedColormap.from_list('custom_diverging', colors, N=100)
        
        # Set the figure size based on the number of assets
        n_assets = len(corr_matrix)
        figsize = (min(12, max(8, n_assets * 0.7)), min(10, max(6, n_assets * 0.7)))
        
        # Create the figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Generate the heatmap - much more efficient without annotations on every cell
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)  # Create mask for upper triangle
        heatmap = sns.heatmap(
            corr_matrix, 
            annot=True,  # Show correlation values
            fmt=".2f",   # Format to 2 decimal places
            cmap=cmap,   # Custom colormap
            vmin=-1, vmax=1,  # Fix bounds between -1 and 1
            center=0,    # Center the colormap at 0
            square=True, # Make cells square
            linewidths=.5,  # Add thin lines between cells
            annot_kws={"size": 8 if n_assets > 10 else 9},  # Adjust text size based on matrix size
            mask=mask,   # Only show lower triangle (reduces visual redundancy)
            cbar_kws={"shrink": 0.8, "label": "Correlation"}  # Colorbar settings
        )
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        plt.title("Asset Correlation Heatmap", fontsize=14, pad=20)
        
        # Tighten the layout to ensure everything fits
        plt.tight_layout()
        
        return fig
    
    # Generate and display the heatmap
    corr_fig = generate_corr_heatmap(correlation_matrix)
    st.pyplot(corr_fig)
    
    # Explanation of the correlation matrix
    with st.expander("What does this correlation matrix show?"):
        st.markdown("""
        This correlation matrix shows how the returns of different assets in your portfolio move in relation to each other:
        
        - **+1.00**: Perfect positive correlation - assets move exactly the same way
        - **0.00**: No correlation - assets move independently of each other
        - **-1.00**: Perfect negative correlation - assets move exactly opposite to each other
        
        A well-diversified portfolio typically includes assets with low or negative correlations to each other, 
        which can help reduce overall portfolio risk.
        """)
else:
    st.warning("Correlation data is not available. Please ensure your portfolio contains multiple assets with historical price data.")

# Section 4: Exchange Rate Tracking
st.header("Exchange Rate")
st.markdown("Track historical exchange rates between major currencies and Bitcoin.")

@st.cache_data(ttl=86400)  # Cache for 1 day
def load_exchange_rate_data(ticker, period="1y"):
    """
    Load exchange rate data from Yahoo Finance API and process it for visualization.
    
    Args:
        ticker (str): Yahoo Finance ticker symbol for the exchange rate pair
        period (str): Time period for data retrieval (default: 1 year)
        
    Returns:
        pandas.DataFrame: Processed exchange rate data with simple column structure
    """
    import yfinance as yf
    try:
        # Download data from Yahoo Finance
        data = yf.download(ticker, period=period, progress=False)
        
        # If data is empty, return empty DataFrame
        if data.empty:
            return pd.DataFrame()
            
        # Create a clean DataFrame with the columns we need
        processed_df = pd.DataFrame()
        processed_df['Date'] = data.index
        
        # Extract 'Close' price - handle both MultiIndex and regular columns
        if isinstance(data.columns, pd.MultiIndex):
            # For MultiIndex, get the first level 'Close' column
            # This works regardless of the second level
            close_cols = [col for col in data.columns if col[0] == 'Close']
            if close_cols:
                processed_df['Close'] = data[close_cols[0]].values
            else:
                return pd.DataFrame()  # No Close column found
        else:
            # For regular columns, just get 'Close'
            if 'Close' in data.columns:
                processed_df['Close'] = data['Close'].values
            else:
                return pd.DataFrame()  # No Close column found
        
        # Add other columns if needed for display
        for col_name in ['Open', 'High', 'Low']:
            if isinstance(data.columns, pd.MultiIndex):
                cols = [col for col in data.columns if col[0] == col_name]
                if cols:
                    processed_df[col_name] = data[cols[0]].values
            elif col_name in data.columns:
                processed_df[col_name] = data[col_name].values
        
        # Calculate daily change
        processed_df['Daily Change %'] = processed_df['Close'].pct_change() * 100
        
        return processed_df
    except Exception as e:
        st.error(f"Error loading exchange rate data: {e}")
        return pd.DataFrame()

# Define currency pairs and their tickers
currency_pairs = {
    "USD/CAD": "CAD=X",  # Canadian Dollar to US Dollar
    "CAD/CNY": "CADCNY=X",  # Canadian Dollar to Chinese Yuan
    "USD/CNY": "CNY=X",  # US Dollar to Chinese Yuan
    "BTC/USD": "BTC-USD",  # US Dollar to Bitcoin
}

# Create tabs for different currency pairs
selected_pair = st.radio(
    "Select Currency Pair:",
    list(currency_pairs.keys()),
    horizontal=True
)

# # Add a debug section
# with st.expander("Debug Info", expanded=False):
#     st.write("This section shows debugging information for the exchange rate data.")
#     debug_info = st.empty()

try:
    # Load data for selected pair
    ticker = currency_pairs[selected_pair]
    exchange_data = load_exchange_rate_data(ticker)

    # # Debug information
    # with debug_info.container():
    #     st.write("Exchange Rate Data Info:")
    #     st.write(f"Data shape: {exchange_data.shape if not exchange_data.empty else 'Empty DataFrame'}")
    #     if not exchange_data.empty:
    #         st.write(f"Columns: {exchange_data.columns.tolist()}")
    #         st.write(f"Data types: {exchange_data.dtypes}")
    #         st.write("Sample data:")
    #         st.write(exchange_data.head(2))
    
    if not exchange_data.empty and 'Close' in exchange_data.columns:
        # Process the data
        try:
            # Make a copy to avoid chained indexing warnings
            processed_data = exchange_data.copy()
            
            # Calculate daily percentage change safely
            processed_data['Daily Change %'] = processed_data['Close'].pct_change() * 100
            
            # Get scalar values for calculations
            start_price = processed_data['Close'].iloc[0]
            current_price = processed_data['Close'].iloc[-1]
            
            # Ensure these are scalar values
            start_price = float(start_price)
            current_price = float(current_price)
            
            # Calculate change values
            ytd_change = ((current_price - start_price) / start_price) * 100
            
            # Get daily change safely
            try:
                # Get the last row's daily change as a scalar value
                daily_change_value = processed_data['Daily Change %'].iloc[-1]
                daily_change = float(daily_change_value) if not pd.isna(daily_change_value) else 0.0
            except:
                daily_change = 0.0
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            
            # Format display values
            if selected_pair == "USD/BTC":
                price_display = f"{current_price:,.2f}"
            else:
                price_display = f"{current_price:.4f}"
            
            col1.metric(
                "Current Rate", 
                price_display,
                f"{daily_change:.2f}%"
            )
            col2.metric("Year-to-Date Change", f"{ytd_change:.2f}%")
            
            # Create exchange rate chart
            fig = px.line(
                processed_data, 
                x='Date', 
                y='Close',
                title=f'{selected_pair} Exchange Rate (Past Year)',
                labels={'Close': 'Exchange Rate', 'Date': 'Date'}
            )
            
            # Add range slider
            fig.update_layout(
                xaxis=dict(
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1, label="1m", step="month", stepmode="backward"),
                            dict(count=3, label="3m", step="month", stepmode="backward"),
                            dict(count=6, label="6m", step="month", stepmode="backward"),
                            dict(step="all")
                        ])
                    ),
                    rangeslider=dict(visible=True),
                    type="date"
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # # Show recent exchange rate data table
            # st.subheader("Recent Exchange Rate Data")
            # display_cols = ['Date', 'Open', 'High', 'Low', 'Close']
            # st.dataframe(
            #     processed_data[display_cols].tail(10).sort_values('Date', ascending=False),
            #     use_container_width=True,
            #     hide_index=True
            # )
        except Exception as e:
            st.error(f"Error processing exchange rate data: {str(e)}")
            st.info("The data may be incomplete or in an unexpected format.")
    elif not exchange_data.empty:
        st.error(f"Data is missing required 'Close' column. Found columns: {exchange_data.columns.tolist()}")
    else:
        st.warning(f"No exchange rate data available for {selected_pair}.")
except Exception as e:
    st.error(f"Error loading exchange rate data: {str(e)}")
    st.info("Please try a different currency pair or check your internet connection.")


# Section 4: Performance Comparison (VOO & QQQ)
st.header("Market Benchmark Comparison")
st.markdown("This section shows the performance of Portfolio vs QQQ/VOO over the past year.")

@st.cache_data(ttl=86400) # Cache for a day
def calc_normalized_benchmark_data(df, portfolio_metrics_data):
    
    sort_by_cols = ['symbol', 'date']
    df = df.sort_values(by=sort_by_cols).reset_index(drop=True)
    # Convert date to datetime and pivot the DataFrame
    df['date'] = pd.to_datetime(df['date'])

    # Filter for close prices and pivot the data
    prices_df = df.pivot(index='date', columns='symbol', values='close')
    prices_df = prices_df.ffill().bfill()

    symbols_allocs = dict(zip(portfolio_metrics_data["Symbols"], portfolio_metrics_data["Allocations"]))
    symbols_allocs = {k: float(v.strip('%')) for k, v in symbols_allocs.items()}
    sorted_symbols = sorted(prices_df.columns)
    sorted_portfolio = {symbol: symbols_allocs[symbol] for symbol in sorted_symbols}
    allocations = [float(alloc) for alloc in sorted_portfolio.values()]

    normalized_allocs_positions = prices_df / prices_df.iloc[0] * allocations
    normalized_allocs_positions = normalized_allocs_positions.sum(axis = 1)
    normalized_benchmark_data = prices_df[['QQQ', 'VOO']].copy()
    normalized_benchmark_data = normalized_benchmark_data / normalized_benchmark_data.iloc[0] * 100
    normalized_benchmark_data['Portfolio'] = normalized_allocs_positions

    return normalized_benchmark_data

normalized_benchmark_data = calc_normalized_benchmark_data(performance_df, portfolio_metrics_data)

if not normalized_benchmark_data.empty:
    fig_benchmark = px.line(normalized_benchmark_data, title='Portfolio vs QQQ/VOO Performance (Normalized to 100)')
    fig_benchmark.update_layout(
        yaxis=dict(
            title=dict(
                text='Normalized Price (Start = 100)',
                font=dict(size=14)  # You can adjust or add other font properties like color, family
            )
        ),
        legend_title_text='Ticker'
    )
    st.plotly_chart(fig_benchmark, use_container_width=True)
else:
    st.warning("Could not load Portfolio QQQ/VOO historical data at this time.")

# Section 4: Individual Stock Performance
st.header("Individual Asset Performance")
st.markdown("This section shows the past year's performance for each of your holdings.")

if not performance_df.empty:
    # Get unique symbols for selection
    symbols = sorted(performance_df['symbol'].unique())
    selected_symbol = st.selectbox("Select Asset to View:", symbols)
    
    # Filter data for selected symbol
    symbol_data = performance_df[performance_df['symbol'] == selected_symbol].copy()
    symbol_data['date'] = pd.to_datetime(symbol_data['date'])
    symbol_data = symbol_data.sort_values('date')
    
    # Create figure with secondary y-axis for volume
    fig = go.Figure()
    
    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=symbol_data['date'],
            open=symbol_data['open'],
            high=symbol_data['high'],
            low=symbol_data['low'],
            close=symbol_data['close'],
            name="Price",
        )
    )
    
    # Add volume as bar chart on secondary y-axis with color scale based on volume
    fig.add_trace(
        go.Bar(
            x=symbol_data['date'],
            y=symbol_data['volume'],
            name="Volume",
            marker=dict(
                color=symbol_data['volume'],
                colorscale='Plasma',
                showscale=False
            ),
            opacity=0.6,
            yaxis="y2"
        )
    )
    
    # Layout updates for dual y-axis
    fig.update_layout(
        title=f'{selected_symbol} Price and Volume',
        yaxis_title='Price',
        xaxis_title='Date',
        yaxis2=dict(
            title=dict(
                text='Volume',
                font=dict(color='rgba(58, 71, 80, 0.6)')
            ),
            tickfont=dict(color='rgba(58, 71, 80, 0.6)'),
            anchor="x",
            overlaying="y",
            side="right"
        ),
        height=600,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(rangebreaks=[
            dict(bounds=["sat", "mon"]),  # hide weekends
            dict(values=symbol_data[
                symbol_data['open'].isna() & 
                symbol_data['high'].isna() & 
                symbol_data['low'].isna() & 
                symbol_data['close'].isna()
            ]['date']) # hide days with no OHLC data
        ])
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No performance data file found or loaded. Check the `performance_reports` folder for valid files.")


# You can add more visualizations here as data becomes available or ideas emerge.
# For example:
# - Sector allocation (if sector data is available for each symbol)
# - Currency exposure
# - Performance attribution (if historical returns per stock and benchmark are available)


# Add beautiful links section at the end of the dashboard
st.markdown("---")
st.header("📚 Resources")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("[![Stock Note](https://img.shields.io/badge/Stock_Note-000000?style=for-the-badge&logo=notion&logoColor=white)](https://www.notion.so/Stock-Note-03acb655380c44f98dbce4117d698539)")
    st.caption("Stock Note")
with col2:
    st.markdown("[![Macrotrends](https://img.shields.io/badge/Macrotrends-4285F4?style=for-the-badge&logo=google-analytics&logoColor=white)](https://www.macrotrends.net/stocks/research)")
    st.caption("Basic Analysis")
with col3:
    st.markdown("[![Yahoo Finance](https://img.shields.io/badge/Yahoo_Finance-6001D2?style=for-the-badge&logo=yahoo&logoColor=white)](https://finance.yahoo.com/quote/IFC.TO/)")
    st.caption("Advanced charting and analysis")

# To run this app: streamlit run app.py
