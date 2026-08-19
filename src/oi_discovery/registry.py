"""Versioned discovery run registry."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REGISTRY_SCHEMA_VERSION = "oi.discovery.registry.v0"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _stable_id(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


@dataclass
class DiscoveryRun:
    """An auditable record of one discovery execution."""

    run_id: str
    created_at: str
    query: dict[str, Any]
    sources: list[str]
    candidates: list[dict[str, Any]] = field(default_factory=list)
    rejected: list[dict[str, Any]] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    provenance: list[dict[str, Any]] = field(default_factory=list)
    manifest: dict[str, Any] | None = None
    evaluation: dict[str, Any] | None = None
    next_action: str | None = None
    status: str = "candidate"
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema_version"] = REGISTRY_SCHEMA_VERSION
        return payload

    @classmethod
    def from_manifest(
        cls,
        manifest: dict[str, Any],
        *,
        evaluation: dict[str, Any] | None = None,
        next_action: str | None = None,
        status: str = "candidate",
    ) -> "DiscoveryRun":
        dataset = manifest.get("dataset", {})
        decisions = manifest.get("decisions", [])
        selected_ids = set(manifest.get("selected_asset_ids", []))
        candidates = [item for item in dataset.get("assets", []) if item.get("asset_id") in selected_ids]
        rejected = [item for item in decisions if not item.get("eligible", False)]
        reasons = sorted({reason for item in decisions for reason in item.get("rejected_reasons", [])})
        provenance = []
        if dataset.get("source_url"):
            provenance.append({"kind": "dataset", "url": dataset["source_url"], "source": dataset.get("source")})
        for asset in dataset.get("assets", []):
            url = asset.get("source_url") or asset.get("content_url")
            if url:
                provenance.append({"kind": "asset", "asset_id": asset.get("asset_id"), "url": url, "source": asset.get("source")})
        query = manifest.get("query", {})
        identity = {
            "query": query,
            "dataset_id": dataset.get("dataset_id"),
            "version": dataset.get("version"),
            "selected_asset_ids": sorted(selected_ids),
        }
        warnings = list(manifest.get("warnings", []))
        if manifest.get("download_performed"):
            warnings.append("download_performed_true:registry_accepts_metadata_only_runs_by_default")
        return cls(
            run_id=_stable_id(identity),
            created_at=_utc_now(),
            query=query,
            sources=sorted({dataset.get("source", "unknown")}),
            candidates=candidates,
            rejected=rejected,
            reasons=reasons,
            provenance=provenance,
            manifest=manifest,
            evaluation=evaluation,
            next_action=next_action,
            status=status,
            warnings=warnings,
        )


class DiscoveryRegistry:
    """Append-only JSONL registry for reproducible discovery runs."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, run: DiscoveryRun) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(run.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")

    def list(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        with self.path.open(encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]

    def get(self, run_id: str) -> dict[str, Any] | None:
        return next((item for item in self.list() if item.get("run_id") == run_id), None)
