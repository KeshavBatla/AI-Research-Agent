import logging
from typing import List, Dict, Any
from langchain_community.document_loaders import WikipediaLoader
from langchain_tavily import TavilySearch
from app.config import get_settings

logger = logging.getLogger(__name__)


def search_tavily(query: str, max_results: int = 3) -> str:
    """Execute search using Tavily API and format results into XML-tagged docs."""
    settings = get_settings()
    if not settings.TAVILY_API_KEY:
        logger.warning("TAVILY_API_KEY is not set. Web search will return empty context.")
        return ""

    try:
        tavily_search = TavilySearch(max_results=max_results, tavily_api_key=settings.TAVILY_API_KEY)
        data = tavily_search.invoke({"query": query})
        search_docs = data.get("results", data) if isinstance(data, dict) else data

        if not search_docs:
            return ""

        formatted_search_docs = "\n\n---\n\n".join(
            [
                f'<Document href="{doc.get("url", "")}"/>\n{doc.get("content", "")}\n</Document>'
                for doc in search_docs
                if isinstance(doc, dict)
            ]
        )
        return formatted_search_docs
    except Exception as e:
        logger.error(f"Error executing Tavily search for query '{query}': {e}")
        return ""


def search_wikipedia_docs(query: str, max_docs: int = 2) -> str:
    """Execute search using Wikipedia loader and format results into XML-tagged docs."""
    try:
        search_docs = WikipediaLoader(query=query, load_max_docs=max_docs).load()
        if not search_docs:
            return ""

        formatted_search_docs = "\n\n---\n\n".join(
            [
                f'<Document source="{doc.metadata.get("source", "")}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
                for doc in search_docs
            ]
        )
        return formatted_search_docs
    except Exception as e:
        logger.error(f"Error executing Wikipedia search for query '{query}': {e}")
        return ""
