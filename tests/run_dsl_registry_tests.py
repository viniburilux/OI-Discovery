"""Offline tests for Query DSL, absence assessment and Discovery Registry."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from oi_discovery.evaluation import assess_manifest
from oi_discovery.query import parse_query
from oi_discovery.registry import DiscoveryRegistry, DiscoveryRun


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    fixture = json.loads((root / "tests" / "fixtures" / "manifest_minimal.json").read_text(encoding="utf-8"))

    parsed = parse_query(
        {
            "schema_version": "oi.discovery.query.v0",
            "sources": ["zenodo"],
            "formats": ["record"],
            "max_size_gb": 1,
            "max_assets": 3,
            "license": ["CC-BY-4.0"],
        }
    )
    assert parsed.canonical.source == "zenodo"
    assert parsed.canonical.max_size_bytes == 1024**3
    assert "license" in parsed.unresolved_constraints
    assert parsed.executable is False

    assessment = assess_manifest(fixture, unresolved_constraints=list(parsed.unresolved_constraints))
    assert assessment["conclusion"] == "insufficient_evidence"
    assert assessment["candidate_count"] == 1
    assert assessment["rejected_count"] == 1
    assert "missing_license" in assessment["rejection_reasons"]

    with tempfile.TemporaryDirectory() as temp_dir:
        registry = DiscoveryRegistry(Path(temp_dir) / "registry.jsonl")
        run = DiscoveryRun.from_manifest(
            fixture,
            evaluation=assessment,
            next_action=assessment["next_action"],
        )
        registry.append(run)
        loaded = registry.get(run.run_id)
        assert loaded is not None
        assert loaded["status"] == "candidate"
        assert loaded["manifest"]["download_performed"] is False
        assert loaded["evaluation"]["conclusion"] == "insufficient_evidence"
    print("dsl_registry_valid unresolved=license conclusion=insufficient_evidence")


if __name__ == "__main__":
    main()
