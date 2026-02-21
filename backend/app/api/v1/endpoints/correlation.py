from fastapi import APIRouter, HTTPException
from app.api.v1.schemas.common import CorrelationMatrix
from app.services.external_api import get_holdings_dataframe, load_performance
from app.services.correlation_service import (
    calculate_portfolio_correlation,
    correlation_matrix_to_json,
)

router = APIRouter(prefix="/correlation", tags=["correlation"])


@router.get("/matrix", response_model=CorrelationMatrix)
async def get_correlation_matrix():
    """Get the correlation matrix for portfolio assets."""
    holdings_df = await get_holdings_dataframe()
    performance_df = await load_performance()

    if holdings_df.empty or performance_df.empty:
        raise HTTPException(
            status_code=503, detail="Unable to fetch data for correlation calculation"
        )

    corr_matrix, _, weighted_corr = calculate_portfolio_correlation(
        holdings_df, performance_df
    )

    if corr_matrix is None:
        raise HTTPException(
            status_code=400,
            detail="Insufficient data to calculate correlation matrix. Need at least 2 symbols with 30+ days of common data.",
        )

    # Convert to JSON format with lower triangle mask
    matrix_json = correlation_matrix_to_json(corr_matrix)

    return CorrelationMatrix(
        symbols=matrix_json["symbols"],
        values=matrix_json["values"],
        weighted_correlation=weighted_corr or 0.0,
    )
