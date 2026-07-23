"""
HTTP server for ckg-agentforce — Streamable HTTP transport (Render/Smithery-compatible).
"""
from __future__ import annotations

import time
from collections import defaultdict

from .server import mcp

_STRIPE_LINK = "https://buy.stripe.com/00wbJ1gsYcm01tC52A1kA08"
_CAL_LINK = "https://cal.com/daniel-yarmoluk-sjmnub/30min"
_FREE_LIMIT = 50  # calls per IP per 24h before 402

_call_counts: dict = defaultdict(lambda: {"count": 0, "reset": time.time() + 86400})

_landing_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ckg-agentforce — Salesforce AgentForce Knowledge Graph</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 580px; margin: 48px auto; padding: 0 20px; color: #1a1a1a; line-height: 1.5; }
    h1 { font-size: 1.4rem; margin: 0 0 2px; }
    .sub { color: #666; font-size: 0.9em; margin: 0 0 20px; }
    .stats { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }
    .stat { background: #f0f4f8; border-radius: 6px; padding: 8px 14px; text-align: center; }
    .stat strong { display: block; font-size: 1.2rem; }
    .stat span { font-size: 0.75rem; color: #666; }
    .math { font-family: monospace; font-size: 0.85em; border-left: 3px solid #0f6e56; padding: 8px 14px; background: #f4f4f4; margin: 12px 0 20px; line-height: 1.8; }
    .audit { border: 1px solid #c8e6de; background: #f8fffe; border-radius: 6px; padding: 12px 16px; margin: 12px 0 20px; font-size: 0.88em; }
    .audit p { margin: 0 0 6px; }
    .audit ul { margin: 0; padding-left: 18px; }
    .audit li { margin-bottom: 2px; }
    .conf { background: #e6f4ef; color: #0f6e56; font-weight: 700; padding: 1px 8px; border-radius: 3px; font-size: 0.82em; }
    code { background: #f0f0f0; padding: 1px 5px; border-radius: 3px; font-size: 0.88em; }
    pre { background: #f4f4f4; padding: 12px; border-radius: 6px; font-size: 0.85em; overflow-x: auto; }
    .tools { font-size: 0.9em; padding-left: 18px; margin: 8px 0 16px; }
    .tools li { margin-bottom: 3px; }
    .btns { display: flex; gap: 10px; flex-wrap: wrap; margin: 12px 0 20px; }
    .btn-green { background: #0f6e56; color: white; padding: 10px 22px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 0.92em; }
    .btn-dark { background: #1a1a1a; color: white; padding: 10px 22px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 0.92em; }
    .footer { font-size: 0.82em; color: #888; margin-top: 8px; }
    .footer a { color: #0f6e56; }
    .badge { background: #0f6e56; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.72rem; font-weight: 600; }
    h2 { font-size: 0.95rem; margin: 20px 0 6px; text-transform: uppercase; letter-spacing: 0.04em; color: #444; }
  </style>
</head>
<body>
  <h1>ckg-agentforce <span class="badge">v0.2.6</span></h1>
  <p class="sub">Salesforce AgentForce · Compressed Knowledge Graph · MCP-native</p>

  <div class="stats">
    <div class="stat"><strong>40</strong><span>nodes</span></div>
    <div class="stat"><strong>0.471</strong><span>F1 vs RAG 0.123</span></div>
    <div class="stat"><strong>11×</strong><span>fewer tokens</span></div>
    <div class="stat"><strong>269</strong><span>tokens avg</span></div>
  </div>

  <div class="math">335 AgentForce queries<br>= 1,000,000 tokens · RAG<br>= &nbsp;&nbsp;90,000 tokens · RAG + CKG</div>

  <p style="font-size:0.9em;">AgentForce charges $2/autonomous resolution. Most failures come from agents not knowing the prerequisite chain. This graph declares those relationships explicitly — your agent traverses declared edges instead of inferring from docs.</p>

  <div class="audit">
    <p>Every edge SHA-256-pinned to a Salesforce source doc. The graph doesn't guess — it traverses. <span class="conf">GuardrailDecisionV1 · 13/13</span></p>
    <ul>
      <li><code>source_content_hash</code> computed at extraction time, before any query outcome</li>
      <li>Recomputable: <code>curl -s &lt;url&gt; | sha256sum</code></li>
      <li><code>verify_source()</code> fails closed on mismatch</li>
    </ul>
    <p style="margin:6px 0 0;color:#666;">Prior art: <a href="https://github.com/crewAIInc/crewAI/issues/4877">crewAI GuardrailProvider spec #4877</a></p>
  </div>

  <h2>Endpoint</h2>
  <pre>POST https://ckg-agentforce.onrender.com/mcp</pre>

  <h2>Tools</h2>
  <ul class="tools">
    <li><code>query_ckg(concept, depth)</code> — subgraph traversal</li>
    <li><code>get_prerequisites(concept)</code> — full upstream chain</li>
    <li><code>resolution_path()</code> — the $2/resolution billing chain</li>
    <li><code>search_concepts(query)</code> · <code>list_concepts()</code></li>
  </ul>

  <h2>Quick start</h2>
  <pre>pip install ckg-agentforce   # or: uvx ckg-agentforce</pre>

  <p style="font-size:0.85em;color:#666;">Free tier: 50 calls/day per IP.</p>

  <div class="btns">
    <a class="btn-green" href="https://buy.stripe.com/00wbJ1gsYcm01tC52A1kA08">Subscribe $29/mo →</a>
    <a class="btn-dark" href="https://cal.com/daniel-yarmoluk-sjmnub/30min">Book a call →</a>
  </div>

  <p class="footer">
    <a href="https://graphifymd.com/pro/">graphifymd.com/pro</a> ·
    <a href="https://github.com/Yarmoluk/ckg-agentforce">GitHub</a> ·
    <a href="https://github.com/Yarmoluk/ckg-benchmark/blob/main/paper/main.pdf">Benchmark paper</a>
  </p>
</body>
</html>"""


def _get_ip(request) -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    return forwarded.split(",")[0].strip() if forwarded else (request.client.host or "unknown")


def _check_rate_limit(ip: str) -> bool:
    now = time.time()
    state = _call_counts[ip]
    if now > state["reset"]:
        state["count"] = 0
        state["reset"] = now + 86400
    if state["count"] >= _FREE_LIMIT:
        return False
    state["count"] += 1
    return True


def main():
    import os
    import sys

    port = int(os.environ.get("PORT", 8000))
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])

    from starlette.applications import Starlette
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    from starlette.responses import HTMLResponse, JSONResponse
    from starlette.routing import Mount, Route
    import uvicorn

    class RateLimitMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            if request.url.path.startswith("/mcp"):
                ip = _get_ip(request)
                if not _check_rate_limit(ip):
                    return JSONResponse(
                        {
                            "error": "Free tier limit reached (50 calls/day).",
                            "subscribe_29_mo": _STRIPE_LINK,
                            "enterprise": _CAL_LINK,
                            "message": "Self-serve: $29/mo unlimited. Enterprise teams: book a 30-min call.",
                        },
                        status_code=402,
                    )
            return await call_next(request)

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
    app.add_middleware(RateLimitMiddleware)

    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
