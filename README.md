# STIL Lab MCP Server

MCP server for the [Software Technology and Intelligence Research Lab (STIL)](https://ouniali.github.io/) at ETS Montreal. Gives Claude direct access to lab knowledge and live research paper search.

## Tools

| Tool | Description |
|---|---|
| `get_lab_overview` | Lab description, director, contact, research areas |
| `list_students` | List students by role (`phd`/`master`) and status (`current`/`alumni`) |
| `get_student_info` | Lookup any student by partial name |
| `list_publications` | STIL publications, filterable by year/author/venue/keyword |
| `get_research_topics` | Research areas and active projects |
| `search_arxiv` | Live ArXiv search with optional year filter |
| `search_semantic_scholar` | Live search covering ACM, IEEE, and more |
| `find_related_work` | Cross-searches ArXiv + Semantic Scholar for a research question |

---

## How it works

```
Claude Desktop / Claude Code / any MCP client
        │
        │  JSON-RPC over HTTP (Streamable HTTP transport)
        ▼
  https://your-server.railway.app/mcp
        │
        ├── reads data/ JSON files (students, publications, projects)
        ├── calls arxiv.org API
        └── calls semanticscholar.org API
```

The server exposes a single endpoint: `POST /mcp` (and `GET /mcp` for SSE streaming).  
Clients authenticate with `Authorization: Bearer <token>`.

---

## Deployment

### Option A — Railway (recommended, free tier)

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
3. Select this repo — Railway auto-detects the `Procfile`
4. In **Variables**, set:
   ```
   MCP_AUTH_TOKEN=<generate a strong random token>
   ```
   (`PORT` is set automatically by Railway)
5. Deploy. Your server URL will be `https://<project>.up.railway.app`

### Option B — Fly.io

```bash
fly launch          # auto-detects Dockerfile, creates fly.toml
fly secrets set MCP_AUTH_TOKEN=<your-token>
fly deploy
```

### Option C — Docker (any VPS)

```bash
docker build -t stil-mcp .
docker run -p 8000:8000 \
  -e MCP_AUTH_TOKEN=<your-token> \
  stil-mcp
```

---

## Connecting clients to the hosted server

Once deployed, add to Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`):

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

For Claude Code CLI:
```bash
claude mcp add --transport streamable-http stil-lab https://<your-server>/mcp
```

Share the URL with lab members — they each add this one config line, no local install needed.

---

## Local development

```bash
# Install deps
uv sync

# Run locally (stdio mode, for Claude Code)
uv run python server.py

# Run locally as HTTP server
MCP_TRANSPORT=streamable-http uv run python server.py

# Dev mode with MCP inspector
uv run mcp dev server.py
```

---

## Updating lab data

Edit the JSON files in `data/` directly, then redeploy:

| File | What it contains |
|---|---|
| `data/students.json` | Student profiles, roles, research topics |
| `data/publications.json` | Lab publication list |
| `data/projects.json` | Active research projects |
| `data/lab_info.json` | General lab info, director contact |
