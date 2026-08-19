"""Offline validation for OI Discovery Benchmark v0."""

from __future__ import annotations

import json
from pathlib import Path


REQUIRED = {
    "id",
    "domain",
    "question",
    "decision",
    "expected_sources",
    "inclusion",
    "exclusion",
    "minimum_answer",
    "gold_label_status",
}


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    path = root / "benchmark" / "benchmark_v0.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    questions = payload.get("questions", [])
    assert len(questions) == 10, f"expected 10 questions, got {len(questions)}"
    ids = [item.get("id") for item in questions]
    assert len(set(ids)) == 10, "benchmark IDs must be unique"
    for item in questions:
        missing = REQUIRED - set(item)
        assert not missing, f"{item.get('id')} missing {sorted(missing)}"
        for field in ("expected_sources", "inclusion", "exclusion"):
            assert item[field], f"{item['id']} has empty {field}"
    negative = [item for item in questions if item["gold_label_status"] == "negative_control"]
    assert len(negative) == 1, "benchmark must have exactly one negative control"
    assert negative[0]["id"] == "B009"
    assert payload["policy"]["metadata_only"] is True
    assert payload["policy"]["no_raw_download"] is True
    print(f"benchmark_valid questions={len(questions)} negative_control={negative[0]['id']}")


if __name__ == "__main__":
    main()
