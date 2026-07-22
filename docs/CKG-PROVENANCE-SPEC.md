# CKG Source Provenance Specification
**Version:** 1.0.0  
**Status:** Stable  
**Maintained by:** Graphify.md  
**Reference implementations:** ckg-agentforce · ckg-nvidia-ai · ckg-nvidia-nemoclaw

---

## Overview

Every Compact Knowledge Graph (CKG) must carry verifiable source provenance per node. This closes the audit chain from a declared edge answer all the way back to the exact bytes of the source document at extraction time.

No probabilistic inference means nothing to an auditor unless every declared edge traces to a pinned source. This spec defines that pin.

---

## The Audit Chain

```
edge answer
  → graph commit hash       (git log -- <domain>.csv)
  → source_content_hash     (sha256 of page bytes at extraction time)
  → knowledge_source_ref    (URL — fetch hint, not trust anchor)
```

- **graph commit hash** — when was this edge written, by whom, what changed
- **source_content_hash** — the document said this at extraction time; mismatch is deterministic
- **knowledge_source_ref** — where to fetch the source; the page may have changed since extraction

---

## Per-Node Provenance Fields

Required in all CKG domain CSVs and graph data:

| Field | Type | Description |
|---|---|---|
| `SourceURL` | string | Fetch hint — where the node came from. Not a trust anchor; the page can change. |
| `source_content_hash` | string | Trust anchor. `sha256:<64-char hex>` — SHA-256 of the source document's bytes at extraction time. Mismatch = stale edge or silent upstream edit. |

### CSV column format

```
ConceptID,ConceptLabel,Dependencies,TaxonomyID,SourceURL,source_content_hash
1,AgentForce Platform,,PLATFORM,https://help.salesforce.com/...,sha256:cc11eedeee761e...
```

---

## What Each Field Proves

| Field | Proves | Does NOT prove |
|---|---|---|
| `SourceURL` | Where the node came from | That the source still says the same thing |
| `source_content_hash` | The node was declared from specific content at a specific moment | That the source is still live or correct today |

The hash requires no publisher cooperation. Mismatch is deterministic — no judgment required.

---

## Verification Command

For any node:

```bash
curl -s <SourceURL> | sha256sum
# compare to source_content_hash
# mismatch → stale edge or upstream edit → mark stale: true, re-extract
```

---

## Stale Edge Policy

1. Re-fetch source URL
2. Compare hash: `curl -s <url> | sha256sum`
3. If mismatch:
   - Mark edge `stale: true` in the CSV
   - Do not silently serve a stale edge
   - Flag for re-extraction with updated `source_content_hash`
4. If URL returns 404:
   - Mark edge `stale: true`
   - Locate the moved or archived version
   - Update both `SourceURL` and `source_content_hash` together

---

## MCP Server — Required Tool

Every MCP server that serves a CKG must expose a `verify_source` tool:

```python
@mcp.tool()
def verify_source(concept: str) -> str:
    """Return the source URL and content hash for a concept node.
    Caller can verify: curl -s <source_url> | sha256sum == source_hash"""
    id_to_label, label_to_id, _, _, _, provenance = load_graph(DOMAIN)
    cid = find_concept(label_to_id, concept)
    prov = provenance.get(cid, {})
    return {
        "concept": id_to_label[cid],
        "source_url": prov["source_url"],
        "source_hash": prov["source_hash"],
        "verify": f"curl -s '{prov['source_url']}' | sha256sum",
    }
```

**Tool signature (required):**
- Input: `concept: str`
- Output: `{ concept, source_url, source_hash, verify }`
- Returns the bash verification command as a string in the `verify` field

---

## Hash Refresh Script

Run before publishing any CKG update:

```python
# scripts/refresh_hashes.py
import hashlib, httpx, csv, sys
from pathlib import Path

def refresh(csv_path: str):
    rows = list(csv.DictReader(open(csv_path)))
    for row in rows:
        url = row.get("SourceURL", "").strip()
        if not url:
            continue
        try:
            content = httpx.get(url, timeout=30, follow_redirects=True).content
            row["source_content_hash"] = "sha256:" + hashlib.sha256(content).hexdigest()
        except Exception as e:
            print(f"  WARN: {row['ConceptLabel']} — {e}", file=sys.stderr)
    # write back
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Refreshed {csv_path}")

if __name__ == "__main__":
    for p in sys.argv[1:]:
        refresh(p)
```

Usage:
```bash
python3 scripts/refresh_hashes.py src/ckg_agentforce/domains/agentforce.csv
```

---

## Temporal Precedence (Out of Scope)

`issued_at` / temporal precedence requires an external anchor (blockchain, RFC 3161 TSA) to be meaningful. A self-declared timestamp inside a digest you control proves nothing. This spec does not fake temporal precedence — that is tracked via git commit history only.

---

## Scope — What This Spec Does and Does Not Cover

| In scope | Out of scope |
|---|---|
| Per-node source URL (fetch hint) | Timestamp proof / temporal ordering |
| Per-node SHA-256 content hash (trust anchor) | Publisher cooperation or canonical URL guarantees |
| Stale edge detection via hash mismatch | Continuous monitoring (run refresh_hashes on demand) |
| MCP `verify_source` tool contract | Real-time source change detection |
| Audit chain documentation | Cryptographic signing of the graph itself |

---

## Applying This Spec to a New CKG

1. Add `SourceURL` and `source_content_hash` columns to your domain CSV
2. Run `scripts/refresh_hashes.py` before first publish
3. Add `verify_source(concept)` tool to your MCP server (copy pattern above)
4. Reference this spec in your package README's Source Provenance section
5. When re-extracting nodes, re-run `refresh_hashes.py` and commit the updated hashes

---

## Reference Implementations

| Package | Version | Notes |
|---|---|---|
| `ckg-agentforce` | 0.2.x+ | First implementation; hash column seeded |
| `ckg-nvidia-ai` | 0.7.0+ | GuardrailDecisionV1 reference impl |
| `ckg-nvidia-nemoclaw` | 0.5.0+ | GuardrailDecisionV1 reference impl; `verify_source` live |

GuardrailDecisionV1 full spec: `~/projects/ckg-nvidia-ai/docs/guardrail-decision-v1.md`

---

*Graphify.md · patent pending · graphifymd.com*
