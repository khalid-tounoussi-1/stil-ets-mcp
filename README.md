# STIL Lab MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server for the **Software Technology and Intelligence Research Lab (STIL)** at [ETS Montreal](https://ouniali.github.io/). It gives any MCP-compatible AI client (Claude Desktop, Claude Code, etc.) direct access to lab knowledge and live academic paper search — without copy-pasting context manually.

---

## What it does

```
Claude Desktop / Claude Code / any MCP client
        │
        │  JSON-RPC over Streamable HTTP
        ▼
  https://your-server.railway.app/mcp
        │
        ├── Lab knowledge (students, publications, projects)
        ├── ArXiv API  — live paper search
        └── Semantic Scholar API  — covers ACM, IEEE, and more
```

Once connected, you can ask Claude things like:
- *"Who are the current PhD students at STIL and what are they working on?"*
- *"Find related work on Infrastructure-as-Code technical debt"*
- *"List STIL publications from 2025 on code review"*

---

## Available tools

| Tool | Description |
|---|---|
| `get_lab_overview` | Lab description, director contact, and research areas |
| `list_students` | List students filtered by role (`phd` / `master`) and status (`current` / `alumni`) |
| `get_student_info` | Detailed profile for any student — partial name match supported |
| `list_publications` | STIL publications, filterable by year, author, venue, or keyword |
| `get_research_topics` | Research areas and active projects |
| `search_arxiv` | Search ArXiv by keywords, with optional year filter |
| `search_semantic_scholar` | Search Semantic Scholar (covers ACM Digital Library, IEEE Xplore, and more) |
| `find_related_work` | Cross-search ArXiv + Semantic Scholar for a research question |

---

## Project structure

```
stil-ets-mcp/
├── server.py              # MCP server entry point — all tools defined here
├── Dockerfile             # Container image for hosted deployment
├── Procfile               # Start command for Railway / Heroku
├── pyproject.toml         # Python dependencies
├── tools/
│   ├── arxiv_search.py    # ArXiv API wrapper
│   ├── semantic_scholar.py # Semantic Scholar API wrapper
│   └── lab_knowledge.py   # Reads the data/ JSON files
└── data/
    ├── lab_info.json       # Lab name, director, research topics
    ├── students.json       # Student profiles
    ├── publications.json   # STIL publication list
    └── projects.json       # Active research projects
```

---

## Local setup

**Requirements:** Python 3.11+, [`uv`](https://docs.astral.sh/uv/getting-started/installation/)

```bash
git clone https://github.com/khalid-tounoussi-1/stil-ets-mcp.git
cd stil-ets-mcp
uv sync
```

Run in stdio mode (for Claude Code):
```bash
uv run python server.py
```

Run as an HTTP server:
```bash
MCP_TRANSPORT=streamable-http uv run python server.py
# → listening on http://localhost:8000/mcp
```

Inspect tools interactively:
```bash
uv run mcp dev server.py
```

---

## Deployment

### Railway (recommended)

1. Fork or push this repo to GitHub
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
3. Select this repo — Railway auto-detects the `Procfile`
4. Set the environment variable:
   ```
   MCP_TRANSPORT=streamable-http
   ```
   (`PORT` is injected automatically by Railway)
5. Deploy — your server URL will be `https://<project>.up.railway.app`

### Fly.io

```bash
fly launch        # auto-detects Dockerfile, creates fly.toml
fly secrets set MCP_TRANSPORT=streamable-http
fly deploy
```

### Docker (any VPS)

```bash
docker build -t stil-mcp .
docker run -p 8000:8000 -e MCP_TRANSPORT=streamable-http stil-mcp
```

---

## Connecting a client

**Claude Desktop** — edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "stil-lab": {
      "type": "streamable-http",
      "url": "https://<your-server>/mcp"
    }
  }
}
```

**Claude Code CLI:**

```bash
claude mcp add --transport streamable-http stil-lab https://<your-server>/mcp
```

Restart Claude Desktop after editing the config. Lab members only need the URL — no local install required.

---

## Keeping data up to date

Edit the JSON files in `data/` directly and redeploy:

| File | Contents |
|---|---|
| `data/lab_info.json` | Lab name, director contact, research topics, awards |
| `data/students.json` | Student profiles — name, role, year, research topic |
| `data/publications.json` | Publication list — title, authors, year, venue |
| `data/projects.json` | Active research projects with keywords and members |

---

## About STIL

The **Software Technology and Intelligence Research Lab** is led by [Prof. Ali Ouni](mailto:ali.ouni@etsmtl.ca) at ETS Montreal (École de technologie supérieure), University of Quebec. The lab works at the intersection of Artificial Intelligence and Software Engineering — focusing on software maintenance, refactoring, technical debt, Infrastructure-as-Code, and empirical SE.

→ [ouniali.github.io](https://ouniali.github.io/)
