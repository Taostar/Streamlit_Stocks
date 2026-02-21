from fastapi import APIRouter
from app.api.v1.endpoints import portfolio, holdings, correlation, exchange, benchmark, performance

api_router = APIRouter()

api_router.include_router(portfolio.router)
api_router.include_router(holdings.router)
api_router.include_router(correlation.router)
api_router.include_router(exchange.router)
api_router.include_router(benchmark.router)
api_router.include_router(performance.router)
