from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from oi_discovery.manifest import build_result, write_manifest
from oi_discovery.models import AssetRecord, DatasetRecord, DiscoveryQuery
from oi_discovery.selection import rank_assets


def dataset() -> DatasetRecord:
    return DatasetRecord(
        source="fixture",
        dataset_id="fixture-001",
        version="v1",
        name="Public electrophysiology metadata fixture",
        asset_count=3,
        assets=(
            AssetRecord(source="fixture", asset_id="a-nwb", path="recording.nwb", size_bytes=100, format="nwb", source_url="https://example.org/a"),
            AssetRecord(source="fixture", asset_id="b-csv", path="table.csv", size_bytes=20, format="csv", source_url="https://example.org/b"),
            AssetRecord(source="fixture", asset_id="c-nwb", path="large.nwb", size_bytes=500, format="nwb", source_url="https://example.org/c"),
        ),
    )


def test_selection_is_explainable_and_deterministic() -> None:
    query = DiscoveryQuery(source="fixture", dataset_id="fixture-001", formats=("nwb",), max_size_bytes=200, max_assets=1)
    decisions = rank_assets(dataset(), query)
    assert decisions[0].asset_id == "a-nwb"
    assert decisions[0].eligible is True
    assert "format_matches" in decisions[0].reasons
    assert decisions[1].eligible is False
    assert "format_not_requested:csv" in decisions[1].rejected_reasons
    assert "above_max_size" in decisions[2].rejected_reasons


def test_manifest_is_metadata_only(tmp_path: Path) -> None:
    query = DiscoveryQuery(source="fixture", dataset_id="fixture-001", formats=("nwb",))
    result = build_result(dataset(), query)
    path = write_manifest(result, tmp_path / "manifest.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["download_performed"] is False
    assert payload["provenance"]["policy"] == "metadata-only"
    assert payload["selected_asset_ids"] == ["a-nwb", "c-nwb"]
    assert payload["warnings"]
