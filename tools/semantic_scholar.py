import os
import time

import httpx

SS_API = "https://api.semanticscholar.org/graph/v1"
_FIELDS = "title,authors,year,venue,abstract,externalIds,openAccessPdf"
_TIMEOUT = 15


def _headers() -> dict:
    key = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
    return {"x-api-key": key} if key else {}


def _get_with_retry(url: str, params: dict, retries: int = 2) -> httpx.Response:
    for attempt in range(retries):
        response = httpx.get(url, params=params, headers=_headers(), timeout=_TIMEOUT)
        if response.status_code == 429:
            wait = 2 ** attempt
            time.sleep(wait)
            continue
        response.raise_for_status()
        return response
    response.raise_for_status()
    return response


def search_semantic_scholar_papers(query: str, max_results: int = 10) -> list[dict]:
    params = {
        "query": query,
        "limit": min(max(max_results, 1), 100),
        "fields": _FIELDS,
    }

    response = _get_with_retry(f"{SS_API}/paper/search", params)

    papers = []
    for paper in response.json().get("data", []):
        authors = [a.get("name", "") for a in paper.get("authors", [])]
        ext = paper.get("externalIds") or {}

        url = None
        if paper.get("openAccessPdf"):
            url = paper["openAccessPdf"].get("url")
        elif ext.get("DOI"):
            url = f"https://doi.org/{ext['DOI']}"
        elif ext.get("ArXiv"):
            url = f"https://arxiv.org/abs/{ext['ArXiv']}"

        abstract = paper.get("abstract") or ""
        papers.append({
            "title": paper.get("title", ""),
            "authors": authors,
            "year": paper.get("year"),
            "venue": paper.get("venue", ""),
            "abstract": abstract[:600] + "..." if len(abstract) > 600 else abstract,
            "doi": ext.get("DOI"),
            "url": url,
        })

    return papers
