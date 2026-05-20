FROM python:3.11-slim

LABEL io.modelcontextprotocol.server.name="io.github.khalid-tounoussi-1/stil-ets-mcp"

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

ENV MCP_TRANSPORT=streamable-http
ENV PORT=8000

EXPOSE 8000

CMD ["uv", "run", "python", "server.py"]
