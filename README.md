# ckg-agentforce

**Salesforce AgentForce as a traversable knowledge graph.**  
40 nodes · 5 tools · 2 resources · 1 resource template · 2 prompts · MCP-native

AgentForce charges **$2 per autonomous resolution**. Every resolution requires the agent to correctly traverse: Einstein Agent → Resolution Criteria → Audit Trail → Einstein Trust Layer → Policy Enforcement. Wrong inference means retry, CSAT impact, and a $2 charge with no result.

Vector RAG retrieves ~2,982 tokens of Salesforce docs. The agent infers what matters. Confident. Possibly wrong.

This graph declares what the agent should already know.

```
pip install ckg-agentforce
uvx ckg-agentforce          # run as MCP server
```

---

## Knowledge Graph — 40 nodes

```
                        AgentForce Platform
                        ╱       │        ╲
              Einstein Agent  Data Cloud  Model Selection
             ╱    │    │    ╲      │            │
    Agent Topic   │  Grounding  Salesforce   Reasoning Engine
         │        │     │       CRM        ╱    │    ╲
   Agent Action  Resolution  Knowledge   NVIDIA  Token  Context
   ╱  ╱  ╱  ╲   Criteria    Base        NIM    Budget  Window
  Flow Apex Mul. Ext.   ╲
  Act. Act. Act. Act.   Autonomous Resolution ←── Audit Trail
                            ($2 / event)               │
                                │              Einstein Trust Layer
                           Agent Metrics       ╱   │     │    ╲
                           Handoff to     Data   Zero  Policy  Compliance
                             Human       Masking  DR   Enforce  Rules
```

**Node taxonomy (40 total)**

| Type | Count | Key concepts |
|---|---|---|
| CAPABILITY | 7 | Flow · Apex · External · MuleSoft · Standard · Custom Actions · Grounding |
| COMPLIANCE | 4 | Audit Trail · Zero Data Retention · Policy Enforcement · Compliance Rules |
| AGENT | 4 | Einstein Agent · Service Agent · Sales Agent · Marketing Agent |
| CONCEPT | 3 | Agent Topic · Resolution Criteria · Conversation State |
| WORKFLOW | 3 | Handoff to Human · Omni-Channel Routing · Multi-Agent Orchestration |
| CONFIG | 3 | Agent Instruction · Token Budget · Model Selection |
| SECURITY | 2 | Einstein Trust Layer · Data Masking |
| MECHANISM | 2 | Grounding · Retrieval Augmented Generation |
| PLATFORM | 2 | AgentForce Platform · Data Cloud |
| ARTIFACT | 2 | Knowledge Base · Prompt Template |
| Other | 8 | BILLING · ALGORITHM · DATASOURCE · ENGINE · RUNTIME · MONITORING · CONSTRAINT · TOOL |

---

## Install

```bash
pip install ckg-agentforce
```

Requires Python ≥ 3.10 · `mcp >= 1.0.0`

---

## Setup

### Claude Desktop

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

### Claude Code CLI

```bash
claude mcp add agentforce uvx ckg-agentforce
```

### Cursor / Windsurf

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

### Verify

```
list_concepts()
resolution_path()
query_ckg('Autonomous Resolution', 4)
```

---

## Tools

### `list_concepts()`
All 40 AgentForce concepts, grouped by type.

```
ckg-agentforce — 40 concepts:
  AgentForce Platform   [PLATFORM]
  Einstein Agent        [AGENT]
  Einstein Trust Layer  [SECURITY]
  Autonomous Resolution [BILLING]
  ...
```

### `search_concepts(query)`
Find concepts by keyword.

```python
search_concepts("resolution")   # → Resolution Criteria · Autonomous Resolution
search_concepts("trust")        # → Einstein Trust Layer · Zero Data Retention
search_concepts("action")       # → all 7 action types
```

### `query_ckg(concept, depth=3)`
Traverse any concept — prerequisites upstream, dependents downstream. Every relationship traces to a declared Salesforce doc.

```python
query_ckg('Autonomous Resolution', 4)
```

