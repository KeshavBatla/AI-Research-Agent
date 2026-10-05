import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.graph.state import Analyst, Perspectives
from app.utils.parser import extract_sources_from_text

client = TestClient(app)


def test_health_endpoint():
    """Verify GET /api/health returns 200 and schema."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "llm_configured" in data
    assert "tavily_configured" in data


def test_frontend_serving():
    """Verify GET / serves HTML landing page."""
    response = client.get("/")
    assert response.status_code == 200
    assert "DeepResearch" in response.text
    assert "<!DOCTYPE html>" in response.text


def test_research_validation_empty_query():
    """Verify POST /api/research rejects invalid/empty queries with 422."""
    response = client.post("/api/research", json={"query": ""})
    assert response.status_code == 422


def test_research_validation_short_query():
    """Verify POST /api/research rejects queries under 3 characters."""
    response = client.post("/api/research", json={"query": "ai"})
    assert response.status_code == 422


def test_parser_extract_sources():
    """Test utility parser with markdown citations."""
    sample_text = """
    # Research Report
    Quantum computing shows promise [1].
    
    ## Sources
    [1] IBM Quantum Computing - https://quantum-computing.ibm.com
    [2] Nature Physics - https://www.nature.com/articles/s41567
    """
    sources = extract_sources_from_text(sample_text)
    assert len(sources) >= 2
    urls = [s["url"] for s in sources]
    assert "https://quantum-computing.ibm.com" in urls
    assert "https://www.nature.com/articles/s41567" in urls


@patch("app.api.routes.get_settings")
def test_research_missing_api_key(mock_get_settings):
    """Verify POST /api/research raises 500 if GEMINI_API_KEY is not configured."""
    mock_settings = MagicMock()
    mock_settings.GEMINI_API_KEY = None
    mock_get_settings.return_value = mock_settings

    response = client.post("/api/research", json={"query": "Test Topic for AI"})
    assert response.status_code == 500
    assert "GEMINI_API_KEY is not configured" in response.json()["detail"]


@patch("app.api.routes.get_settings")
@patch("app.api.routes.build_research_graph")
def test_research_execution_flow(mock_build_graph, mock_get_settings):
    """Test full endpoint flow with mocked LangGraph execution."""
    mock_settings = MagicMock()
    mock_settings.GEMINI_API_KEY = "dummy-key"
    mock_settings.DEFAULT_MAX_ANALYSTS = 2
    mock_get_settings.return_value = mock_settings

    mock_graph = MagicMock()
    
    async def fake_ainvoke(state):
        return {
            "topic": state["topic"],
            "introduction": "# Autonomous AI in Healthcare\n\n## Introduction\nAutonomous AI is advancing healthcare diagnostics.",
            "content": "## Insights\n- Breakthrough diagnostic speed.\n- Multi-modal imaging models.",
            "conclusion": "## Conclusion\nIn summary, transformative clinical adoption is accelerating.",
            "final_report": "# Autonomous AI in Healthcare\n\n## Introduction\nAutonomous AI...\n\n---\n\nBreakthrough diagnostic speed.\n\n---\n\n## Conclusion\nIn summary...\n\n## Sources\n[1] Nature Medicine - https://nature.com/articles/123",
            "analysts": [
                Analyst(
                    name="Dr. Elena Vance",
                    role="Clinical AI Lead",
                    affiliation="Stanford Medicine",
                    description="Expert in real-world clinical AI deployments."
                )
            ],
            "sections": ["## Clinical Perspective\nDetails on medical imaging."]
        }

    mock_graph.ainvoke = fake_ainvoke
    mock_build_graph.return_value = mock_graph

    response = client.post(
        "/api/research",
        json={"query": "Autonomous AI in Healthcare", "max_analysts": 1}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Autonomous AI in Healthcare"
    assert len(data["analysts"]) == 1
    assert data["analysts"][0]["name"] == "Dr. Elena Vance"
    assert len(data["sources"]) >= 1
    assert data["sources"][0]["domain"] == "nature.com"
