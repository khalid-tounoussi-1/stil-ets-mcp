import xml.etree.ElementTree as ET
from urllib.parse import urlencode

import httpx

ARXIV_API = "https://export.arxiv.org/api/query"
_NS = {"atom": "http://www.w3.org/2005/Atom"}


def search_arxiv_papers(
    query: str,
    max_results: int = 10,
    year_from: int | None = None,
) -> list[dict]:
    params = urlencode({
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": min(max(max_results, 1), 50),
        "sortBy": "relevance",
        "sortOrder": "descending",
    })

    response = httpx.get(f"{ARXIV_API}?{params}", timeout=30)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    papers = []

    for entry in root.findall("atom:entry", _NS):
        published = entry.findtext("atom:published", "", _NS)[:10]
        year = int(published[:4]) if published else None

        if year_from and year and year < year_from:
            continue

        title = (entry.findtext("atom:title", "", _NS) or "").strip().replace("\n", " ")
        summary = (entry.findtext("atom:summary", "", _NS) or "").strip().replace("\n", " ")
        authors = [
            a.findtext("atom:name", "", _NS)
            for a in entry.findall("atom:author", _NS)
        ]
        arxiv_id = (entry.findtext("atom:id", "", _NS) or "").split("/abs/")[-1]

        papers.append({
            "title": title,
            "authors": authors,
            "year": year,
            "published": published,
            "abstract": summary[:600] + "..." if len(summary) > 600 else summary,
            "arxiv_id": arxiv_id,
            "url": f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else None,
        })

    return papers
