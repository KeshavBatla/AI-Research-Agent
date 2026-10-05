import logging
import re
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status
from app.api.schemas import (
    ResearchRequest,
    ResearchResponse,
    HealthResponse,
    AnalystModel,
    SourceModel,
)
from app.config import get_settings
from app.graph.workflow import build_research_graph
from app.utils.parser import extract_sources_from_text

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Verify application health and API configuration status."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        llm_configured=bool(settings.GEMINI_API_KEY),
        tavily_configured=bool(settings.TAVILY_API_KEY),
    )


@router.post("/research", response_model=ResearchResponse, tags=["Research"])
async def run_research(request: ResearchRequest):
    """
    Execute end-to-end multi-analyst research graph:
    1. Generates analyst personas
    2. Conducts parallel expert interviews with web & Wikipedia retrieval
    3. Writes individual analytical memos
    4. Synthesizes executive introduction, insights, and conclusion
    5. Returns structured report and references
    """
    settings = get_settings()
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GEMINI_API_KEY is not configured on the server. Please set it in your environment or .env file.",
        )

    try:
        logger.info(f"Initiating research on topic: {request.query}")
        graph = build_research_graph(with_interrupt=False)

        initial_state = {
            "topic": request.query,
            "max_analysts": request.max_analysts or settings.DEFAULT_MAX_ANALYSTS,
            "human_analyst_feedback": request.human_feedback or "approve",
            "analysts": [],
            "sections": [],
            "introduction": "",
            "content": "",
            "conclusion": "",
            "final_report": "",
        }

        # Run graph execution
        result = await graph.ainvoke(initial_state)

        # Extract title from introduction (# Title)
        intro_text = result.get("introduction", "")
        title_match = re.search(r"^#\s+(.+)$", intro_text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else f"Research: {request.query}"

        # Clean intro text to remove standalone title header if needed
        clean_intro = intro_text
        if title_match:
            clean_intro = intro_text.replace(title_match.group(0), "").strip()

        # Parse analyst personas
        analyst_objs = [
            AnalystModel(
                name=a.name,
                role=a.role,
                affiliation=a.affiliation,
                description=a.description,
            )
            for a in result.get("analysts", [])
        ]

        # Extract sources from report and sections
        final_report = result.get("final_report", "")
        raw_sources = extract_sources_from_text(final_report)
        sources = [
            SourceModel(
                title=s.get("title", s.get("domain", "")),
                url=s.get("url", ""),
                domain=s.get("domain", ""),
            )
            for s in raw_sources
        ]

        # Extract key findings from memos or content
        key_findings = []
        content_text = result.get("content", "")
        bullet_points = re.findall(r"^[*-]\s+(.+)$", content_text, re.MULTILINE)
        if bullet_points:
            key_findings = [bp.strip() for bp in bullet_points[:6]]
        else:
            # Fallback to analyst memo summary sentences
            for sec in result.get("sections", []):
                for line in sec.split("\n"):
                    if line.strip().startswith("-") or line.strip().startswith("*"):
                        key_findings.append(line.strip().lstrip("*- "))
                        if len(key_findings) >= 5:
                            break

        return ResearchResponse(
            query=request.query,
            title=title,
            introduction=clean_intro,
            summary=result.get("content", ""),
            key_findings=key_findings,
            conclusion=result.get("conclusion", ""),
            final_report=final_report,
            analysts=analyst_objs,
            sources=sources,
            sections=result.get("sections", []),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error during research execution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Research agent execution failed: {str(e)}",
        )
