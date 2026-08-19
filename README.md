# OI Discovery

OI Discovery is a metadata-first, source-agnostic foundation for discovering scientific datasets and assets, recording why each candidate was selected or rejected, and handing the result to a reviewable memory system.

It is intentionally smaller than a general scientific platform. The first public core answers a concrete operational question:

> Which public assets match a query over source, dataset, format, size and provenance, and why?

The core does not download biological data, deserialize pickle files, claim scientific suitability, or replace domain review. It creates a reproducible manifest that another researcher or system can inspect before any controlled acquisition or analysis.

## What is included

The package contains a source-agnostic `DiscoveryAdapter` contract, DANDI, OpenAlex, PatentsView and Zenodo adapters, normalized dataset and asset models, deterministic eligibility and ranking, a versioned manifest schema, and a bridge that converts a manifest into a candidate link for LuxMemory. The PatentsView adapter searches patent metadata only and preserves identifiers, titles, dates, classifications, inventors, assignees and family fields when the API returns them. The bridge preserves the query hash, metadata observations, candidate status, limitations, capability IDs and validation gate without writing to a database automatically.

The public repository is the reusable infrastructure layer. The private [OI-Organoids-Intelligence](https://github.com/viniburilux/OI-Organoids-Intelligence) repository remains the research laboratory for papers, experiments, source-specific scripts and biological analysis.

## Quick start

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
PYTHONPATH=src python scripts/oi_discover.py \
  --source dandi \
  --dataset-id 001603 \
  --version draft \
  --format nwb \
  --max-assets 1 \
  --output discovery_result.json
```

The live command requires network access to the selected public API. For PatentsView, set `PATENTSVIEW_API_KEY` before running a live query; the adapter refuses live calls without the key. All adapters produce metadata only and the manifest always records `download_performed: false`.

A PatentsView query uses `dataset_id` as the text search while keeping the canonical query contract source-agnostic:

```bash
export PATENTSVIEW_API_KEY="..."
PYTHONPATH=src python scripts/oi_discover.py \
  --source patentsview \
  --dataset-id "methanol detection" \
  --max-assets 5 \
  --output patentsview_result.json
```

For tests that must not use a network or credential, call `PatentAdapter.normalize_response()` with a saved fixture payload.

To connect an existing manifest to LuxMemory without changing the database:

```bash
PYTHONPATH=src python scripts/link_manifest_to_luxmemory.py \
  --manifest discovery_result.json \
  --output discovery_memory_link.json \
  --memory-type result \
  --capability-id CAP-OBS-EVIDENCE_MEMORY_DECISION
```

## Offline validation

No network is required for the core validation:

```bash
PYTHONPATH=src python tests/run_offline_tests.py
PYTHONPATH=src python tests/run_live_metadata_tests.py
PYTHONPATH=src python tests/run_cross_domain_live_tests.py
PYTHONPATH=src python tests/run_dsl_registry_tests.py
```

The suite validates the offline PatentsView normalizer, deterministic selection, manifest generation, schema invariants, the OI→LuxMemory bridge, query DSL and registry behavior, and compatibility with a real metadata-only DANDI manifest. It does not execute the private research scripts and does not load raw scientific files. The cross-domain live test can cover DANDI, Zenodo and OpenAlex without a patent credential; PatentsView live coverage is reported as skipped when `PATENTSVIEW_API_KEY` is unavailable.

## Extension model

New sources should implement the adapter contract and map their native response into `DatasetRecord` and `AssetRecord`. The source-specific adapter should preserve raw metadata, source identifiers, official URLs, version information and explicit warnings. Selection rules belong to the common layer so that DANDI, OpenAlex, PatentsView, Zenodo, GitHub, Crossref or Europe PMC can be compared without duplicating policy.

The intended evolution is:

```text
source API → adapter → canonical records → explainable selection → manifest → LuxMemory review link → controlled analysis
```

The cross-domain live smoke test currently exercises DANDI for organoids, Zenodo for mangrove-related records, and OpenAlex for technology papers. PatentsView is now covered offline with a deterministic fixture; its live smoke test is intentionally conditional on `PATENTSVIEW_API_KEY` and is skipped, with an explicit reason, when no credential is available.

## Epistemic boundary

An eligible asset is an operational candidate, not a scientific conclusion. A manifest can prove what the source reported at a given time and why the deterministic query selected an asset. It cannot prove data quality, biological relevance, statistical validity, license compatibility for every derivative, or suitability for a particular hypothesis.

## License

The public core is released under the MIT License. Source-specific datasets, papers, external APIs and private research artifacts remain subject to their own terms.
