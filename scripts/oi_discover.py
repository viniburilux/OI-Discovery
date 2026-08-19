#!/usr/bin/env python3
"""Metadata-only OI Discovery CLI.

Example:
    python scripts/oi_discover.py \
        --source dandi \
        --dataset-id 001603 \
        --version draft \
        --format nwb \
        --max-assets 1 \
        --output data_catalog/discovery_result.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from oi_discovery.adapters.dandi import DandiAdapter
from oi_discovery.manifest import build_result, write_manifest
from oi_discovery.models import DiscoveryQuery


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Discover public OI datasets by metadata only.")
    parser.add_argument("--source", default="dandi", choices=["dandi"])
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--version", default="draft")
    parser.add_argument("--format", dest="formats", action="append", default=[])
    parser.add_argument("--modality", dest="modalities", action="append", default=[])
    parser.add_argument("--min-size-bytes", type=int)
    parser.add_argument("--max-size-bytes", type=int)
    parser.add_argument("--max-assets", type=int)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    query = DiscoveryQuery(
        source=args.source,
        dataset_id=args.dataset_id,
        version=args.version,
        formats=tuple(args.formats),
        modalities=tuple(args.modalities),
        min_size_bytes=args.min_size_bytes,
        max_size_bytes=args.max_size_bytes,
        max_assets=args.max_assets,
    )
    dataset = DandiAdapter().discover(query)
    result = build_result(dataset, query)
    output = write_manifest(result, args.output)
    print(f"wrote {output}")
    print(f"dataset={dataset.dataset_id} assets={dataset.asset_count} selected={len(result.selected_asset_ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
