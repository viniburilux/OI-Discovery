# OI Discovery

OI Discovery is a metadata-first, source-agnostic foundation for discovering scientific datasets and assets, recording why each candidate was selected or rejected, and handing the result to a reviewable memory system.

It is intentionally smaller than a general scientific platform. The first public core answers a concrete operational question:

> Which public assets match a query over source, dataset, format, size and provenance, and why?

The core does not download biological data, deserialize pickle files, claim scientific suitability, or replace domain review. It creates a reproducible manifest that another researcher or system can inspect before any controlled acquisition or analysis.

## What is included

The package contains a source-agnostic `DiscoveryAdapter` contract, an initial DANDI adapter, normalized dataset and asset models, deterministic eligibility and ranking, a versioned manifest schema, and a bridge that converts a manifest into a candidate link for LuxMemory. The bridge preserves the query hash, metadata observations, candidate status, limitations, capability IDs and validation gate without writing to a database automatically.

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

The live command requires network access to the public DANDI API. It produces metadata only and always records `download_performed: false`.

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
```

The suite validates deterministic selection, manifest generation, schema invariants, the OI→LuxMemory bridge, and compatibility with a real metadata-only DANDI manifest. It does not execute the private research scripts and does not load raw scientific files.

## Extension model

New sources should implement the adapter contract and map their native response into `DatasetRecord` and `AssetRecord`. The source-specific adapter should preserve raw metadata, source identifiers, official URLs, version information and explicit warnings. Selection rules belong to the common layer so that DANDI, OpenAlex, Zenodo, GitHub, Crossref or Europe PMC can be compared without duplicating policy.

The intended evolution is:

```text
source API → adapter → canonical records → explainable selection → manifest → LuxMemory review link → controlled analysis
```

## Epistemic boundary

An eligible asset is an operational candidate, not a scientific conclusion. A manifest can prove what the source reported at a given time and why the deterministic query selected an asset. It cannot prove data quality, biological relevance, statistical validity, license compatibility for every derivative, or suitability for a particular hypothesis.

## License

The public core is released under the MIT License. Source-specific datasets, papers, external APIs and private research artifacts remain subject to their own terms.
