"""OI Discovery: metadata-first scientific dataset discovery."""

from oi_discovery.bridge import build_link
from oi_discovery.investigation import (
    Claim,
    EvidenceGap,
    EvidenceReference,
    InvestigationState,
    ResearchMove,
)
from oi_discovery.manifest import SCHEMA_VERSION, build_result, write_manifest
from oi_discovery.models import (
    AssetRecord,
    DatasetRecord,
    DiscoveryQuery,
    DiscoveryResult,
    EligibilityDecision,
)

__all__ = [
    "SCHEMA_VERSION",
    "AssetRecord",
    "DatasetRecord",
    "DiscoveryQuery",
    "DiscoveryResult",
    "EligibilityDecision",
    "Claim",
    "EvidenceGap",
    "EvidenceReference",
    "InvestigationState",
    "ResearchMove",
    "build_link",
    "build_result",
    "write_manifest",
]
