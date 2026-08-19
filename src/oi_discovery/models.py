"""Canonical data contracts for OI Discovery.

These models deliberately describe metadata and provenance, not raw biological data.
They are safe to serialize into manifests and can be populated by multiple public APIs.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class DiscoveryQuery:
    """A reproducible selection request against one or more discovery sources."""

    source: str = "any"
    dataset_id: str | None = None
    version: str = "draft"
    formats: tuple[str, ...] = ()
    modalities: tuple[str, ...] = ()
    min_size_bytes: int | None = None
    max_size_bytes: int | None = None
    max_assets: int | None = None
    require_public: bool = True

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["formats"] = list(self.formats)
        payload["modalities"] = list(self.modalities)
        return payload


@dataclass(frozen=True)
class AssetRecord:
    """A source asset represented by metadata only; no content is downloaded."""

    source: str
    asset_id: str
    path: str
    size_bytes: int | None = None
    format: str | None = None
    modality: str | None = None
    license: str | None = None
    source_url: str | None = None
    content_url: str | None = None
    checksum: str | None = None
    modified_at: str | None = None
    raw_metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DatasetRecord:
    """A normalized dataset record composed from a public source API."""

    source: str
    dataset_id: str
    version: str
    name: str
    status: str | None = None
    description: str | None = None
    license: str | None = None
    source_url: str | None = None
    asset_count: int = 0
    total_size_bytes: int | None = None
    assets: tuple[AssetRecord, ...] = ()
    raw_metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["assets"] = [asset.to_dict() for asset in self.assets]
        return payload


@dataclass(frozen=True)
class EligibilityDecision:
    """An explainable decision about one asset under one query."""

    asset_id: str
    eligible: bool
    score: float
    reasons: tuple[str, ...] = ()
    rejected_reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["reasons"] = list(self.reasons)
        payload["rejected_reasons"] = list(self.rejected_reasons)
        return payload


@dataclass(frozen=True)
class DiscoveryResult:
    """A complete, auditable answer to a discovery query."""

    schema_version: str
    query: DiscoveryQuery
    dataset: DatasetRecord
    decisions: tuple[EligibilityDecision, ...]
    selected_asset_ids: tuple[str, ...]
    download_performed: bool = False
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "query": self.query.to_dict(),
            "dataset": self.dataset.to_dict(),
            "decisions": [decision.to_dict() for decision in self.decisions],
            "selected_asset_ids": list(self.selected_asset_ids),
            "download_performed": self.download_performed,
            "warnings": list(self.warnings),
        }
