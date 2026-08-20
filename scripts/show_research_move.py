"""Render a public Research Move fixture as a decision card."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Show a TraceFoundry Research Move fixture")
    parser.add_argument(
        "--fixture",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "examples"
        / "research_move_v0"
        / "v001_investigation_state.json",
    )
    parser.add_argument(
        "--move",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "examples"
        / "research_move_v0"
        / "v001_research_move.json",
    )
    args = parser.parse_args()
    state = json.loads(args.fixture.read_text(encoding="utf-8"))
    move = json.loads(args.move.read_text(encoding="utf-8"))

    print(f"Investigation: {state['investigation_id']}")
    print(f"Question: {state['question']}")
    print(f"Status: {state['status']} | Decision: {state.get('decision')}")
    print(f"Evidence: {len(state['evidence'])} | Claims: {len(state['claims'])} | Open gaps: {len(state['gaps'])}")
    print("\nClaims:")
    for claim in state["claims"]:
        print(f"- [{claim['status']}] {claim['statement']}")
    print("\nNext Research Move:")
    print(f"- {move['title']}")
    print(f"  Objective: {move['objective']}")
    print(f"  Action: {move['action']}")
    print(f"  Stop criteria: {len(move['stop_criteria'])}")


if __name__ == "__main__":
    main()
