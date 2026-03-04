# Portfolio Dashboard

A portfolio visualization dashboard with a React/TypeScript frontend and a FastAPI backend. Displays stock/ETF holdings, performance analytics, correlation matrices, exchange rates, and benchmark comparisons.

## Architecture

```
External API (ngrok)
    ├── /accounts/holdings  → portfolio holdings & metrics
    └── /market/data        → historical OHLCV price data
            ↓
    FastAPI Backend (backend/)
        ├── /api/v1/portfolio   → portfolio overview & metrics
        ├── /api/v1/holdings    → current holdings table
        ├── /api/v1/correlation → correlation matrix
        ├── /api/v1/exchange    → exchange rates (USD/CAD, CAD/CNY, BTC/USD)
        ├── /api/v1/benchmark   → benchmark comparison
        └── /api/v1/performance → individual asset candlestick data
            ↓
    React Frontend (frontend/)
        └── Vite + React 19 + TailwindCSS + Plotly.js dashboard
```

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Settings (external API URL, CORS, cache TTLs)
│   │   ├── api/v1/
│   │   │   ├── router.py        # API router
│   │   │   ├── endpoints/       # portfolio, holdings, correlation, exchange, benchmark, performance
│   │   │   └── schemas/         # Pydantic request/response models
│   │   ├── services/            # Business logic & data processing
│   │   └── core/cache.py        # Caching layer
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.tsx             # React entry point
│   │   ├── App.tsx              # Root component (React Query provider)
│   │   ├── pages/Dashboard.tsx  # Main dashboard page
│   │   ├── api/                 # Axios client & API calls
│   │   ├── components/
│   │   │   ├── charts/          # BarChart, CandlestickChart, HeatmapChart, LineChart, PieChart
│   │   │   ├── common/          # Layout, MetricCard
│   │   │   ├── sections/        # Dashboard sections (PortfolioOverview, AssetAllocation, etc.)
│   │   │   └── tables/          # HoldingsTable
│   │   ├── hooks/usePortfolio.ts
│   │   ├── types/portfolio.ts
│   │   └── utils/               # formatters, colorUtils
│   └── package.json
├── config.json                  # Legacy: ngrok API_URL (used by old Streamlit app)
└── requirements.txt             # Legacy: Streamlit dependencies
```

## Setup

### Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure the external API URL (optional — defaults to the ngrok URL in config.py)
echo "EXTERNAL_API_URL=https://your-ngrok-url.ngrok-free.app" > .env

# Start the server
uvicorn app.main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure the backend URL (optional — defaults to http://localhost:8000/api/v1)
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env

# Start the dev server
npm run dev
```

Opens at `http://localhost:5173`.

## Configuration

| Location | Variable | Default | Description |
|---|---|---|---|
| `backend/.env` | `EXTERNAL_API_URL` | ngrok URL | The external portfolio data API |
| `backend/.env` | `CORS_ORIGINS` | `localhost:5173,3000` | Allowed frontend origins |
| `frontend/.env` | `VITE_API_URL` | `http://localhost:8000/api/v1` | Backend API base URL |

## Dashboard Sections

- **Portfolio Overview** — total market value (CAD), cumulative return, Sharpe ratio, daily return
- **Asset Allocation** — pie chart of portfolio weights
- **Current Holdings** — sortable holdings table with market values and currencies
- **Holdings Bar Chart** — bar chart of position sizes
- **Correlation Matrix** — heatmap of pairwise asset correlations
- **Exchange Rates** — USD/CAD, CAD/CNY, USD/CNY, BTC/USD live rates
- **Benchmark Comparison** — portfolio vs. benchmark (e.g. SPY) performance
- **Individual Asset** — candlestick OHLCV chart per symbol

## Tech Stack

**Backend:** Python, FastAPI, Uvicorn, Pydantic v2, yfinance, pandas, cachetools

**Frontend:** React 19, TypeScript, Vite, TailwindCSS 4, Plotly.js, TanStack Query, TanStack Table, Axios
