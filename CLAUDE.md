# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py

# Run on a specific port
streamlit run app.py --server.port 8502

# Run with Dev Container settings (disables CORS/XSRF for local dev)
streamlit run app.py --server.enableCORS false --server.enableXsrfProtection false
```

## Architecture

This is a Streamlit portfolio visualization dashboard that displays stock/ETF holdings and performance analytics.

### Data Flow

```
Backend API (ngrok)
    ├── /accounts/holdings → Portfolio holdings & metrics
    └── /market/data       → Historical OHLCV price data
            ↓
      utils.py (data processing & caching)
            ↓
      app.py (Streamlit dashboard)
```

### Key Files

- **app.py**: Main Streamlit application with all dashboard sections (overview metrics, allocation pie chart, holdings table, correlation heatmap, exchange rates, benchmark comparison, candlestick charts)
- **utils.py**: Data fetching and processing functions with Streamlit caching decorators
- **config.json**: Contains `API_URL` for the backend endpoint (ngrok URL)

### Caching Strategy

All data functions use `@st.cache_data()` with different TTLs:
- `fetch_portfolio_data()`: 5 minutes (holdings change frequently)
- `load_performance()`: 1 hour (historical data)
- `calculate_portfolio_correlation()`: 1 hour
- `calculate_market_value_changes()`: 1 hour
- Exchange rate data: 1 day
- Correlation heatmap figure: 1 hour

### API Data Structures

**Holdings endpoint** (`/accounts/holdings`) returns:
```json
{
  "portfolio_holdings": [{"symbol", "quantity", "current_price", "current_market_value", "current_market_value_CAD", "currency", "percentage"}],
  "portfolio_metrics": {"Total Market Value (CAD)", "Cumulative Return", "Average Daily Return", "Sharpe Ratio", "Symbols", "Allocations"}
}
```

**Market data endpoint** (`/market/data`) returns array of `{symbol, data: [{date, open, high, low, close, volume}]}`.

### External Dependencies

- yfinance: Used for exchange rate data (USD/CAD, CAD/CNY, USD/CNY, BTC/USD)
- plotly: Interactive charts (pie, bar, line, candlestick)
- seaborn/matplotlib: Correlation heatmap
