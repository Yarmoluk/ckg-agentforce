# ckg-agentforce

**Salesforce AgentForce as a traversable knowledge graph — MCP-native, 40 nodes, $2/resolution billing path declared.**

The graph doesn't guess — it traverses.

---

## The problem

AgentForce charges **$2 per autonomous resolution**. Each resolution requires the agent to correctly traverse: Einstein Agent → Resolution Criteria → Audit Trail → Einstein Trust Layer → Policy Enforcement. Wrong inference = retry + CSAT impact + billing with no result.

Vector RAG over Salesforce docs retrieves ~2,982 tokens of chunks. The agent then *infers* what matters. Confident. Possibly wrong.

## The alternative

```
pip install ckg-agentforce
```

The CKG traverses 4 declared hops to the same answer: **269 tokens, auditable, source-traced to Salesforce developer docs.**

| | RAG | CKG |
|---|---|---|
| Tokens/query | 2,982 | 269 |
| Compression | — | **11×** |
| Answer quality (F1) | 0.123 | **0.471** |
| Traceability | model infers | declared edge |
| Resolution risk | confident, possibly wrong | auditable |

## Install

```bash
pip install ckg-agentforce
uvx ckg-agentforce          # run as MCP server
```

## Claude Desktop config

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

## What's covered (40 nodes)

**Platform core:** AgentForce Platform · Einstein Agent · Agent Topic · Agent Action · Agent Channel  
**Resolution path:** Resolution Criteria · Autonomous Resolution · Human Handoff · Conversation Turn  
**Trust & compliance:** Einstein Trust Layer · Audit Trail · Policy Enforcement · Data Masking · Toxicity Detection  
**Grounding:** Grounding · Semantic Retrieval · Knowledge Base · Document Retrieval · Metadata Filtering  
**Agent types:** Service Agent · Sales Agent · Marketing Agent · Commerce Agent · Field Service Agent  
**Actions:** Standard Action · Flow Action · Apex Action · Prompt Action · External Service Action · Custom Action  
**Data layer:** Data Cloud · Unified Data Model · Calculated Insight · Segment · Activation  
**Infrastructure:** Reasoning Engine · Model Selection · NVIDIA NIM · Context Window Management · Session State

## Tools (MCP)

| Tool | What it does |
|---|---|
| `list_concepts()` | All 40 AgentForce concepts |
| `search_concepts(query)` | Find by keyword — "resolution", "trust", "grounding", "NIM" |
| `query_ckg(concept, depth)` | Traverse prerequisites + dependents, with token comparison |
| `get_prerequisites(concept)` | Full ordered prerequisite chain |
| `resolution_path()` | The $2/resolution billing chain — what must be traversed correctly |

## The $2/resolution chain

```
resolution_path()
→ Einstein Agent [AGENT]
    requires: AgentForce Platform · Reasoning Engine · Einstein Trust Layer
→ Resolution Criteria [BILLING]
    requires: Einstein Agent
→ Autonomous Resolution [BILLING]
    requires: Resolution Criteria · Audit Trail
→ Audit Trail [SECURITY]
→ Policy Enforcement [SECURITY]
    requires: Einstein Trust Layer
→ Einstein Trust Layer [SECURITY]

BEFORE (RAG): 2,982 tokens — model infers resolution requirements
AFTER  (CKG): 269 tokens, 4 hops — declared, auditable, source-traced
```

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

## Enterprise stack

97 domains across NVIDIA, finance, regulatory, and enterprise AI:  
**[graphifymd.com/pro](https://graphifymd.com/pro/)** — $99/mo

---

**Graphify.md** · patent pending · [graphifymd.com](https://graphifymd.com)
