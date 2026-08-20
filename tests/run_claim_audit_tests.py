#!/usr/bin/env python3
"""Offline checks for the public Claim Audit Starter Kit."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "claim_audit_v0" / "claims_registry.json"
SCHEMA = ROOT / "schemas" / "claim_audit.schema.json"
ALLOWED = {
    "observed",
    "inferred",
    "hypothesis",
    "insufficient",
    "blocked",
    "rejected",
    "contradicted",
}


def main() -> None:
    registry = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    assert registry["schema_version"] == "claim-audit-v0"
    assert schema["title"] == "TraceFoundry Claim Audit Registry"
    assert registry["claims"], "fixture must contain claims"

    statuses = {claim["status"] for claim in registry["claims"]}
    assert statuses <= ALLOWED
    assert {"observed", "rejected", "contradicted"} <= statuses

    for claim in registry["claims"]:
        assert claim["claim_id"]
        assert claim["statement"]
        assert claim["evidence_ids"]
        assert claim["source_uris"]
        for uri in claim["source_uris"]:
            parsed = urlparse(uri)
            assert parsed.scheme == "https"
            assert parsed.netloc

    serialized = EXAMPLE.read_text(encoding="utf-8")
    forbidden = [
        r"/home/ubuntu/",
        r"OPENAI_API_KEY=",
        r"PATENTSVIEW_API_KEY=",
        r"memory\.jsonl",
        r"OI-Organoids-Intelligence",
        r"luxmemory/data",
    ]
    for pattern in forbidden:
        assert not re.search(pattern, serialized), f"forbidden exposure: {pattern}"

    print(f"claim_audit_ok claims={len(registry['claims'])} statuses={','.join(sorted(statuses))}")


if __name__ == "__main__":
    main()
