"""Live metadata-only checks for a public DANDI dataset.

This runner intentionally does not download assets or execute biological analysis.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from oi_discovery.adapters.dandi import DandiAdapter
from oi_discovery.bridge import build_link
from oi_discovery.manifest import build_result, write_manifest
from oi_discovery.models import DiscoveryQuery


OUT = Path("/tmp/oi_discovery_live_dandi_001603")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    query = DiscoveryQuery(
        source="dandi",
        dataset_id="001603",
        version="draft",
        formats=("nwb",),
        max_assets=1,
    )
    dataset = DandiAdapter().discover(query)
    assert dataset.dataset_id == "001603"
    assert dataset.asset_count >= 1
    assert dataset.raw_metadata.get("dataset")
    assert dataset.raw_metadata.get("asset_count_from_api") == dataset.asset_count

    result = build_result(dataset, query)
    manifest_path = write_manifest(result, OUT / "dandi_001603_live_manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["query"]["dataset_id"] == "001603"
    assert manifest["download_performed"] is False
    assert len(manifest["selected_asset_ids"]) == 1
    assert manifest["decisions"]

    link = build_link(
        manifest,
        str(manifest_path),
        capability_ids=["CAP-OBS-EVIDENCE_MEMORY_DECISION"],
    )
    link_path = OUT / "dandi_001603_live_memory_link.json"
    link_path.write_text(json.dumps(link, indent=2) + "\n", encoding="utf-8")
    assert link["interpretation"]["status"] == "candidate"
    assert "metadata-only" in link["interpretation"]["limitations"]
    assert link["luxmemory"]["capability_ids"] == ["CAP-OBS-EVIDENCE_MEMORY_DECISION"]

    print("live_metadata_tests_ok")
    print(f"dataset_id={dataset.dataset_id}")
    print(f"asset_count={dataset.asset_count}")
    print(f"selected_asset_ids={result.selected_asset_ids}")
    print("download_performed=False")
    print(f"manifest={manifest_path}")
    print(f"memory_link={link_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
