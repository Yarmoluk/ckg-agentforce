"""
HTTP server for ckg-agentforce — Streamable HTTP transport (Render/Smithery-compatible).
"""
from __future__ import annotations

from .server import mcp

_landing_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ckg-agentforce — Salesforce AgentForce Knowledge Graph</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 680px; margin: 60px auto; padding: 0 24px; color: #1a1a1a; }
    h1 { font-size: 1.6rem; margin-bottom: 4px; }
    .sub { color: #555; margin-bottom: 32px; }
    .stat { display: inline-block; background: #f0f4f8; border-radius: 6px; padding: 10px 18px; margin: 4px 4px 4px 0; }
    .stat strong { display: block; font-size: 1.3rem; }
    .stat span { font-size: 0.82rem; color: #666; }
    code { background: #f4f4f4; padding: 2px 6px; border-radius: 4px; font-size: 0.92em; }
    pre { background: #f4f4f4; padding: 16px; border-radius: 8px; overflow-x: auto; }
    a { color: #0f6e56; }
    .badge { display: inline-block; background: #0f6e56; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.78rem; font-weight: 600; }
  </style>
</head>
<body>
  <h1>ckg-agentforce</h1>
  <p class="sub">Compressed Knowledge Graph · Salesforce AgentForce · <span class="badge">v0.2.6</span></p>

  <div>
    <div class="stat"><strong>40</strong><span>nodes</span></div>
    <div class="stat"><strong>269</strong><span>tokens avg</span></div>
    <div class="stat"><strong>11×</strong><span>fewer tokens than RAG</span></div>
    <div class="stat"><strong>$2</strong><span>per resolution</span></div>
  </div>

  <h2>MCP endpoint</h2>
  <pre>POST https://ckg-agentforce.onrender.com/mcp</pre>

  <h2>Tools</h2>
  <ul>
    <li><code>list_concepts()</code> — all 40 AgentForce concepts</li>
    <li><code>search_concepts(query)</code> — keyword search</li>
    <li><code>query_ckg(concept, depth)</code> — subgraph traversal</li>
    <li><code>get_prerequisites(concept)</code> — full upstream chain</li>
    <li><code>resolution_path()</code> — the $2/resolution billing chain</li>
  </ul>

  <h2>Quick start</h2>
  <pre>pip install ckg-agentforce
# or via uvx:
uvx ckg-agentforce</pre>

  <p>
    <a href="https://graphifymd.com/pro/">graphifymd.com/pro</a> ·
    <a href="https://github.com/Yarmoluk/ckg-agentforce">GitHub</a> ·
    <a href="https://github.com/Yarmoluk/ckg-benchmark/blob/main/paper/main.pdf">Benchmark paper</a>
  </p>
</body>
</html>"""


def main():
    import sys

    port = 8000
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])

    from starlette.applications import Starlette
    from starlette.requests import Request
    from starlette.responses import HTMLResponse, JSONResponse
    from starlette.routing import Mount, Route
    import uvicorn

    async def homepage(request: Request):
        return HTMLResponse(_landing_html)

    async def server_card(request: Request):
        return JSONResponse({
            "name": "ckg-agentforce",
            "version": "0.2.6",
            "description": "40-node Compressed Knowledge Graph for Salesforce AgentForce",
            "tools": [
                "list_concepts", "search_concepts", "query_ckg",
                "get_prerequisites", "resolution_path",
            ],
            "prompts": ["show_burn", "map_agentforce_stack"],
            "resources": ["agentforce://nodes", "agentforce://resolution-chain"],
            "publisher": "Graphify.md",
            "publisher_url": "https://graphifymd.com",
        })

    mcp_app = mcp.streamable_http_app()

    app = Starlette(routes=[
        Route("/", homepage),
        Route("/.well-known/mcp/server-card.json", server_card),
        Mount("/mcp", app=mcp_app),
    ])

    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