```
## Autonomous Resolution  ·  AgentForce CKG
Type: BILLING · Depth: 4 hops

Prerequisites
  - [REQUIRES:1.00] Resolution Criteria     (CONCEPT)
  - [REQUIRES:1.00] Audit Trail             (COMPLIANCE)
    - [REQUIRES:1.00] Einstein Trust Layer  (SECURITY)
      - [REQUIRES:1.00] AgentForce Platform (PLATFORM)
      - [REQUIRES:1.00] Reasoning Engine    (ENGINE)

Builds toward
  - [REQUIRES:0.95] Handoff to Human  (WORKFLOW)
  - [REQUIRES:0.90] Agent Metrics     (MONITORING)

This traversal: ~269 tokens · RAG equivalent: ~2,982 tokens · 11× compression
```

### `get_prerequisites(concept)`
Full ordered upstream chain.

```python
get_prerequisites('Custom Actions')
# → AgentForce Platform → Agent Topic → Agent Action → Apex Action → Custom Actions
```

### `resolution_path()`
The exact $2/resolution billing traversal — every hop declared.

```
Einstein Agent [AGENT]
  requires: AgentForce Platform · Reasoning Engine · Einstein Trust Layer

Resolution Criteria [CONCEPT]
  requires: Einstein Agent

Autonomous Resolution [BILLING]
  requires: Resolution Criteria · Audit Trail

Audit Trail [COMPLIANCE]
  requires: Einstein Trust Layer

Policy Enforcement [COMPLIANCE]
  requires: Einstein Trust Layer

Einstein Trust Layer [SECURITY]
  requires: AgentForce Platform

---
BEFORE (RAG): 2,982 tokens · model infers · confident, possibly wrong
AFTER  (CKG):  269 tokens · 4 declared hops · auditable by design
```

---

## Resources

Two static resources readable by any MCP client.

| URI | Contents |
|---|---|
| `agentforce://nodes` | All 40 concepts grouped by taxonomy type |
| `agentforce://resolution-chain` | The $2/resolution billing path with declared edges |

---

## Resource Templates

Parameterized access to any concept in the graph.

| Template | Returns |
|---|---|
| `agentforce://concept/{concept}` | Prerequisites + dependents for any named concept |

**Example:** read `agentforce://concept/Einstein Trust Layer`

```
# Einstein Trust Layer  [SECURITY]

## Prerequisites (1)
  - AgentForce Platform

## Dependents (6)
  - Data Masking · Audit Trail · Zero Data Retention
  - Grounding · Einstein Agent · Policy Enforcement
```

---

## Prompts

### `show_burn`
Walks the resolution path and renders a before/after: RAG 2,982 tokens vs CKG 269 tokens, with the exact hop path.

Steps it runs: `resolution_path()` → `query_ckg('Autonomous Resolution', 4)` → `query_ckg('Einstein Trust Layer', 3)`

### `map_agentforce_stack`
Maps the full platform from Einstein Agent to billing, then renders an interactive D3.js force-directed graph.

Node colors: AGENT=teal · SECURITY=red · BILLING=amber · CAPABILITY=blue · PLATFORM=slate

---

## Benchmark

| Metric | RAG | GraphRAG | **CKG** |
|---|---|---|---|
| F1 | 0.123 | 0.120 | **0.471** |
| Tokens / query | 2,982 | — | **269** |
| Traceability | model infers | partial | **declared edge** |

v0.6.2 · 7,928 queries · 45 domains  
Dataset: [huggingface.co/datasets/danyarm/ckg-benchmark](https://huggingface.co/datasets/danyarm/ckg-benchmark)  
Paper: [github.com/Yarmoluk/ckg-benchmark/blob/main/paper/main.pdf](https://github.com/Yarmoluk/ckg-benchmark/blob/main/paper/main.pdf)

---

## Enterprise stack

97 domains across NVIDIA, finance, regulatory, and enterprise AI. Remote MCP connector — no install, paste one URL into claude.ai or Cursor.

[graphifymd.com/pro/](https://graphifymd.com/pro/) — $99/mo

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

Graphify.md · patent pending · [graphifymd.com](https://graphifymd.com)
