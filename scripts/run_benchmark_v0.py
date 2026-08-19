"""Run the executable portion of OI Discovery Benchmark v0.

The runner intentionally records partial coverage and dependency blocks. It does
not download scientific content or claim that metadata-only candidates satisfy
scientific, legal, licensing, or reproducibility criteria that the adapters do
not expose.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from oi_discovery.adapters.dandi import DandiAdapter
from oi_discovery.adapters.openalex import OpenAlexAdapter
from oi_discovery.adapters.patentsview import PatentAdapter
from oi_discovery.adapters.zenodo import ZenodoAdapter
from oi_discovery.evaluation import assess_manifest
from oi_discovery.manifest import build_result, write_manifest
from oi_discovery.models import DiscoveryQuery
from oi_discovery.registry import DiscoveryRegistry, DiscoveryRun


RESULTS_DIR = ROOT / "benchmark" / "runs_v0"
SUMMARY_PATH = ROOT / "benchmark" / "results_v0.json"
REGISTRY_PATH = ROOT / "benchmark" / "registry_v0.jsonl"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_id(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def query_dict(query: DiscoveryQuery) -> dict[str, Any]:
    return query.to_dict()


def append_dependency_block(
    registry: DiscoveryRegistry,
    *,
    question_id: str,
    source: str,
    query: DiscoveryQuery,
    reason: str,
    next_action: str,
) -> dict[str, Any]:
    evaluation = {
        "assessment_schema_version": "oi.discovery.assessment.v0",
        "conclusion": "dependency_blocked",
        "basis": "required_external_dependency_unavailable",
        "sources_consulted": [],
        "candidate_count": 0,
        "rejected_count": 0,
        "rejection_reasons": {},
        "unresolved_constraints": [reason],
        "hard_constraints": [],
        "warnings": [reason],
        "next_action": next_action,
    }
    registry.append(
        DiscoveryRun(
            run_id=stable_id({"question_id": question_id, "source": source, "query": query_dict(query), "status": "dependency_blocked"}),
            created_at=utc_now(),
            query={**query_dict(query), "benchmark_question_id": question_id},
            sources=[source],
            reasons=[reason],
            evaluation=evaluation,
            next_action=next_action,
            status="dependency_blocked",
            warnings=[reason],
        )
    )
    return {
        "question_id": question_id,
        "source": source,
        "query": query.dataset_id,
        "status": "dependency_blocked",
        "reason": reason,
        "evaluation": evaluation,
        "download_performed": False,
    }


def run_case(
    registry: DiscoveryRegistry,
    *,
    question_id: str,
    case_name: str,
    adapter: Any,
    query: DiscoveryQuery,
    unresolved_constraints: list[str],
    hard_constraints: list[str],
    cache: dict[tuple[str, str | None, str], Any],
) -> dict[str, Any]:
    cache_key = (adapter.source_name, query.dataset_id, query.version)
    if cache_key not in cache:
        cache[cache_key] = adapter.discover(query)
    dataset = cache[cache_key]
    result = build_result(dataset, query)
    manifest_path = write_manifest(result, RESULTS_DIR / f"{question_id}_{case_name}.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluation = assess_manifest(
        manifest,
        unresolved_constraints=unresolved_constraints,
        hard_constraints=hard_constraints,
    )
    run = DiscoveryRun.from_manifest(
        manifest,
        evaluation=evaluation,
        next_action=evaluation["next_action"],
        status=evaluation["conclusion"],
    )
    run.query = {**run.query, "benchmark_question_id": question_id}
    registry.append(run)
    return {
        "question_id": question_id,
        "case": case_name,
        "source": dataset.source,
        "query": query.dataset_id,
        "status": evaluation["conclusion"],
        "records": dataset.asset_count,
        "selected": len(result.selected_asset_ids),
        "rejected": sum(1 for decision in manifest.get("decisions", []) if not decision.get("eligible", False)),
        "evaluation": evaluation,
        "manifest": str(manifest_path.relative_to(ROOT)),
        "download_performed": False,
    }


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if REGISTRY_PATH.exists():
        REGISTRY_PATH.unlink()
    registry = DiscoveryRegistry(REGISTRY_PATH)
    cache: dict[tuple[str, str | None, str], Any] = {}
    dandi = DandiAdapter()
    zenodo = ZenodoAdapter()
    openalex = OpenAlexAdapter()
    patentsview = PatentAdapter()
    results: list[dict[str, Any]] = []

    def add_case(question_id: str, case_name: str, adapter: Any, query: DiscoveryQuery, unresolved: list[str], hard: list[str]) -> None:
        try:
            results.append(run_case(registry, question_id=question_id, case_name=case_name, adapter=adapter, query=query, unresolved_constraints=unresolved, hard_constraints=hard, cache=cache))
        except Exception as exc:  # benchmark records dependency failures as data, not as scientific absence
            source = getattr(adapter, "source_name", "unknown")
            reason = f"{source}_execution_failed: {type(exc).__name__}: {exc}"
            results.append(append_dependency_block(
                registry,
                question_id=question_id,
                source=source,
                query=query,
                reason=reason,
                next_action=f"retry_{source}_benchmark_case_after_dependency_recovery",
            ))

    add_case(
        "B001", "dandi_001603", dandi,
        DiscoveryQuery(source="dandi", dataset_id="001603", version="draft", formats=("nwb",), max_assets=3),
        ["human relevance not normalized by DANDI adapter", "electrophysiology modality not normalized", "NWB equivalence and documentation require manual review"],
        ["human or human-derived", "electrophysiology modality", "NWB or equivalent metadata"],
    )
    add_case(
        "B001", "zenodo_organoid_electrophysiology", zenodo,
        DiscoveryQuery(source="zenodo", dataset_id="human organoid electrophysiology NWB", formats=("record",), max_assets=3),
        ["human relevance, modality and NWB support are not hard filters in the common selector"],
        ["human or human-derived", "electrophysiology modality", "NWB or equivalent metadata"],
    )
    add_case(
        "B001", "openalex_organoid_electrophysiology", openalex,
        DiscoveryQuery(source="openalex", dataset_id="human organoid electrophysiology", formats=("paper",), max_assets=3),
        ["paper metadata is not a dataset-content proof", "NWB support is unresolved"],
        ["public dataset evidence", "NWB or equivalent metadata"],
    )

    add_case(
        "B002", "openalex_lithium_low_temperature", openalex,
        DiscoveryQuery(source="openalex", dataset_id="lithium recovery low temperature", formats=("paper",), max_assets=3),
        ["temperature condition may require abstract/full-text inspection", "Crossref adapter unavailable"],
        ["lithium recovery", "low-temperature process condition"],
    )

    add_case(
        "B003", "zenodo_mangrove_brazil", zenodo,
        DiscoveryQuery(source="zenodo", dataset_id="mangrove Brazil", formats=("record",), max_assets=3),
        ["geographic relevance and deduplication require review"],
        ["mangrove and Brazil relevance", "license or access field present"],
    )
    add_case(
        "B003", "openalex_mangrove_brazil", openalex,
        DiscoveryQuery(source="openalex", dataset_id="mangrove Brazil", formats=("paper",), max_assets=3),
        ["paper metadata is not a dataset-access proof", "license/access completeness is unresolved"],
        ["mangrove and Brazil relevance", "license or access field present"],
    )

    add_case(
        "B004", "openalex_mineral_metal_recovery", openalex,
        DiscoveryQuery(source="openalex", dataset_id="mineral retrieval metal recovery", formats=("paper",), max_assets=3),
        ["target mineral and method cues require title/abstract/manual comparison", "Crossref adapter unavailable"],
        ["target material identified", "retrieval or recovery process signal"],
    )
    if not os.getenv("PATENTSVIEW_API_KEY"):
        results.append(append_dependency_block(
            registry,
            question_id="B004",
            source="patentsview",
            query=DiscoveryQuery(source="patentsview", dataset_id="metal recovery", formats=("patent_metadata",), max_assets=3),
            reason="PATENTSVIEW_API_KEY is unavailable; patent evidence was not queried.",
            next_action="provide_patentsview_api_key_for_patent_source_comparison",
        ))
    else:
        add_case(
            "B004", "patentsview_metal_recovery", patentsview,
            DiscoveryQuery(source="patentsview", dataset_id="metal recovery", formats=("patent_metadata",), max_assets=3),
            ["claims and legal status are not downloaded or validated"],
            ["target material identified", "retrieval or recovery process signal"],
        )

    if not os.getenv("PATENTSVIEW_API_KEY"):
        results.append(append_dependency_block(
            registry,
            question_id="B005",
            source="patentsview",
            query=DiscoveryQuery(source="patentsview", dataset_id="methanol detection", formats=("patent_metadata",), max_assets=5),
            reason="PATENTSVIEW_API_KEY is unavailable; patent-family evidence was not queried.",
            next_action="provide_patentsview_api_key_for_patent_family_smoke_test",
        ))
    else:
        add_case(
            "B005", "patentsview_methanol_detection", patentsview,
            DiscoveryQuery(source="patentsview", dataset_id="methanol detection", formats=("patent_metadata",), max_assets=5),
            ["family grouping, jurisdiction completeness, claims and legal status require review"],
            ["methanol detection relevance", "family or publication identifier"],
        )

    add_case(
        "B007", "zenodo_environmental_comparison", zenodo,
        DiscoveryQuery(source="zenodo", dataset_id="mangrove environmental monitoring", formats=("record",), max_assets=3),
        ["cross-source duplicate detection module is not implemented"],
        ["stable identifiers and title/author/year comparability"],
    )
    add_case(
        "B007", "openalex_environmental_comparison", openalex,
        DiscoveryQuery(source="openalex", dataset_id="mangrove environmental monitoring", formats=("paper",), max_assets=3),
        ["cross-source duplicate detection module is not implemented"],
        ["stable identifiers and title/author/year comparability"],
    )

    add_case(
        "B008", "dandi_readiness_001603", dandi,
        DiscoveryQuery(source="dandi", dataset_id="001603", version="draft", formats=("nwb",), max_assets=3),
        ["accessibility, license and documentation readiness are not fully normalized"],
        ["accessible metadata", "license/access evidence", "documentation signal"],
    )
    add_case(
        "B008", "zenodo_readiness_organoid", zenodo,
        DiscoveryQuery(source="zenodo", dataset_id="organoid electrophysiology", formats=("record",), max_assets=3),
        ["documentation signal and scientific readiness require manual review"],
        ["accessible metadata", "license/access evidence", "documentation signal"],
    )
    if not os.getenv("PATENTSVIEW_API_KEY"):
        results.append(append_dependency_block(
            registry,
            question_id="B008",
            source="patentsview",
            query=DiscoveryQuery(source="patentsview", dataset_id="organoid technology", formats=("patent_metadata",), max_assets=3),
            reason="PATENTSVIEW_API_KEY is unavailable; patent readiness evidence was not queried.",
            next_action="provide_patentsview_api_key_for_readiness_comparison",
        ))

    add_case(
        "B009", "dandi_nwb_under_1mb", dandi,
        DiscoveryQuery(source="dandi", dataset_id="001603", version="draft", formats=("nwb",), max_size_bytes=1024 * 1024, max_assets=3),
        ["human system and documentation sufficiency are unresolved"],
        ["NWB format", "electrophysiology modality", "human system", "size <= 1 MB", "documentation sufficient"],
    )
    add_case(
        "B009", "zenodo_nwb_under_1mb", zenodo,
        DiscoveryQuery(source="zenodo", dataset_id="human electrophysiology NWB", formats=("nwb",), max_size_bytes=1024 * 1024, max_assets=3),
        ["Zenodo search result format/access semantics require manual review"],
        ["NWB format", "electrophysiology modality", "human system", "size <= 1 MB", "documentation sufficient"],
    )

    # These benchmark questions remain explicit non-runs because the required adapters/modules do not exist yet.
    pending = [
        {
            "question_id": "B006",
            "status": "pending_adapter",
            "reason": "GitHub/Crossref paper-to-code linkage adapter is not implemented in the public core.",
            "next_action": "implement paper-to-code provenance adapter before running B006",
        },
        {
            "question_id": "B010",
            "status": "pending_cross_source_module",
            "reason": "Cross-source evidence map and conflict/readiness module are not implemented as a single benchmark runner.",
            "next_action": "implement cross-source merge and conflict gate before running B010",
        },
    ]
    for item in pending:
        registry.append(
            DiscoveryRun(
                run_id=stable_id(item),
                created_at=utc_now(),
                query={"benchmark_question_id": item["question_id"]},
                sources=[],
                reasons=[item["reason"]],
                evaluation={
                    "assessment_schema_version": "oi.discovery.assessment.v0",
                    "conclusion": item["status"],
                    "basis": "required_public_module_unavailable",
                    "sources_consulted": [],
                    "candidate_count": 0,
                    "rejected_count": 0,
                    "rejection_reasons": {},
                    "unresolved_constraints": [item["reason"]],
                    "hard_constraints": [],
                    "warnings": [item["reason"]],
                    "next_action": item["next_action"],
                },
                next_action=item["next_action"],
                status=item["status"],
                warnings=[item["reason"]],
            )
        )
    results.extend(pending)

    summary = {
        "schema_version": "oi.discovery.benchmark.results.v0",
        "benchmark": "benchmark/benchmark_v0.json",
        "created_at": utc_now(),
        "policy": {"metadata_only": True, "no_raw_download": True, "human_review_required": True},
        "executed_question_ids": sorted({item["question_id"] for item in results if item["question_id"] not in {"B006", "B010"}}),
        "pending_question_ids": ["B006", "B010"],
        "results": results,
        "registry": str(REGISTRY_PATH.relative_to(ROOT)),
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"benchmark_v0_complete results={len(results)} registry={REGISTRY_PATH}")
    for item in results:
        print(json.dumps({key: item[key] for key in ("question_id", "source", "status") if key in item}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
