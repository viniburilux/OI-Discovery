"""Public contracts for auditable investigation state and research moves.

These contracts describe reasoning about public metadata and provenance. They do
not contain raw scientific data, private memory, credentials, or autonomous
scientific conclusions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


EPISTEMIC_STATUSES = (
    "observed",
    "inferred",
    "hypothesis",
    "insufficient",
    "blocked",
    "rejected",
    "contradicted",
)

INVESTIGATION_STATUSES = ("open", "in_review", "resolved", "closed")
MOVE_STATUSES = ("proposed", "accepted", "completed", "rejected", "blocked")


@dataclass(frozen=True)
class EvidenceReference:
    """A pointer to public evidence or a reproducible source observation."""

    evidence_id: str
    kind: str
    source: str
    uri: str | None = None
    record_id: str | None = None
    observed_at: str | None = None
    metadata_only: bool = True
    provenance_note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Claim:
    """A reviewable statement with an explicit epistemic status."""

    claim_id: str
    statement: str
    status: str
    evidence_ids: tuple[str, ...] = ()
    gap_ids: tuple[str, ...] = ()
    note: str | None = None

    def __post_init__(self) -> None:
        if self.status not in EPISTEMIC_STATUSES:
            raise ValueError(f"unsupported epistemic status: {self.status}")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["evidence_ids"] = list(self.evidence_ids)
        payload["gap_ids"] = list(self.gap_ids)
        return payload


@dataclass(frozen=True)
class EvidenceGap:
    """An explicit uncertainty that prevents a stronger claim or decision."""

    gap_id: str
    statement: str
    severity: str = "material"
    required_evidence: tuple[str, ...] = ()
    status: str = "open"

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["required_evidence"] = list(self.required_evidence)
        return payload


@dataclass(frozen=True)
class InvestigationState:
    """A versioned snapshot of the state of one investigation."""

    schema_version: str
    investigation_id: str
    question: str
    status: str
    evidence: tuple[EvidenceReference, ...] = ()
    claims: tuple[Claim, ...] = ()
    gaps: tuple[EvidenceGap, ...] = ()
    decision: str | None = None
    next_move_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.status not in INVESTIGATION_STATUSES:
            raise ValueError(f"unsupported investigation status: {self.status}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "investigation_id": self.investigation_id,
            "question": self.question,
            "status": self.status,
            "evidence": [item.to_dict() for item in self.evidence],
            "claims": [item.to_dict() for item in self.claims],
            "gaps": [item.to_dict() for item in self.gaps],
            "decision": self.decision,
            "next_move_id": self.next_move_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class ResearchMove:
    """A proposed or completed next action that can reduce an evidence gap."""

    schema_version: str
    move_id: str
    investigation_id: str
    title: str
    objective: str
    action_type: str
    action: str
    rationale: str
    evidence_ids: tuple[str, ...] = ()
    gap_ids: tuple[str, ...] = ()
    expected_observation: str | None = None
    stop_criteria: tuple[str, ...] = ()
    status: str = "proposed"
    created_at: str | None = None
    provenance_note: str | None = None

    def __post_init__(self) -> None:
        if self.status not in MOVE_STATUSES:
            raise ValueError(f"unsupported research move status: {self.status}")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["evidence_ids"] = list(self.evidence_ids)
        payload["gap_ids"] = list(self.gap_ids)
        payload["stop_criteria"] = list(self.stop_criteria)
        return payload


def build_investigation_state(
    *,
    schema_version: str,
    investigation_id: str,
    question: str,
    status: str,
    evidence: list[EvidenceReference] | tuple[EvidenceReference, ...] = (),
    claims: list[Claim] | tuple[Claim, ...] = (),
    gaps: list[EvidenceGap] | tuple[EvidenceGap, ...] = (),
    decision: str | None = None,
    next_move_id: str | None = None,
    created_at: str | None = None,
    updated_at: str | None = None,
    warnings: list[str] | tuple[str, ...] = (),
) -> InvestigationState:
    """Build a normalized immutable investigation snapshot."""

    return InvestigationState(
        schema_version=schema_version,
        investigation_id=investigation_id,
        question=question,
        status=status,
        evidence=tuple(evidence),
        claims=tuple(claims),
        gaps=tuple(gaps),
        decision=decision,
        next_move_id=next_move_id,
        created_at=created_at,
        updated_at=updated_at,
        warnings=tuple(warnings),
    )


__all__ = [
    "EPISTEMIC_STATUSES",
    "INVESTIGATION_STATUSES",
    "MOVE_STATUSES",
    "EvidenceReference",
    "Claim",
    "EvidenceGap",
    "InvestigationState",
    "ResearchMove",
    "build_investigation_state",
]
