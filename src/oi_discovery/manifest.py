"""Manifest generation for reproducible discovery results."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from oi_discovery.models import DatasetRecord, DiscoveryQuery, DiscoveryResult
from oi_discovery.selection import rank_assets

SCHEMA_VERSION = "oi-discovery.manifest.v0.1"


def build_result(dataset: DatasetRecord, query: DiscoveryQuery) -> DiscoveryResult:
    decisions = rank_assets(dataset, query)
    selected = tuple(decision.asset_id for decision in decisions if decision.eligible)
    warnings: list[str] = [
        "metadata_only: no scientific asset was downloaded",
        "eligibility_is_heuristic: inspect source metadata before analysis",
    ]
    if not selected:
        warnings.append("no_asset_satisfied_query")
    return DiscoveryResult(
        schema_version=SCHEMA_VERSION,
        query=query,
        dataset=dataset,
        decisions=decisions,
        selected_asset_ids=selected,
        download_performed=False,
        warnings=tuple(warnings),
    )


def manifest_payload(result: DiscoveryResult) -> dict[str, Any]:
    payload = result.to_dict()
    payload["generated_at"] = datetime.now(timezone.utc).isoformat()
    payload["provenance"] = {
        "generator": "oi-discovery-core",
        "policy": "metadata-only",
        "source": result.dataset.source,
        "source_url": result.dataset.source_url,
    }
    return payload


def write_manifest(result: DiscoveryResult, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(manifest_payload(result), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output
