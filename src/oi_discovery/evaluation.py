"""Evaluation helpers for candidate sufficiency and explicit absence."""

from __future__ import annotations

from collections import Counter
from typing import Any


def assess_manifest(
    manifest: dict[str, Any],
    *,
    unresolved_constraints: list[str] | tuple[str, ...] = (),
    hard_constraints: list[str] | tuple[str, ...] = (),
) -> dict[str, Any]:
    """Return a conservative assessment without relaxing query constraints."""

    dataset = manifest.get("dataset", {})
    decisions = manifest.get("decisions", [])
    selected = list(manifest.get("selected_asset_ids", []))
    rejected = [item for item in decisions if not item.get("eligible", False)]
    reason_counts = Counter(
        reason
        for item in rejected
        for reason in item.get("rejected_reasons", [])
    )
    sources = sorted({dataset.get("source", "unknown")})
    warnings = list(manifest.get("warnings", []))
    unresolved = list(unresolved_constraints)
    hard = list(hard_constraints)

    if unresolved:
        conclusion = "insufficient_evidence"
        basis = "unresolved_constraints"
    elif not selected:
        conclusion = "insufficient_evidence"
        basis = "no_eligible_candidates"
    elif hard:
        conclusion = "candidate_evidence_requires_review"
        basis = "hard_constraints_declared_but_not_fully_validated"
    else:
        conclusion = "candidates_found"
        basis = "eligible_candidates_present"

    return {
        "assessment_schema_version": "oi.discovery.assessment.v0",
        "conclusion": conclusion,
        "basis": basis,
        "sources_consulted": sources,
        "candidate_count": len(selected),
        "rejected_count": len(rejected),
        "rejection_reasons": dict(sorted(reason_counts.items())),
        "unresolved_constraints": unresolved,
        "hard_constraints": hard,
        "warnings": warnings,
        "next_action": (
            "review_source_metadata_and_constraints"
            if conclusion == "insufficient_evidence"
            else "manual_domain_review_before_scientific_use"
        ),
    }


def render_assessment(assessment: dict[str, Any]) -> str:
    """Render a compact human-readable absence/sufficiency report."""

    lines = [
        f"conclusion: {assessment['conclusion']}",
        f"sources_consulted: {', '.join(assessment['sources_consulted']) or 'none'}",
        f"candidates: {assessment['candidate_count']}",
        f"rejected: {assessment['rejected_count']}",
    ]
    if assessment.get("rejection_reasons"):
        lines.append("rejection_reasons:")
        lines.extend(f"  {key}: {value}" for key, value in assessment["rejection_reasons"].items())
    if assessment.get("unresolved_constraints"):
        lines.append("unresolved_constraints:")
        lines.extend(f"  - {item}" for item in assessment["unresolved_constraints"])
    lines.append(f"next_action: {assessment['next_action']}")
    return "\n".join(lines)
