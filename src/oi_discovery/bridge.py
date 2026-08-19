"""Reviewable bridge objects between OI manifests and LuxMemory."""

from __future__ import annotations

import hashlib
import json
from pathlib import PurePosixPath
from typing import Any


def stable_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def asset_quote(asset: dict[str, Any]) -> str:
    size = asset.get("size_bytes", asset.get("size"))
    fields = [
        f"path={asset.get('path', '')}",
        f"format={asset.get('format') or PurePosixPath(asset.get('path', '')).suffix.lstrip('.') or 'unknown'}",
        f"size_bytes={size if size is not None else 'unknown'}",
    ]
    return "; ".join(fields)


def normalize_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    """Normalize current and legacy OI manifests without fetching anything."""

    if "dataset" in manifest and "query" in manifest:
        return manifest

    if "dandiset_id" in manifest and "assets" in manifest:
        dataset_id = str(manifest["dandiset_id"])
        version = str(manifest.get("version", "unknown"))
        base_url = str(manifest.get("source", "")).rstrip("/")
        source_url = f"{base_url}/dandisets/{dataset_id}/" if base_url else None
        raw_assets = manifest.get("assets", [])
        assets: list[dict[str, Any]] = []
        for raw in raw_assets:
            assets.append(
                {
                    "asset_id": raw.get("asset_id"),
                    "path": raw.get("path", ""),
                    "size_bytes": raw.get("size"),
                    "format": PurePosixPath(raw.get("path", "")).suffix.lstrip(".") or None,
                    "source_url": source_url,
                    "raw_metadata": raw,
                }
            )
        selected = manifest.get("selected_smallest_nwb", {})
        selected_ids = [selected["asset_id"]] if selected.get("asset_id") else []
        return {
            "query": {
                "source": "dandi",
                "dataset_id": dataset_id,
                "version": version,
                "formats": ["nwb"],
                "legacy_manifest": True,
            },
            "dataset": {
                "source": "dandi",
                "dataset_id": dataset_id,
                "version": version,
                "name": manifest.get("dandiset", {}).get("draft_version", {}).get("name"),
                "source_url": source_url,
                "asset_count": manifest.get("asset_count_from_api", len(assets)),
                "assets": assets,
            },
            "selected_asset_ids": selected_ids,
            "download_performed": bool(manifest.get("download_performed", False)),
        }

    raise ValueError("Unsupported OI manifest shape: expected current or legacy manifest")


def build_link(
    manifest: dict[str, Any],
    source_path: str,
    memory_type: str = "result",
    capability_ids: list[str] | None = None,
    gate_id: str | None = None,
) -> dict[str, Any]:
    """Build a candidate link without writing to a LuxMemory database."""

    normalized = normalize_manifest(manifest)
    query = normalized["query"]
    dataset = normalized["dataset"]
    source = {
        "adapter": dataset["source"],
        "dataset_id": dataset["dataset_id"],
        "version": dataset["version"],
        "query_hash": stable_hash(query),
        "source_url": dataset.get("source_url"),
    }
    selected = set(normalized.get("selected_asset_ids", []))
    observations: list[dict[str, Any]] = []
    for asset in dataset.get("assets", []):
        if asset.get("asset_id") not in selected:
            continue
        observations.append(
            {
                "asset_id": asset["asset_id"],
                "claim": "asset matches the deterministic discovery query",
                "evidence_role": "metadata_observation",
                "evidence": {
                    "field": "path,format,size_bytes",
                    "quote": asset_quote(asset),
                    "source_url": asset.get("source_url") or asset.get("content_url"),
                },
            }
        )
    dataset_id = dataset["dataset_id"].replace("/", "_")
    return {
        "link_id": f"link_{dataset['source']}_{dataset_id}_{source['query_hash'][7:19]}",
        "source_type": "oi_discovery_manifest",
        "source_path": source_path,
        "source": source,
        "observations": observations,
        "interpretation": {
            "status": "candidate",
            "decision": "candidate_for_inspection" if observations else "no_candidate_selected",
            "limitations": [
                "metadata-only",
                "no scientific suitability established",
                "human review required before analysis",
            ],
        },
        "luxmemory": {
            "memory_type": memory_type,
            "memory_id": None,
            "capability_ids": capability_ids or [],
            "gate_id": gate_id,
        },
    }
