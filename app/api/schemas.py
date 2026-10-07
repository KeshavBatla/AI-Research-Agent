from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    """Input payload for initiating a research workflow."""
    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="The research topic or question to investigate.",
        examples=["Impact of AI agents on modern software engineering"]
    )
    max_analysts: Optional[int] = Field(
        default=2,
        ge=1,
        le=5,
        description="Number of analyst personas to generate and interview."
    )
    human_feedback: Optional[str] = Field(
        default="approve",
        description="Optional editorial direction for persona generation."
    )


class AnalystModel(BaseModel):
    """Structured representation of an analyst persona."""
    name: str
    role: str
    affiliation: str
    description: str


class SourceModel(BaseModel):
    """Source reference cited in the research report."""
    title: str
    url: str
    domain: str


class ResearchResponse(BaseModel):
    """Structured output returned by the research agent."""
    query: str
    title: str
    introduction: str
    summary: str
    key_findings: List[str]
    conclusion: str
    final_report: str
    analysts: List[AnalystModel]
    sources: List[SourceModel]
    sections: List[str]


class HealthResponse(BaseModel):
    """API health status check."""
    status: str
    version: str
    llm_configured: bool
    tavily_configured: bool
