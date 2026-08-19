#!/usr/bin/env python3
"""Create a reviewable OI Discovery -> LuxMemory link from a manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from oi_discovery.bridge import build_link


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Link an OI Discovery manifest to LuxMemory for review.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--memory-type", default="result", choices=["result", "experiment", "hypothesis", "decision", "project_state", "other"])
    parser.add_argument("--capability-id", action="append", default=[])
    parser.add_argument("--gate-id")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    link = build_link(manifest, str(args.manifest), args.memory_type, args.capability_id, args.gate_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(link, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")
    print(f"link_id={link['link_id']} observations={len(link['observations'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
