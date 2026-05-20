import os

import uvicorn
from mcp.server.fastmcp import FastMCP

from tools.arxiv_search import search_arxiv_papers
from tools.lab_knowledge import (
    get_lab_overview_data,
    get_projects_data,
    get_publications_data,
    get_students_data,
)
from tools.semantic_scholar import search_semantic_scholar_papers

def _transport_security() -> dict | None:
    # DNS rebinding protection only makes sense for localhost servers.
    # Disable it when running as a public hosted server.
    if os.getenv("MCP_TRANSPORT") == "streamable-http":
        return {"enable_dns_rebinding_protection": False}
    return None

mcp = FastMCP("STIL Lab Assistant", transport_security=_transport_security())


# ---------------------------------------------------------------------------
# Lab knowledge tools
# ---------------------------------------------------------------------------


@mcp.tool()
def get_lab_overview() -> str:
    """Get an overview of the STIL lab: description, research areas, director, and contact info."""
    d = get_lab_overview_data()
    director = d["director"]
    lines = [
        f"# {d['name']}",
        f"**Institution**: {d['institution']}",
        f"**Director**: {director['name']} — {director['title']}",
        f"**Email**: {director['email']} | **Phone**: {director['phone']}",
        f"**Website**: {d['website']}",
        f"**Location**: {d['location']}",
        "",
        "## Description",
        d["description"],
        "",
        "## Research Topics",
        *[f"- {t}" for t in d["research_topics"]],
        "",
        "## Awards",
        *[f"- {a}" for a in d["awards"]],
    ]
    return "\n".join(lines)


@mcp.tool()
def list_students(role: str = "all", status: str = "current") -> str:
    """
    List students in the STIL lab.

    Args:
        role: Filter by role — "phd", "master", "intern", or "all"
        status: Filter by status — "current", "alumni", or "all"
    """
    students = get_students_data()
    role_l, status_l = role.lower(), status.lower()

    filtered = [
        s for s in students
        if (role_l == "all" or s.get("role", "").lower() == role_l)
        and (status_l == "all" or s.get("status", "").lower() == status_l)
    ]

    if not filtered:
        return f"No students found for role='{role}' and status='{status}'."

    lines = [f"## STIL Students ({len(filtered)} found)\n"]
    for s in filtered:
        end = s.get("year_end") or "present"
        co = f", co-supervised with {s['co_supervisor']}" if s.get("co_supervisor") else ""
        topic = f"\n  Research: {s['research_topic']}" if s.get("research_topic") else ""
        pos = f"\n  Current position: {s['current_position']}" if s.get("current_position") else ""
        lines.append(
            f"- **{s['name']}** [{s['role'].upper()}, {s['year_start'] or '?'}–{end}{co}]"
            f"{topic}{pos}"
        )

    return "\n".join(lines)


@mcp.tool()
def get_student_info(name: str) -> str:
    """
    Get detailed information about a specific student by name (partial match supported).

    Args:
        name: Student name or partial name to search for
    """
    students = get_students_data()
    matches = [s for s in students if name.lower() in s["name"].lower()]

    if not matches:
        return f"No student found matching '{name}'."

    blocks = []
    for s in matches:
        end = s.get("year_end") or "present"
        lines = [
            f"## {s['name']}",
            f"**Role**: {s['role'].upper()}",
            f"**Status**: {s['status'].title()}",
            f"**Period**: {s['year_start'] or '?'}–{end}",
        ]
        if s.get("co_supervisor"):
            lines.append(f"**Co-supervisor**: {s['co_supervisor']}")
        if s.get("research_topic"):
            lines.append(f"**Research Topic**: {s['research_topic']}")
        if s.get("thesis_title"):
            lines.append(f"**Thesis**: {s['thesis_title']}")
        if s.get("current_position"):
            lines.append(f"**Current Position**: {s['current_position']}")
        blocks.append("\n".join(lines))

    return "\n\n---\n\n".join(blocks)


@mcp.tool()
def list_publications(
    year: int | None = None,
    author: str | None = None,
    venue: str | None = None,
    keyword: str | None = None,
) -> str:
    """
    List STIL lab publications with optional filters.

    Args:
        year: Filter by publication year
        author: Filter by author name (partial match)
        venue: Filter by venue/journal name (partial match)
        keyword: Filter by keyword in title
    """
    pubs = get_publications_data()

    if year:
        pubs = [p for p in pubs if p.get("year") == year]
    if author:
        pubs = [p for p in pubs if any(author.lower() in a.lower() for a in p.get("authors", []))]
    if venue:
        pubs = [p for p in pubs if venue.lower() in p.get("venue", "").lower()]
    if keyword:
        kw = keyword.lower()
        pubs = [p for p in pubs if kw in p.get("title", "").lower()]

    if not pubs:
        return "No publications found matching the given filters."

    pubs.sort(key=lambda p: p.get("year") or 0, reverse=True)

    lines = [f"## STIL Publications ({len(pubs)} found)\n"]
    for p in pubs:
        authors = ", ".join(p.get("authors", []))
        year_s = str(p.get("year", "N/A"))
        pub_type = f" [{p['type']}]" if p.get("type") else ""
        lines.append(f"**{p['title']}**")
        lines.append(f"  {authors} ({year_s}) — {p.get('venue', '')}{pub_type}")
        if p.get("url"):
            lines.append(f"  {p['url']}")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
