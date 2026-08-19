"""Cross-domain metadata-only smoke tests for OI Discovery.

The tests call public metadata endpoints and never download dataset contents.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from oi_discovery.adapters.dandi import DandiAdapter
from oi_discovery.adapters.openalex import OpenAlexAdapter
from oi_discovery.adapters.patentsview import PatentAdapter
from oi_discovery.adapters.zenodo import ZenodoAdapter
from oi_discovery.bridge import build_link
from oi_discovery.manifest import build_result, write_manifest
from oi_discovery.models import DiscoveryQuery


OUT = Path("/tmp/oi_discovery_cross_domain")


def run_case(name: str, adapter: object, query: DiscoveryQuery) -> dict[str, object]:
    dataset = adapter.discover(query)  # type: ignore[attr-defined]
    result = build_result(dataset, query)
    manifest_path = write_manifest(result, OUT / f"{name}.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["download_performed"] is False
    assert manifest["dataset"]["asset_count"] > 0
    assert manifest["selected_asset_ids"], f"no eligible assets for {name}"
    link = build_link(manifest, str(manifest_path))
    assert link["interpretation"]["status"] == "candidate"
    return {
        "name": name,
        "source": dataset.source,
        "query": query.dataset_id,
        "records": dataset.asset_count,
        "selected": len(result.selected_asset_ids),
        "manifest": str(manifest_path),
        "download_performed": False,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cases = [
        (
            "01_organoids_dandi",
            DandiAdapter(),
            DiscoveryQuery(source="dandi", dataset_id="001603", version="draft", formats=("nwb",), max_assets=1),
        ),
        (
            "02_mangrove_zenodo",
            ZenodoAdapter(),
            DiscoveryQuery(source="zenodo", dataset_id="mangrove Brazil", formats=("record",), max_assets=3),
        ),
        (
            "03_technology_papers_openalex",
            OpenAlexAdapter(),
            DiscoveryQuery(source="openalex", dataset_id="lithium recovery technology", formats=("paper",), max_assets=3),
        ),
    ]
    results = [run_case(name, adapter, query) for name, adapter, query in cases]
    patent_query = DiscoveryQuery(
        source="patentsview",
        dataset_id="methanol detection",
        version="v0",
        formats=("patent_metadata",),
        max_assets=5,
    )
    if not os.getenv("PATENTSVIEW_API_KEY"):
        results.append({
            "name": "04_methanol_detection_patentsview",
            "source": "patentsview",
            "query": patent_query.dataset_id,
            "status": "skipped_no_api_key",
            "reason": "PATENTSVIEW_API_KEY is not available in this environment; no network call was attempted.",
            "download_performed": False,
        })
    else:
        results.append(run_case("04_methanol_detection_patentsview", PatentAdapter(), patent_query))
    report = OUT / "cross_domain_results.json"
    report.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print("cross_domain_live_tests_ok")
    for item in results:
        print(json.dumps(item, sort_keys=True))
    print(f"report={report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
