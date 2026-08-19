"""Minimal query DSL parser with explicit unsupported-constraint reporting."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from oi_discovery.models import DiscoveryQuery


SUPPORTED_FIELDS = {
    "schema_version",
    "sources",
    "dataset_id",
    "formats",
    "modalities",
    "min_size_gb",
    "max_size_gb",
    "max_assets",
}


@dataclass(frozen=True)
class ParsedQuery:
    """A canonical query plus constraints the current adapter cannot enforce."""

    dsl: dict[str, Any]
    canonical: DiscoveryQuery
    unresolved_constraints: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def executable(self) -> bool:
        return not self.unresolved_constraints

    def to_dict(self) -> dict[str, Any]:
        return {
            "dsl": self.dsl,
            "canonical": self.canonical.to_dict(),
            "unresolved_constraints": list(self.unresolved_constraints),
            "warnings": list(self.warnings),
            "executable": self.executable,
        }


def _as_tuple(values: Any, field_name: str) -> tuple[str, ...]:
    if values is None:
        return ()
    if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
        raise ValueError(f"{field_name} must be a list of strings")
    return tuple(values)


def _gb_to_bytes(value: Any, field_name: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative number")
    return int(value * 1024**3)


def parse_query(payload: dict[str, Any]) -> ParsedQuery:
    """Parse a v0 DSL payload without relaxing unknown constraints."""

    if not isinstance(payload, dict):
        raise ValueError("query must be an object")
    if payload.get("schema_version") != "oi.discovery.query.v0":
        raise ValueError("schema_version must be oi.discovery.query.v0")

    sources = _as_tuple(payload.get("sources"), "sources")
    if not sources:
        raise ValueError("sources must contain at least one source")

    dataset_id = payload.get("dataset_id")
    if dataset_id is not None and not isinstance(dataset_id, str):
        raise ValueError("dataset_id must be a string")
    formats = _as_tuple(payload.get("formats"), "formats")
    modalities = _as_tuple(payload.get("modalities"), "modalities")
    max_assets = payload.get("max_assets")
    if max_assets is not None and (not isinstance(max_assets, int) or max_assets < 1):
        raise ValueError("max_assets must be a positive integer")

    unresolved = tuple(sorted(set(payload) - SUPPORTED_FIELDS))
    warnings = tuple(
        f"constraint_not_enforced:{field}"
        for field in unresolved
        if field != "schema_version"
    )

    source = sources[0] if len(sources) == 1 else "any"
    canonical = DiscoveryQuery(
        source=source,
        dataset_id=dataset_id,
        formats=formats,
        modalities=modalities,
        min_size_bytes=_gb_to_bytes(payload.get("min_size_gb"), "min_size_gb"),
        max_size_bytes=_gb_to_bytes(payload.get("max_size_gb"), "max_size_gb"),
        max_assets=max_assets,
        require_public=True,
    )
    return ParsedQuery(
        dsl=dict(payload),
        canonical=canonical,
        unresolved_constraints=unresolved,
        warnings=warnings,
    )