def get_research_topics() -> str:
    """Get the main research topics and active projects of the STIL lab."""
    data = get_lab_overview_data()
    projects = get_projects_data()

    lines = ["## STIL Research Topics\n"]
    for t in data["research_topics"]:
        lines.append(f"- **{t}**")

    if projects:
        lines.append("\n## Active Research Projects\n")
        for p in projects:
            lines.append(f"### {p['name']}")
            lines.append(p.get("description", ""))
            if p.get("keywords"):
                lines.append(f"*Keywords*: {', '.join(p['keywords'])}")
            if p.get("members"):
                lines.append(f"*Members*: {', '.join(p['members'])}")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# External paper search tools
# ---------------------------------------------------------------------------


@mcp.tool()
def search_arxiv(query: str, max_results: int = 10, year_from: int | None = None) -> str:
    """
    Search ArXiv for research papers.

    Args:
        query: Search query — keywords, author name, or topic
        max_results: Maximum number of results to return (1–50)
        year_from: Only return papers published from this year onwards
    """
    papers = search_arxiv_papers(query, max_results=max_results, year_from=year_from)

    if not papers:
        return f"No papers found on ArXiv for query: '{query}'"

    lines = [f"## ArXiv Results for '{query}' ({len(papers)} papers)\n"]
    for i, p in enumerate(papers, 1):
        authors = ", ".join(p.get("authors", [])[:4])
        if len(p.get("authors", [])) > 4:
            authors += " et al."
        lines.append(f"### {i}. {p['title']}")
        lines.append(f"**Authors**: {authors}")
        lines.append(f"**Published**: {p.get('published', 'N/A')}")
        if p.get("abstract"):
            lines.append(f"**Abstract**: {p['abstract']}")
        if p.get("url"):
            lines.append(f"**URL**: {p['url']}")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
def search_semantic_scholar(query: str, max_results: int = 10) -> str:
    """
    Search Semantic Scholar for research papers (covers ACM Digital Library, IEEE Xplore, and more).

    Args:
        query: Search query — keywords, topic, or research question
        max_results: Maximum number of results to return (1–100)
    """
    try:
        papers = search_semantic_scholar_papers(query, max_results=max_results)
    except Exception as e:
        return (
            f"Semantic Scholar search failed for '{query}': {e}\n\n"
            "This is usually caused by API rate limiting. "
            "Set the SEMANTIC_SCHOLAR_API_KEY environment variable to increase limits."
        )

    if not papers:
        return f"No papers found on Semantic Scholar for query: '{query}'"

    lines = [f"## Semantic Scholar Results for '{query}' ({len(papers)} papers)\n"]
    for i, p in enumerate(papers, 1):
        authors = ", ".join(p.get("authors", [])[:4])
        if len(p.get("authors", [])) > 4:
            authors += " et al."
        year = p.get("year", "N/A")
        venue = p.get("venue", "")
        lines.append(f"### {i}. {p['title']}")
        lines.append(f"**Authors**: {authors}")
        lines.append(f"**Year**: {year}" + (f" | **Venue**: {venue}" if venue else ""))
        if p.get("abstract"):
            lines.append(f"**Abstract**: {p['abstract']}")
        if p.get("url"):
            lines.append(f"**URL**: {p['url']}")
        elif p.get("doi"):
            lines.append(f"**DOI**: https://doi.org/{p['doi']}")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
def find_related_work(research_question: str, max_results_per_source: int = 5) -> str:
    """
    Find related work by searching both ArXiv and Semantic Scholar simultaneously.

    Args:
        research_question: The research question or topic to find related work for
        max_results_per_source: Number of results per source (default 5)
    """
    arxiv_papers = search_arxiv_papers(research_question, max_results=max_results_per_source)
    try:
        ss_papers = search_semantic_scholar_papers(research_question, max_results=max_results_per_source)
    except Exception:
        ss_papers = []

    lines = [f"## Related Work for: '{research_question}'\n"]

    lines.append(f"### ArXiv ({len(arxiv_papers)} papers)\n")
    for i, p in enumerate(arxiv_papers, 1):
        authors = ", ".join(p.get("authors", [])[:3])
        if len(p.get("authors", [])) > 3:
            authors += " et al."
        year = (p.get("published") or "")[:4] or "N/A"
        lines.append(f"{i}. **{p['title']}**")
        lines.append(f"   {authors} ({year})")
        if p.get("url"):
            lines.append(f"   {p['url']}")
        lines.append("")

    lines.append(f"### Semantic Scholar ({len(ss_papers)} papers)\n")
    for i, p in enumerate(ss_papers, 1):
        authors = ", ".join(p.get("authors", [])[:3])
        if len(p.get("authors", [])) > 3:
            authors += " et al."
        year = p.get("year", "N/A")
        venue = f", {p['venue']}" if p.get("venue") else ""
        lines.append(f"{i}. **{p['title']}**")
        lines.append(f"   {authors} ({year}{venue})")
        if p.get("url"):
            lines.append(f"   {p['url']}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        uvicorn.run(
            mcp.streamable_http_app(),
            host="0.0.0.0",
            port=int(os.getenv("PORT", "8000")),
            log_level="info",
        )
    else:
        mcp.run()


if __name__ == "__main__":
    main()
