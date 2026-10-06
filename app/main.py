import os
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import get_settings
from app.api.routes import router as api_router

class VercelRewriteMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope["headers"])
            if b"x-vercel-original-url" in headers:
                original_url = headers[b"x-vercel-original-url"].decode("utf-8")
                if "?" in original_url:
                    path, query = original_url.split("?", 1)
                else:
                    path = original_url
                    query = ""
                scope["path"] = path
                scope["query_string"] = query.encode("utf-8")
        await self.app(scope, receive, send)


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

# Register API routes
app.include_router(api_router, prefix="/api")

# Static files directory
STATIC_DIR = Path(__file__).resolve().parent / "static"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(STATIC_DIR / "index.html")
else:
    @app.get("/")
    async def root():
        return {
            "message": "DeepResearch API is online. Static UI folder not found.",
            "docs": "/docs",
        }

app = VercelRewriteMiddleware(app)