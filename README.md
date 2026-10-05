<div align="center">

# DeepResearch: Multi-Agent AI Research Assistant

An autonomous, multi-perspective AI research system built with **LangGraph**, **Google Gemini**, **Tavily Search**, and **FastAPI**.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.1+-000000?style=flat)](https://github.com/langchain-ai/langgraph)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

</div>

---

## Overview

**DeepResearch** simulates a collaborative, multi-analyst research team. Instead of generating shallow one-shot answers, it decomposes any complex inquiry into diverse specialist perspectives, retrieves real-time knowledge via Tavily and Wikipedia, interviews simulated domain experts, drafts comprehensive analytical memos, and consolidates findings into a publication-ready executive report with cited sources.

---

## Research Workflow Architecture

```
User Query ("Impact of AI Agents on Software Engineering")
  │
  ▼
FastAPI Server (Endpoints & Validation)
  │
  ▼
LangGraph Multi-Analyst Workflow
  │
  ├── 1. Persona Generation (Planner)
  │      └── Creates diverse AI Analyst personas (e.g., Lead Architect, Security Auditor, DevOps Specialist)
  │
  ├── 2. Parallel Expert Interviews (LangGraph Send API)
  │      ├── Analyst 1 ──> [Tavily Web Search + Wikipedia] ──> Expert Interview ──> Analytical Memo
  │      ├── Analyst 2 ──> [Tavily Web Search + Wikipedia] ──> Expert Interview ──> Analytical Memo
  │      └── Analyst 3 ──> [Tavily Web Search + Wikipedia] ──> Expert Interview ──> Analytical Memo
  │
  ├── 3. Synthesis & Report Assembly
  │      ├── Introduction & Title Generation
  │      ├── Cross-Memo Insight Consolidation
  │      └── Conclusion & Source Deduplication
  │
  ▼
Structured Response & Clean Web UI
  ├── Executive Summary & Key Findings
  ├── Publication-Grade Markdown Report
  ├── Interactive Analyst Profiles
  └── Cited Sources with Domain Previews & One-Click Markdown Export
```

---

## Features

- **Multi-Perspective Analytical Planning**: Deconstructs questions across varied viewpoints and motives to avoid confirmation bias.
- **Parallel Sub-Graph Interviews**: Uses LangGraph's dynamic `Send()` API to conduct concurrent interactive interviews between analysts and an expert grounded in retrieved context.
- **Hybrid Retrieval Engine**: Combines **Tavily Web Search** for current information with **Wikipedia** for fundamental encyclopedic grounding.
- **Source Deduplication & Citations**: Tracks citation brackets `[1]`, `[2]` throughout memos and generates consolidated source lists with domain cards.
- **Enterprise-Grade FastAPI Backend**: Structured Pydantic v2 validation, comprehensive error handling, and clean asynchronous endpoints.
- **Modern Dark AI Web Interface**: Built with responsive vanilla HTML/CSS/JS (no Node.js build step needed), featuring real-time stage progress, tabbed sections, and copy/download controls.
- **Vercel Serverless Ready**: Zero-config deployment with modern `vercel.json` and ASGI serverless entrypoint.

---

## Tech Stack

- **Backend**: FastAPI, Pydantic v2, Uvicorn
- **Agent Orchestration**: LangGraph, LangChain Core
- **LLM**: Google Gemini (`ChatGoogleGenerativeAI` via `gemini-2.5-flash` or configurable)
- **Retrieval Tools**: Tavily AI Search API, Wikipedia Loader
- **Frontend**: Responsive Dark UI, Marked.js, Plus Jakarta Sans & JetBrains Mono typography
- **Testing**: Pytest, FastAPI TestClient, Mocking

---

## Project Structure

```
AI-Research-Agent/
│
├── api/
│   └── index.py            # Vercel serverless ASGI entrypoint
│
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI application initialization & static routing
│   ├── config.py           # Pydantic BaseSettings configuration
│   │
│   ├── api/                # API router & Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── schemas.py
│   │
│   ├── agents/             # Modular agent node definitions
│   │   ├── __init__.py
│   │   ├── planner.py      # Generates analyst personas
│   │   ├── interviewer.py  # Conducts expert Q&A with web retrieval
│   │   └── writer.py       # Drafts memos and synthesizes final report
│   │
│   ├── graph/              # LangGraph state & workflow construction
│   │   ├── __init__.py
│   │   ├── state.py        # TypedDict & Pydantic state definitions
│   │   └── workflow.py     # StateGraph configuration and compiled graphs
│   │
│   ├── tools/              # Retrieval tools (Tavily, Wikipedia)
│   │   ├── __init__.py
│   │   └── search.py
│   │
│   ├── services/           # Core services (Gemini LLM factory)
│   │   ├── __init__.py
│   │   └── llm.py
│   │
│   ├── utils/              # Parsers & string formatting utilities
│   │   ├── __init__.py
│   │   └── parser.py
│   │
│   └── static/             # Frontend single-page application
│       └── index.html
│
├── notebooks/              # Reference prototype
│   ├── research_agent_original.ipynb
│   └── 18research_assistant.py
│
├── tests/                  # Test suite
│   ├── __init__.py
│   └── test_api.py
│
├── reports/                # Output storage (.gitkeep)
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── requirements.txt        # Production Python dependencies
├── vercel.json             # Vercel deployment configuration
└── README.md
```

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/KeshavBatla/AI-Research-Agent.git
cd AI-Research-Agent
```

### 2. Set Up Python Virtual Environment (Windows)

```powershell
python -m venv .venv
.venv\Scripts\activate
```

*(On macOS/Linux: `source .venv/bin/activate`)*

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create your `.env` file by copying the template:

```powershell
copy .env.example .env
```

Edit `.env` with your API keys:

```env
# Required for reasoning and report synthesis
GEMINI_API_KEY=your_gemini_api_key_here

# Required for real-time web retrieval
TAVILY_API_KEY=your_tavily_api_key_here

# Optional configuration
MODEL_NAME=gemini-2.5-flash
APP_ENV=development
DEBUG=True
PORT=8000
HOST=0.0.0.0
```

> **API Key Resources:**
> - Get a Google Gemini API key: [Google AI Studio](https://aistudio.google.com/)
> - Get a Tavily API key: [Tavily AI Search](https://tavily.com/)

---

## Running Locally

Start the FastAPI application with Uvicorn:

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open your browser and navigate to:
- **Interactive Web Interface**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## API Reference

### Health Check

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "llm_configured": true,
  "tavily_configured": true
}
```

### Run Research

```http
POST /api/research
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "Recent breakthroughs in solid-state battery commercialization",
  "max_analysts": 3,
  "human_feedback": "approve"
}
```

**Response Body:**
```json
{
  "query": "Recent breakthroughs in solid-state battery commercialization",
  "title": "Solid-State Batteries: Commercialization Milestones and Challenges",
  "introduction": "An executive analysis of next-generation electrolyte technologies...",
  "summary": "Key insights across material chemistry, manufacturing scale, and automotive validation...",
  "key_findings": [
    "Sulfide-based solid electrolytes demonstrate superior conductivity.",
    "Major OEMs targeting initial pilot fleet integration by 2027."
  ],
  "conclusion": "Commercial viability hinges on resolving interfacial resistance and cost-effective roll-to-roll manufacturing.",
  "final_report": "# Solid-State Batteries...\n\n...",
  "analysts": [
    {
      "name": "Dr. Sarah Chen",
      "role": "Materials Science Fellow",
      "affiliation": "Battery Innovation Labs",
      "description": "Focuses on solid electrolyte stability and dendrite suppression."
    }
  ],
  "sources": [
    {
      "title": "Nature Energy - Solid-State Battery Review",
      "url": "https://nature.com/articles/example",
      "domain": "nature.com"
    }
  ],
  "sections": ["## Materials Science Analysis\n..."]
}
```

---

## Testing

Run the automated test suite with `pytest`:

```powershell
pytest -v
```

The tests cover:
- Health check endpoint verification
- Frontend static asset serving
- Input validation (empty query, minimum length)
- Markdown source citation extraction
- Error propagation on missing configuration
- End-to-end mocked LangGraph state graph execution

---

## Vercel Deployment

This project is optimized for direct deployment to Vercel:

1. Push your repository to GitHub: `https://github.com/KeshavBatla/AI-Research-Agent`
2. Log into [Vercel](https://vercel.com) and click **"Add New Project"**.
3. Import the `AI-Research-Agent` repository.
4. In the **Environment Variables** section, configure:
   - `GEMINI_API_KEY`: Your Gemini API key
   - `TAVILY_API_KEY`: Your Tavily API key
   - `MODEL_NAME`: `gemini-2.5-flash`
5. Click **Deploy**. Vercel will automatically build the ASGI serverless function and route all traffic via `vercel.json`.

---

## Future Improvements

- [ ] **Streaming SSE Output**: Stream individual interview turns and drafting tokens directly to the frontend.
- [ ] **Export to PDF**: Generate styled PDF reports with executive cover pages.
- [ ] **Custom Knowledge Upload**: Enable users to upload private PDF documents alongside web search.
- [ ] **Human-in-the-Loop Approval UI**: Add an interactive checkpoint in the UI allowing users to refine the generated analyst personas before interviews begin.

---

## License

MIT License. Developed for research and technical exploration.
