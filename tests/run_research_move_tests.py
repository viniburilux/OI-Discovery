"""Offline tests for public Investigation State and Research Move contracts."""

from __future__ import annotations

import json
from pathlib import Path

from oi_discovery import (
    Claim,
    EvidenceGap,
    EvidenceReference,
    InvestigationState,
    ResearchMove,
)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    state_payload = json.loads(
        (root / "examples" / "research_move_v0" / "v001_investigation_state.json").read_text(
            encoding="utf-8"
        )
    )
    move_payload = json.loads(
        (root / "examples" / "research_move_v0" / "v001_research_move.json").read_text(
            encoding="utf-8"
        )
    )

    evidence = tuple(EvidenceReference(**item) for item in state_payload["evidence"])
    claims = tuple(Claim(**item) for item in state_payload["claims"])
    gaps = tuple(EvidenceGap(**item) for item in state_payload["gaps"])
    state = InvestigationState(
        schema_version=state_payload["schema_version"],
        investigation_id=state_payload["investigation_id"],
        question=state_payload["question"],
        status=state_payload["status"],
        evidence=evidence,
        claims=claims,
        gaps=gaps,
        decision=state_payload["decision"],
        next_move_id=state_payload["next_move_id"],
        created_at=state_payload["created_at"],
        updated_at=state_payload["updated_at"],
        warnings=tuple(state_payload["warnings"]),
    )
    move = ResearchMove(
        schema_version=move_payload["schema_version"],
        move_id=move_payload["move_id"],
        investigation_id=move_payload["investigation_id"],
        title=move_payload["title"],
        objective=move_payload["objective"],
        action_type=move_payload["action_type"],
        action=move_payload["action"],
        rationale=move_payload["rationale"],
        evidence_ids=tuple(move_payload["evidence_ids"]),
        gap_ids=tuple(move_payload["gap_ids"]),
        expected_observation=move_payload["expected_observation"],
        stop_criteria=tuple(move_payload["stop_criteria"]),
        status=move_payload["status"],
        created_at=move_payload["created_at"],
        provenance_note=move_payload["provenance_note"],
    )

    assert state.to_dict()["warnings"]
    assert len(state.evidence) == 4
    assert len(state.claims) == 3
    assert len(state.gaps) == 4
    assert state.next_move_id == move.move_id
    assert move.investigation_id == state.investigation_id
    assert move.status == "proposed"
    assert all(item.metadata_only for item in state.evidence)
    assert any(claim.status == "insufficient" for claim in state.claims) is False
    assert any("not" in criterion.lower() for criterion in move.stop_criteria)
    print(
        "research_move_valid "
        f"investigation={state.investigation_id} "
        f"evidence={len(state.evidence)} claims={len(state.claims)} gaps={len(state.gaps)}"
    )


if __name__ == "__main__":
    main()
