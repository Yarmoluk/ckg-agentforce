#!/usr/bin/env python3
"""
CKG Domain Validator — enforces edge integrity rules at build time.
Run before any CSV ships. Hard fails on violations — no warnings, no overrides.

Rules:
  1. REQUIRES without SourceURL → FAIL
  2. Any confidence value without SourceURL → FAIL
  3. RELATES_TO without SourceURL → confidence must be null → FAIL if not
  4. ENABLES without SourceURL → confidence must be null → FAIL if not
  5. Unknown edge type → FAIL
  6. Dependency references a ConceptID that doesn't exist → FAIL
"""

import csv
import sys
from pathlib import Path

VALID_EDGE_TYPES = {"REQUIRES", "ENABLES", "RELATES_TO", "IMPLEMENTS"}
EDGES_REQUIRING_SOURCE = {"REQUIRES"}
EDGES_FORBIDDING_CONFIDENCE_WITHOUT_SOURCE = {"ENABLES", "RELATES_TO", "IMPLEMENTS"}


def parse_dependencies(dep_string):
    """Parse 'ID:EDGETYPE:CONFIDENCE|ID:EDGETYPE' into list of dicts."""
    if not dep_string or not dep_string.strip():
        return []
    deps = []
    for token in dep_string.split("|"):
        token = token.strip()
        if not token:
            continue
        parts = token.split(":")
        dep = {
            "raw": token,
            "id": parts[0],
            "edge_type": parts[1] if len(parts) > 1 else "REQUIRES",
            "confidence": parts[2] if len(parts) > 2 else None,
        }
        deps.append(dep)
    return deps


def validate_csv(path):
    errors = []
    path = Path(path)

    if not path.exists():
        return [f"FILE NOT FOUND: {path}"]

    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        if "SourceURL" not in (reader.fieldnames or []):
            errors.append("SCHEMA: Missing required column 'SourceURL'")
            return errors
        rows = list(reader)

    concept_ids = {row["ConceptID"] for row in rows}

    for row in rows:
        cid = row["ConceptID"]
        label = row.get("ConceptLabel", cid)
        source = (row.get("SourceURL") or "").strip()
        deps = parse_dependencies(row.get("Dependencies", ""))

        for dep in deps:
            dep_id = dep["id"]
            etype = dep["edge_type"]
            confidence = dep["confidence"]
            raw = dep["raw"]

            # Rule 6: dependency must reference a real ConceptID
            if dep_id not in concept_ids:
                errors.append(
                    f"[{cid}] {label}: dependency '{raw}' references unknown ConceptID {dep_id}"
                )

            # Rule 5: edge type must be valid
            if etype not in VALID_EDGE_TYPES:
                errors.append(
                    f"[{cid}] {label}: unknown edge type '{etype}' in '{raw}'"
                )
                continue

            # Rule 1: REQUIRES must have SourceURL
            if etype in EDGES_REQUIRING_SOURCE and not source:
                errors.append(
                    f"[{cid}] {label}: REQUIRES edge '{raw}' has no SourceURL — "
                    f"cite the doc page or demote to RELATES_TO:null"
                )

            # Rules 2/3/4: confidence without SourceURL is a false precision claim
            if confidence is not None and not source:
                errors.append(
                    f"[{cid}] {label}: edge '{raw}' has confidence={confidence} but no SourceURL — "
                    f"confidence without a source is invented precision. Remove confidence or add SourceURL."
                )

    return errors


def has_source_url_column(path):
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return "SourceURL" in (reader.fieldnames or [])


def validate_all(domain_dir):
    domain_dir = Path(domain_dir)
    csvs = sorted(domain_dir.glob("*.csv"))
    if not csvs:
        print(f"No CSV files found in {domain_dir}")
        sys.exit(1)

    total_errors = 0
    failed_domains = []
    v1_domains = []

    for csv_path in csvs:
        if csv_path.stem.endswith(("-B", "-A-backup")):
            continue

        if not has_source_url_column(csv_path):
            v1_domains.append(csv_path.name)
            continue

        errors = validate_csv(csv_path)
        if errors:
            print(f"\nFAIL  {csv_path.name}  ({len(errors)} error{'s' if len(errors)>1 else ''})")
            for e in errors:
                print(f"      {e}")
            total_errors += len(errors)
            failed_domains.append(csv_path.name)
        else:
            print(f"OK    {csv_path.name}")

    print(f"\n{'='*60}")

    if v1_domains:
        print(f"MIGRATE  {len(v1_domains)} v1 domains (no SourceURL column — not yet enforced):")
        for d in v1_domains:
            print(f"         {d}")

    if total_errors == 0:
        print(f"\nv2 DOMAINS: ALL PASS")
        sys.exit(0)
    else:
        print(f"\nFAILED — {total_errors} errors across {len(failed_domains)} v2 domains")
        print(f"Domains with errors: {', '.join(failed_domains)}")
        print("Nothing ships until v2 domain errors are resolved.")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        # validate single file
        errors = validate_csv(sys.argv[1])
        if errors:
            for e in errors:
                print(e)
            sys.exit(1)
        else:
            print("OK")
            sys.exit(0)
    else:
        domain_dir = Path(__file__).parent.parent / "src/ckg_nvidia_ai/domains"
        validate_all(domain_dir)
