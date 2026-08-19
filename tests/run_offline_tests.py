from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from oi_discovery.bridge import build_link
from oi_discovery.manifest import build_result, write_manifest
from oi_discovery.models import AssetRecord, DatasetRecord, DiscoveryQuery
from oi_discovery.selection import rank_assets


def fixture_dataset() -> DatasetRecord:
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


def test_selection() -> None:
    query = DiscoveryQuery(source="fixture", dataset_id="fixture-001", formats=("nwb",), max_size_bytes=200, max_assets=1)
    decisions = rank_assets(fixture_dataset(), query)
    assert decisions[0].asset_id == "a-nwb"
    assert decisions[0].eligible is True
    assert "format_matches" in decisions[0].reasons
    by_id = {decision.asset_id: decision for decision in decisions}
    assert by_id["b-csv"].eligible is False
    assert "format_not_requested:csv" in by_id["b-csv"].rejected_reasons
    assert "above_max_size" in by_id["c-nwb"].rejected_reasons


def test_manifest(tmp_path: Path) -> None:
    query = DiscoveryQuery(source="fixture", dataset_id="fixture-001", formats=("nwb",))
    result = build_result(fixture_dataset(), query)
    path = write_manifest(result, tmp_path / "manifest.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["download_performed"] is False
    assert payload["provenance"]["policy"] == "metadata-only"
    assert payload["selected_asset_ids"] == ["a-nwb", "c-nwb"]
    assert payload["warnings"]


def test_bridge() -> None:
    query = DiscoveryQuery(source="fixture", dataset_id="fixture-001", formats=("nwb",))
    result = build_result(fixture_dataset(), query)
    link = build_link(result.to_dict(), "data_catalog/fixture.json", capability_ids=["CAP-OBS-EVIDENCE_MEMORY_DECISION"])
    assert link["source_type"] == "oi_discovery_manifest"
    assert link["source"]["query_hash"].startswith("sha256:")
    assert len(link["observations"]) == 2
    assert link["interpretation"]["status"] == "candidate"
    assert link["luxmemory"]["capability_ids"] == ["CAP-OBS-EVIDENCE_MEMORY_DECISION"]


def test_legacy_manifest() -> None:
    legacy_path = ROOT / "tests/legacy_dandi_fixture.json"
    legacy = {
        "source": "https://api.dandiarchive.org/api/",
        "dandiset_id": "001603",
        "version": "draft",
        "dandiset": {"draft_version": {"name": "fixture"}},
        "asset_count_from_api": 1,
        "assets": [{
            "asset_id": "legacy-asset-001",
            "blob": "legacy-blob-001",
            "path": "sub-HO3/session.nwb",
            "size": 9066104,
        }],
        "selected_smallest_nwb": {
            "asset_id": "legacy-asset-001",
            "blob": "legacy-blob-001",
            "path": "sub-HO3/session.nwb",
            "size": 9066104,
        },
        "download_performed": False,
    }
    link = build_link(legacy, str(legacy_path), capability_ids=["CAP-OBS-EVIDENCE_MEMORY_DECISION"])
    assert link["source"]["dataset_id"] == "001603"
    assert link["source"]["adapter"] == "dandi"
    assert len(link["observations"]) == 1
    assert link["observations"][0]["asset_id"] == "legacy-asset-001"
    assert "metadata-only" in link["interpretation"]["limitations"]


def test_schema() -> None:
    schema = json.loads((ROOT / "schemas/discovery_manifest.schema.json").read_text(encoding="utf-8"))
    link_schema = json.loads((ROOT / "schemas/discovery_memory_link.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["download_performed"]["const"] is False
    assert schema["properties"]["provenance"]["properties"]["policy"]["const"] == "metadata-only"
    assert link_schema["properties"]["source_type"]["const"] == "oi_discovery_manifest"


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as directory:
        test_selection()
        test_manifest(Path(directory))
        test_bridge()
        test_legacy_manifest()
        test_schema()
    print("offline_tests_ok: selection, manifest, bridge, legacy manifest, schema")
