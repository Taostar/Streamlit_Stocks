from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api.v1.router import api_router
from app.api.v1.schemas.common import HealthResponse

settings = get_settings()

app = FastAPI(
    title="Portfolio Dashboard API",
    description="FastAPI backend for Portfolio Dashboard",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok")


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Portfolio Dashboard API",
        "docs": "/docs",
        "health": "/health",
    }
