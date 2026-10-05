import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure the project root is on sys.path so `app.*` imports resolve on Vercel
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import get_settings
from app.api.schemas import (
    ResearchRequest,
    ResearchResponse,
    HealthResponse,
    AnalystModel,
    SourceModel,
)
from app.api.routes import router as api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# FastAPI app — no prefix here.
# Vercel routes /api/(.*) to this function, stripping the /api prefix,
# so routes like /health and /research must be registered at the root level.
app = FastAPI(
    title="DeepResearch AI Agent API",
    description="Multi-analyst research agent powered by LangGraph, Gemini, Tavily, and Wikipedia.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the router at root — Vercel strips /api before handing off
app.include_router(api_router)
