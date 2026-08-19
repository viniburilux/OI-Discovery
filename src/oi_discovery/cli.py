"""Command-line entry point for metadata-only discovery."""

from __future__ import annotations

import argparse
from pathlib import Path

from oi_discovery.adapters.dandi import DandiAdapter
from oi_discovery.manifest import build_result, write_manifest
from oi_discovery.models import DiscoveryQuery


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Discover public scientific assets by metadata only.")
    parser.add_argument("--source", default="dandi", choices=["dandi"])
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--version", default="draft")
    parser.add_argument("--format", dest="formats", action="append", default=[])
    parser.add_argument("--modality", dest="modalities", action="append", default=[])
    parser.add_argument("--min-size-bytes", type=int)
    parser.add_argument("--max-size-bytes", type=int)
    parser.add_argument("--max-assets", type=int)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
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
