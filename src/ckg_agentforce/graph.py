import csv
import json
from collections import defaultdict, deque
from pathlib import Path

DOMAINS_DIR = Path(__file__).parent / "domains"

EDGE_TYPES = {"REQUIRES", "ENABLES", "RELATES_TO", "IMPLEMENTS"}


def _parse_dep(token: str) -> tuple[str, str, float | None]:
    """Split 'ID:EDGETYPE:CONFIDENCE' token.
    EDGETYPE defaults to REQUIRES. CONFIDENCE is float 0-1 or None if unreviewed.
    """
    parts = token.split(":", 2)
    etype = parts[1] if len(parts) >= 2 and parts[1] in EDGE_TYPES else "REQUIRES"
    confidence = None
    if len(parts) == 3 and parts[2]:
        try:
            confidence = float(parts[2])
        except ValueError:
            pass
    return parts[0], etype, confidence


def load_domain_meta(domain: str) -> dict:
    """Return domain-level provenance: source_url, build_date."""
    meta_path = DOMAINS_DIR / "metadata.json"
    if not meta_path.exists():
        return {}
    with open(meta_path) as f:
        data = json.load(f)
    return data.get(domain, {})


def available_domains() -> list[str]:
    return sorted(p.stem for p in DOMAINS_DIR.glob("*.csv"))


def load_graph(domain: str):
    csv_path = DOMAINS_DIR / f"{domain}.csv"
    if not csv_path.exists():
        raise ValueError(f"Domain '{domain}' not found. Run list_domains() to see all 20.")

    id_to_label, label_to_id, prerequisites, dependents, taxonomy, provenance = {}, {}, defaultdict(list), defaultdict(list), {}, {}
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            cid = row["ConceptID"]
            label = row["ConceptLabel"].strip()
            raw = [t.strip() for t in row["Dependencies"].split("|") if t.strip()]
            deps = [_parse_dep(t) for t in raw]  # [(dep_id, etype, confidence), ...]
            id_to_label[cid] = label
            label_to_id[label.lower()] = cid
            taxonomy[cid] = row.get("TaxonomyID", "").strip()
            prerequisites[cid] = deps
            provenance[cid] = {
                "source_url": row.get("SourceURL", ""),
                "source_hash": row.get("source_content_hash", ""),
            }
            for dep_id, etype, confidence in deps:
                dependents[dep_id].append((cid, etype, confidence))

    return id_to_label, label_to_id, prerequisites, dependents, taxonomy, provenance


def find_concept(label_to_id: dict, query: str) -> str | None:
    q = query.lower().strip()
    if q in label_to_id:
        return label_to_id[q]
    for label, cid in label_to_id.items():
        if q in label:
            return cid
    return None


def bfs_subgraph(start_id: str, adj: dict, id_to_label: dict, max_depth: int) -> list[dict]:
    """DFS traversal so parent-child relationships indent correctly in text output."""
    visited: set = set()
    results: list[dict] = []

    def _dfs(cid: str, depth: int, etype, conf):
        if cid in visited or depth > max_depth:
            return
        visited.add(cid)
        results.append({
            "concept": id_to_label.get(cid, cid),
            "concept_id": cid,
            "edge_type": etype,
            "confidence": conf,
            "depth": depth,
        })
        for n, et, c in adj.get(cid, []):
            _dfs(n, depth + 1, et, c)

    _dfs(start_id, 0, None, None)
    return results


def prerequisite_chain(start_id: str, prerequisites: dict, id_to_label: dict) -> list[str]:
    visited, queue, chain = set(), deque([start_id]), []
    while queue:
        cid = queue.popleft()
        if cid in visited:
            continue
        visited.add(cid)
        chain.append(id_to_label.get(cid, cid))
        for dep_id, _etype, _conf in prerequisites.get(cid, []):
            if dep_id not in visited:
                queue.append(dep_id)
    return chain
