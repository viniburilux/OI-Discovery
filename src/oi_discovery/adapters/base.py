"""Adapter protocol for public discovery sources."""

from __future__ import annotations

from typing import Protocol

from oi_discovery.models import DatasetRecord, DiscoveryQuery


class DiscoveryAdapter(Protocol):
    """Minimal contract implemented by every source adapter."""

    source_name: str

    def discover(self, query: DiscoveryQuery) -> DatasetRecord:
        """Return normalized metadata without downloading scientific data."""
        ...
