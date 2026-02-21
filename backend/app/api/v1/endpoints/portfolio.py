from fastapi import APIRouter, HTTPException
from app.api.v1.schemas.portfolio import PortfolioOverview, AllocationResponse, AllocationItem
from app.services.external_api import fetch_portfolio_data, get_holdings_dataframe, load_performance
from app.services.correlation_service import calculate_portfolio_correlation
from app.services.market_value_service import calculate_market_value_changes

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/overview", response_model=PortfolioOverview)
async def get_portfolio_overview():
    """Get portfolio overview metrics for the 6 metric cards."""
    holdings, metrics = await fetch_portfolio_data()

    if holdings is None or metrics is None:
        raise HTTPException(status_code=503, detail="Unable to fetch portfolio data")

    holdings_df = await get_holdings_dataframe()
    performance_df = await load_performance()

    # Calculate correlation
    weighted_correlation = None
    if not holdings_df.empty and not performance_df.empty:
        _, _, weighted_correlation = calculate_portfolio_correlation(
            holdings_df, performance_df
        )

    # Calculate previous day change
    prev_day_change = None
    if not holdings_df.empty and not performance_df.empty:
        _, prev_day_change = calculate_market_value_changes(holdings_df, performance_df)

    return PortfolioOverview(
        total_value_cad=metrics.get("Total Market Value (CAD)", 0),
        cumulative_return=metrics.get("Cumulative Return", 0),
        avg_daily_return=metrics.get("Average Daily Return", 0),
        sharpe_ratio=metrics.get("Sharpe Ratio", 0),
        weighted_correlation=weighted_correlation,
        prev_day_change=prev_day_change,
    )


@router.get("/allocation", response_model=AllocationResponse)
async def get_portfolio_allocation():
    """Get asset allocation data for the pie chart."""
    holdings, metrics = await fetch_portfolio_data()

    if holdings is None:
        raise HTTPException(status_code=503, detail="Unable to fetch holdings data")

    items = []
    total_value = 0

    for holding in holdings:
        market_value_cad = float(holding.get("current_market_value_CAD", 0))
        total_value += market_value_cad

        items.append(
            AllocationItem(
                symbol=holding.get("symbol", ""),
                market_value_cad=market_value_cad,
                percentage=float(holding.get("percentage", 0)),
                currency=holding.get("currency", ""),
                current_price=float(holding.get("current_price", 0)),
            )
        )

    return AllocationResponse(items=items, total_value_cad=total_value)
