"""
SourceSage FastAPI Application
Main entry point for the REST API server.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from api.routes import router
from database.connection import db_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    print("🚀 Starting SourceSage API...")
    
    # Connect to MongoDB
    await db_manager.connect()
    
    # Create downloads directory if it doesn't exist
    os.makedirs("downloads", exist_ok=True)
    
    print("✅ SourceSage API ready!")
    print("📖 Docs: http://localhost:8000/docs")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down SourceSage API...")
    await db_manager.disconnect()
    print("👋 Goodbye!")


# Create FastAPI app
app = FastAPI(
    title="SourceSage API",
    description="AI-powered assistant for finding and analyzing GitHub 'good first issues'",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# CORS Configuration (Fixed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ Allow ALL origins for dev (easiest)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routes
app.include_router(router)


# Health check at root
@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": "SourceSage API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/health",
            "search": "/api/search-issues",
            "analyze": "/api/analyze",
            "download": "/api/download/{filename}",
            "websocket": "/api/ws"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run server
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
