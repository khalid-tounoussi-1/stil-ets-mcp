# STIL Lab MCP Server

MCP server for the [Software Technology and Intelligence Research Lab (STIL)](https://ouniali.github.io/) at ETS Montreal. Gives Claude direct access to lab knowledge and research paper search.

## Tools

| Tool | Description |
|---|---|
| `get_lab_overview` | Lab description, director, contact, research areas |
| `list_students` | List students filtered by role (`phd`/`master`) and status (`current`/`alumni`) |
| `get_student_info` | Detailed info for a student by name (partial match) |
| `list_publications` | STIL publications filtered by year, author, venue, or keyword |
| `get_research_topics` | Research topics and active projects |
| `search_arxiv` | Search ArXiv by keywords, with optional year filter |
| `search_semantic_scholar` | Search Semantic Scholar (covers ACM, IEEE, and more) |
| `find_related_work` | Cross-search ArXiv + Semantic Scholar for a research question |

## Setup

### 1. Install dependencies

```bash
uv sync
```

Or with pip:
```bash
pip install -e .
```

### 2. Add to Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "stil-lab": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/kadoud/Desktop/src/repos/stil-ets-mcp",
        "run",
        "python",
        "server.py"
      ]
    }
  }
}
```

### 3. Add to Claude Code (CLI)

```bash
claude mcp add stil-lab -- uv --directory /Users/kadoud/Desktop/src/repos/stil-ets-mcp run python server.py
```

Restart Claude Desktop after adding the config.

## Keeping data up to date

Lab data lives in `data/`. Edit these JSON files directly to add new students, publications, or projects:

- `data/students.json` — student profiles
- `data/publications.json` — lab publications
- `data/projects.json` — research projects
- `data/lab_info.json` — general lab info

## Development

```bash
# Run the server in dev mode (shows all tool calls)
uv run mcp dev server.py

# Test a specific tool
uv run python -c "
from tools.arxiv_search import search_arxiv_papers
import json
results = search_arxiv_papers('infrastructure as code technical debt', max_results=3)
print(json.dumps(results, indent=2))
"
```
