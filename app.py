import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import fetch_portfolio_data, load_performance_csv, API_URL
from datetime import datetime, timedelta
import os

st.set_page_config(layout="wide", page_title="Portfolio Dashboard")

st.title("📈 Portfolio Visualization Dashboard")

# --- Load Data ---
portfolio_holdings_data, portfolio_metrics_data = fetch_portfolio_data()
performance_df_oneday, max_performance_date = load_performance_csv()

if portfolio_holdings_data is None or portfolio_metrics_data is None:
    st.error("Failed to load portfolio data from API. Please check the API endpoint and your connection.")
    st.stop()

holdings_df = pd.DataFrame(portfolio_holdings_data)

# --- Sidebar for Data Source Info (Optional) ---
st.sidebar.header("Data Sources")
st.sidebar.markdown(f"**Holdings ngrok endpoint:** `{API_URL}/accounts/holdings` & `{API_URL}/market/data`")
st.sidebar.markdown(f"**Performance History Max Date:** `{max_performance_date}`")
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
            st.sidebar.text(f"{key.replace('_', ' ').title()}: {value}")

# --- Main Page Layout ---

# Section 1: Overview Metrics & Allocation
st.header("Portfolio Overview")
if portfolio_metrics_data:
    total_value_cad = portfolio_metrics_data.get("Total Market Value (CAD)", 0)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Portfolio Value (CAD)", f"${total_value_cad:,.2f}")
    col2.metric("Cumulative Return", f"{portfolio_metrics_data.get('Cumulative Return', 0):.2%}")
    col3.metric("Sharpe Ratio", f"{portfolio_metrics_data.get('Sharpe Ratio', 0):.2f}")

if not holdings_df.empty:
    st.subheader("Asset Allocation (CAD Market Value)")
    # Ensure 'current_market_value_CAD' is numeric
    holdings_df['current_market_value_CAD'] = pd.to_numeric(holdings_df['current_market_value_CAD'], errors='coerce')
    holdings_df.dropna(subset=['current_market_value_CAD'], inplace=True)

    fig_allocation = px.pie(holdings_df, 
                              values='current_market_value_CAD', 
                              names='symbol', 
                              title='Portfolio Allocation by Symbol (CAD)',
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
        'symbol', 'quantity', 'average_entry_price', 'current_price', 
        'current_market_value', 'currency', 'current_market_value_CAD', 'percentage'
    ]].copy()
    display_df.rename(columns={
        'symbol': 'Symbol',
        'quantity': 'Quantity',
        'average_entry_price': 'Avg. Entry Price',
        'current_price': 'Current Price',
        'current_market_value': 'Market Value (Local)',
        'currency': 'Currency',
        'current_market_value_CAD': 'Market Value (CAD)',
        'percentage': 'Portfolio %'
    }, inplace=True)
    
    # Formatting
    for col in ['Avg. Entry Price', 'Current Price', 'Market Value (Local)', 'Market Value (CAD)']:
        display_df[col] = display_df[col].apply(lambda x: f"{x:,.2f}" if pd.notnull(x) else 'N/A')
    display_df['Portfolio %'] = display_df['Portfolio %'].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else 'N/A')
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
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

# Section 3: Performance Comparison (VOO & QQQ)
st.header("Market Benchmark Comparison (Past Year)")
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

normalized_benchmark_data = calc_normalized_benchmark_data(performance_df_oneday, portfolio_metrics_data)

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

if not performance_df_oneday.empty:
    # Get unique symbols for selection
    symbols = sorted(performance_df_oneday['symbol'].unique())
    selected_symbol = st.selectbox("Select Asset to View:", symbols)
    
    # Filter data for selected symbol
    symbol_data = performance_df_oneday[performance_df_oneday['symbol'] == selected_symbol].copy()
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

st.info("This is a foundational version of the portfolio dashboard. More features and visualizations can be added as more detailed historical data becomes available.")

# To run this app: streamlit run app.py
