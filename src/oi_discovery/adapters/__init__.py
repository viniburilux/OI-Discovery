"""Public source adapters for OI Discovery."""

from oi_discovery.adapters.dandi import DandiAdapter
from oi_discovery.adapters.openalex import OpenAlexAdapter
from oi_discovery.adapters.patentsview import PatentAdapter
from oi_discovery.adapters.zenodo import ZenodoAdapter

__all__ = ["DandiAdapter", "OpenAlexAdapter", "PatentAdapter", "ZenodoAdapter"]
