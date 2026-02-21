from fastapi import APIRouter, HTTPException
from app.api.v1.schemas.common import BenchmarkData
from app.services.external_api import load_performance, get_portfolio_metrics
from app.services.benchmark_service import calculate_normalized_benchmark_data

router = APIRouter(prefix="/benchmark", tags=["benchmark"])


@router.get("/comparison", response_model=BenchmarkData)
async def get_benchmark_comparison():
    """Get normalized benchmark comparison data (Portfolio vs QQQ vs VOO)."""
    performance_df = await load_performance()
    metrics = await get_portfolio_metrics()

    if performance_df.empty or metrics is None:
        raise HTTPException(
            status_code=503, detail="Unable to fetch data for benchmark comparison"
        )

    data = calculate_normalized_benchmark_data(performance_df, metrics)

    if data is None:
        raise HTTPException(
            status_code=400,
            detail="Unable to calculate benchmark comparison. Ensure QQQ and VOO are in the performance data.",
        )

    return BenchmarkData(
        dates=data["dates"],
        portfolio=data["portfolio"],
        qqq=data["qqq"],
        voo=data["voo"],
    )
