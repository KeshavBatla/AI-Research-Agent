import os
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import get_settings
from app.api.routes import router as api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("deepresearch")

settings = get_settings()

app = FastAPI(
    title="DeepResearch AI Agent API",
    description="Multi-analyst research agent powered by LangGraph, Gemini, Tavily, and Wikipedia.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes at /api/* (for local development with uvicorn)
app.include_router(api_router, prefix="/api")

# Serve the frontend HTML at root — check both public/ and app/static/
PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"
STATIC_DIR = Path(__file__).resolve().parent / "static"

FRONTEND_DIR = PUBLIC_DIR if PUBLIC_DIR.exists() else (STATIC_DIR if STATIC_DIR.exists() else None)

if FRONTEND_DIR is not None:
    if (FRONTEND_DIR / "index.html").exists():
        @app.get("/", include_in_schema=False)
        async def serve_index():
            return FileResponse(FRONTEND_DIR / "index.html")
