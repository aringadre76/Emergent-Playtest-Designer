"""Main FastAPI application."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
from ..core.config import Config
from ..core.orchestrator import PlaytestOrchestrator
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("Starting Emergent Playtest Designer API")
    
    config = Config.from_env()
    app.state.orchestrator = PlaytestOrchestrator(config)
    
    yield
    
    logger.info("Shutting down Emergent Playtest Designer API")


app = FastAPI(
    title="Emergent Playtest Designer",
    description="AI-powered automated testing system for discovering game exploits",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Emergent Playtest Designer API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        orchestrator = app.state.orchestrator
        stats = orchestrator.get_statistics()
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
