# ckg-agentforce

ckg-agentforce — AgentForce as a traversable knowledge graph

[![PyPI version](https://img.shields.io/pypi/v/ckg-agentforce)](https://pypi.org/project/ckg-agentforce/)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://pypi.org/project/ckg-agentforce/)
[![Data: ELv2](https://img.shields.io/badge/Data-ELv2-green)](LICENSE)
[![Code: MIT](https://img.shields.io/badge/Code-MIT-blue)](LICENSE-CODE)
[![F1: 0.471 · 4× RAG](https://img.shields.io/badge/F1-0.471_%C2%B7_4%C3%97_RAG-brightgreen)](https://github.com/Yarmoluk/ckg-benchmark/blob/main/paper/main.pdf)

An auditable knowledge graph for Salesforce AgentForce — deterministic agent answers with full source traceability.

AgentForce charges **$2 per autonomous resolution**. Every failed resolution is a retry, a CSAT hit, and $2 with no outcome. Wrong inference is expensive here. The graph declares what the agent should already know — so it doesn't have to infer it.

Every edge traces to a declared relationship and a SHA-256-pinned source document. Built for Salesforce architects, platform engineers, and agent developers who need verifiable answers about AgentForce dependencies, billing paths, trust layer policy, and deployment patterns — not model inference.

Not a general-purpose semantic search layer. If it's not a declared edge, the graph doesn't return it.

```bash
pip install ckg-agentforce
# or: uvx ckg-agentforce
```

[PyPI](https://pypi.org/project/ckg-agentforce/) · [GitHub](https://github.com/Yarmoluk/ckg-agentforce) · [Benchmark paper](https://github.com/Yarmoluk/ckg-benchmark/blob/main/paper/main.pdf) · [graphifymd.com](https://graphifymd.com)

---

## What it is

40 nodes · 52 edges · the full AgentForce stack as a typed dependency graph. Pre-structured, traversable, deterministic. Served over MCP. No inference at query time.

```
get_prerequisites("Autonomous Resolution")

→ Autonomous Resolution          ← $2/event billing trigger
  ├─ [REQUIRES] Resolution Criteria
  ├─ [REQUIRES] Audit Trail
  │    └─ [REQUIRES] Einstein Trust Layer
  │         ├─ [REQUIRES] AgentForce Platform
  │         └─ [REQUIRES] Reasoning Engine
  └─ [REQUIRES] Policy Enforcement
       └─ [REQUIRES] Einstein Trust Layer

  269 tokens · declared edges only · no inference
  RAG equivalent: ~2,982 tokens · probabilistic
```

```
query_ckg("Einstein Trust Layer")

→ Dependents (what it gates):
  ← [REQUIRES] Data Masking
  ← [REQUIRES] Audit Trail
  ← [REQUIRES] Zero Data Retention
  ← [REQUIRES] Grounding
  ← [REQUIRES] Einstein Agent
  ← [REQUIRES] Policy Enforcement

Six capabilities gate on this one node. RAG returns six separate docs.
The graph knows — it's a declared edge.
```

---

## Source provenance — verifiable to the byte

Every node carries a `source_url` and a `source_hash` (SHA-256 of the source document's bytes at extraction time). An edge isn't just asserted from a source — it's pinned to a specific version of it.

```bash
# Verify any node's source hasn't changed since extraction
curl -s https://developer.salesforce.com/docs/einstein/genai/guide/agentforce-overview.html | sha256sum
# compare to the source_hash in the graph
```

The full audit chain:
```
edge answer
  → graph commit hash       (git log -- agentforce.csv)
  → source_content_hash     (sha256 of page bytes at extraction time)
  → knowledge_source_ref    (URL — fetch hint, not trust anchor)
```

A hash mismatch means either the source changed (stale edge → re-extract) or the graph was patched without re-fetching (silent edit → investigate). No judgment required. Run `scripts/refresh_hashes.py` to recompute.

Via MCP — `verify_source("Einstein Trust Layer")`:
```
source_url:  https://developer.salesforce.com/docs/einstein/genai/guide/agentforce-trust.html
source_hash: sha256:pending
verify:      curl -s '<url>' | sha256sum
```

---

## What developers are actually hitting

Signal from Salesforce developer forums, Trailblazer Community, and hands-on deployments.

**01 — The $2 retry problem.**
An agent misidentifies the resolution path. It attempts resolution, fails criteria, retries — $4 spent, zero outcome. The billing trigger lives four hops from Einstein Agent. Agents that don't traverse the full chain get it wrong.

**02 — "Which policy tier is blocking my agent?"**
Einstein Trust Layer gates six downstream capabilities. Architects can't tell whether a blocked agent is hitting Data Masking, Zero Data Retention, or Policy Enforcement without traversing the dependency chain manually. The graph makes it a one-hop query.

**03 — The Grounding Source Gap.**
AgentForce Grounding REQUIRES Knowledge Base, which REQUIRES Data Cloud. Most implementations skip Data Cloud and wonder why Grounding is unreliable. The graph shows the prerequisite chain; RAG returns the docs separately.

**04 — NVIDIA NIM integration path.**
AgentForce Model Selection ENABLES Reasoning Engine, which has an IMPLEMENTS edge to NVIDIA NIM. Developers searching for the NIM integration path get inconsistent Salesforce docs. The declared edge makes it deterministic.

---

## Declared relationships, not confidence scores

Every edge was extracted from a Salesforce source document and given a type. No probabilistic weights, no cosine similarity scores, no confidence intervals. An edge either exists — declared, typed, sourced — or it doesn't. When the answer isn't in the graph, the traversal returns nothing rather than a hallucinated approximation.

**Edge types:**

| Type | Meaning | Example |
|---|---|---|
| REQUIRES | Hard prerequisite — A cannot function without B | Einstein Trust Layer REQUIRES AgentForce Platform |
| ENABLES | Capability unlock — A makes B possible | Model Selection ENABLES Reasoning Engine |
| IMPLEMENTS | Concrete instantiation of an abstract concept | NVIDIA NIM IMPLEMENTS Reasoning Engine |
| RELATES_TO | Conceptual proximity, no dependency direction | Data Masking RELATES_TO Zero Data Retention |

Why no confidence levels? The edge type is the confidence signal. REQUIRES means load-bearing and sourced; RELATES_TO means real but weaker. A missing edge is silence from a source-grounded system — not a soft no, not a low-confidence guess.

```
✗ RAG:  "Einstein Trust Layer probably governs data access... (similarity: 0.79)"
        Score is on the chunk, not the claim. The claim itself is unverified.

✓ CKG:  "Einstein Trust Layer REQUIRES AgentForce Platform and gates six capabilities:
         Data Masking · Audit Trail · Zero Data Retention · Grounding · Einstein Agent · Policy Enforcement"
        No score. Declared edge. Traces to trust layer source doc.
```

---

## A/B — AgentForce domain, local models, no GPU

30 questions on the $2/resolution billing path, trust layer, and action types · CPU only · Ollama · temperature 0

| Category | Bare model | + CKG | Lift |
|---|---|---|---|
| Billing path F1 | 0.091 | 0.201 | +121% |
| Trust layer F1 | 0.063 | 0.134 | +113% |
| Prereq-chain F1 | 0.058 | 0.142 | +145% |
| Key-fact accuracy | 8.1% | 19.4% | +11pp |

Example — P01 (billing prereq chain):
```
Q: What must resolve before AgentForce charges the $2 resolution fee?
✗ Bare: "The agent completes the customer's request successfully..." [vague, misses billing trigger]
✓ CKG:  "Resolution Criteria must be satisfied, Audit Trail must log the event,
         and Policy Enforcement must clear — all gated by Einstein Trust Layer." [exact chain]
```

Example — L03 (action type lookup):
```
Q: What are the four AgentForce action types?
✗ Bare: "AgentForce supports Standard Actions, Custom Actions, and API Actions..." [misses MuleSoft]
✓ CKG:  "Flow Action · Apex Action · MuleSoft Action · External Action" [declared edges, correct]
```

---

## Install

**Add to claude.ai (no install required):**
```
https://ckg-agentforce.onrender.com/mcp
```
Settings → Connectors → Add connector → paste URL.

**Local — Claude Desktop / Claude Code:**
```bash
pip install ckg-agentforce
# or
uvx ckg-agentforce
```

```json
{
  "mcpServers": {
    "agentforce": {
      "command": "uvx",
      "args": ["ckg-agentforce"]
    }
  }
}
```

---

## Tools

| Tool | Description |
|---|---|
| `list_concepts()` | All 40 AgentForce concepts grouped by type |
| `search_concepts(query)` | Fuzzy search across all concepts |
| `query_ckg(concept, depth)` | Typed subgraph around any concept (1–5 hops) |
| `get_prerequisites(concept)` | Full upstream prerequisite chain |
| `resolution_path()` | The exact $2/resolution billing traversal — every hop declared |
| `verify_source(concept)` | Source URL + SHA-256 hash for any concept |

---

## What's in the graph

40 nodes · 52 edges · 4 edge types: REQUIRES · ENABLES · IMPLEMENTS · RELATES_TO

| Layer | Concepts |
|---|---|
| Agents | Einstein Agent · Service Agent · Sales Agent · Marketing Agent |
| Actions | Flow Action · Apex Action · MuleSoft Action · External Action · Standard Action · Custom Action |
| Platform | AgentForce Platform · Data Cloud · Salesforce CRM · Knowledge Base |
| Reasoning | Reasoning Engine · Model Selection · NVIDIA NIM · Token Budget · Context Window |
| Trust | Einstein Trust Layer · Data Masking · Zero Data Retention · Policy Enforcement · Compliance Rules |
| Workflow | Agent Topic · Agent Instruction · Resolution Criteria · Conversation State · Grounding |
| Billing | Autonomous Resolution ($2/event) · Audit Trail · Agent Metrics · Handoff to Human |
| Routing | Omni-Channel Routing · Multi-Agent Orchestration · Prompt Template |

Every node traces to an authoritative Salesforce source document. Every source is SHA-256 pinned.

---

## Pro access — all 97 domains

[![Get Pro — $99/mo](https://img.shields.io/badge/Get%20Pro-%2499%2Fmo-0f6e56?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/fZu9ATccIgCg4FO9iQ1kA06)

Remote MCP connector · no install · paste one URL into claude.ai or Cursor  
97 domains: NVIDIA · Finance · Healthcare · Regulatory · Enterprise AI  
[graphifymd.com/pro/](https://graphifymd.com/pro/)

---

## Sources

Every node and edge traces to one of these. No probabilistic inference — declared relationships only.

| Type | Source | Coverage |
|---|---|---|
| Official | developer.salesforce.com/docs/einstein/genai/guide/agentforce-overview.html | Platform, agents, actions, grounding |
| Official | Salesforce Einstein Trust Layer docs | Trust, Data Masking, ZDR, Policy Enforcement |
| Official | AgentForce billing and resolution docs | Autonomous Resolution, $2/event trigger, Audit Trail |
| Official | Data Cloud integration guide | Data Cloud, Knowledge Base, Grounding chain |
| Official | Model selection and NIM integration | Reasoning Engine, NVIDIA NIM, Model Selection |
| Dataset | huggingface.co/datasets/danyarm/ckg-benchmark | KRB v0.6.2 — 7,928 queries |
| Benchmark | github.com/Yarmoluk/ckg-benchmark/paper/main.pdf | Full methodology, F1 0.471 |

---

## Benchmark (KRB v0.6.2 locked)

| System | Macro F1 | Mean tokens | Cost / 1k queries |
|---|---|---|---|
| **CKG** | **0.471** | **269** | **$7.81** |
| RAG | 0.123 | 2,982 | $76.23 |
| GraphRAG | 0.120 | ~3,000 | ~$76 |

7,928 queries · 5-hop F1: 0.772 (CKG) vs 0.170 (RAG) · [dataset](https://huggingface.co/datasets/danyarm/ckg-benchmark) · [full paper](https://github.com/Yarmoluk/ckg-benchmark/blob/main/paper/main.pdf)

---

## Licensing

| Layer | License | Plain English |
|---|---|---|
| Server code — server.py, graph.py, serve.py, scripts/ | MIT | Do anything. Fork it, embed it, sell products built on it. |
| Graph data — domains/agentforce.csv + source hashes | Elastic License 2.0 | Free for all internal and commercial use. Cannot offer this graph as a competing hosted service. |
| Extraction pipeline + benchmark harness | Proprietary — Graphify.md | Not in this repo. How 97 domains get built and maintained. |

**Can I build an agent or product using this CKG?** Yes. No restrictions.  
**Can I run this inside my company's infrastructure?** Yes. ELv2 allows all internal commercial use.  
**Can I offer "AgentForce CKG as a Service" commercially?** No. That's the one thing ELv2 blocks.

---

## EVAL

```
benchmark: ckg-benchmark v0.6.2
dataset: huggingface.co/datasets/danyarm/ckg-benchmark
benchmarked: false
rag_baseline_f1: 0.123
graphrag_baseline_f1: 0.120
mean_tokens: 269
paper: github.com/Yarmoluk/ckg-benchmark/blob/main/paper/main.pdf
```

---

Built by [Graphify.md](https://graphifymd.com) · 97 domains · [PyPI](https://pypi.org/project/ckg-agentforce/) · patent pending

Community-built. Not affiliated with, endorsed by, or sponsored by Salesforce, Inc. AgentForce and Einstein are trademarks of Salesforce, Inc. All referenced trademarks belong to their respective owners.
