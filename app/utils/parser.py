import re
from typing import List, Dict, Any


def extract_sources_from_text(text: str) -> List[Dict[str, str]]:
    """
    Extract sources cited or listed in the generated report or memos.
    Parses URLs, citations like [1] https://..., and returns structured objects.
    """
    sources = []
    seen_urls = set()

    # Match URLs directly
    url_pattern = r'https?://[^\s)\]"\'>]+'
    
    # Parse source lines if a Sources section exists
    if "## Sources" in text or "### Sources" in text:
        parts = re.split(r'#{2,3}\s*Sources', text)
        if len(parts) > 1:
            sources_block = parts[1]
            lines = sources_block.strip().split("\n")
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Line format often [1] URL or [1] Title - URL
                urls = re.findall(url_pattern, line)
                if urls:
                    url = urls[0].rstrip(".,;")
                    if url not in seen_urls:
                        seen_urls.add(url)
                        title = line.replace(url, "").strip(" []0123456789:-")
                        domain = url.split("//")[-1].split("/")[0]
                        sources.append({
                            "title": title if title else domain,
                            "url": url,
                            "domain": domain
                        })

    # Also search for any uncaptured URLs in the text
    for match in re.finditer(url_pattern, text):
        raw_url = match.group(0).rstrip(".,;)")
        if raw_url not in seen_urls:
            seen_urls.add(raw_url)
            domain = raw_url.split("//")[-1].split("/")[0]
            sources.append({
                "title": domain,
                "url": raw_url,
                "domain": domain
            })

    return sources
