# Investigation State and Research Moves

TraceFoundry can represent more than a list of search results. The public investigation layer describes **what is known, what is inferred, what remains unresolved, and which next action would reduce uncertainty**.

This layer is intentionally conservative. It uses public metadata and provenance; it does not download scientific assets, run notebooks, deserialize NWB/HDF5/pickle files, or generate unsupported scientific conclusions.

## Core objects

| Object | Purpose |
|---|---|
| `EvidenceReference` | Points to a public source observation, record, asset metadata entry or paper metadata record. |
| `Claim` | A reviewable statement with an explicit epistemic status: `observed`, `inferred`, `hypothesis`, `insufficient`, `blocked`, `rejected` or `contradicted`. |
| `EvidenceGap` | States what prevents a stronger claim or decision and what evidence is required. |
| `InvestigationState` | Versioned snapshot of one question, its evidence, claims, gaps, decision and next move. |
| `ResearchMove` | A proposed or completed next action with rationale, input evidence, expected observation and stop criteria. |

The contracts are available in Python under `oi_discovery.investigation` and as JSON Schemas under `schemas/`.

## Five-minute example

```bash
PYTHONPATH=src python3 scripts/show_research_move.py
PYTHONPATH=src python3 tests/run_research_move_tests.py
```

The public fixture in `examples/research_move_v0/` is derived from the metadata-only V001 execution. It contains public source URLs and conservative statements; it does not contain raw data or private laboratory memory.

## Why this is different from ordinary retrieval

Retrieval returns candidates. An investigation state preserves the status of the evidence and the gaps that still matter. A Research Move converts that state into a next action that can be reviewed, rejected or completed. This makes the system useful for research operations, technology intelligence, due diligence and other decisions where an unsupported answer is worse than an explicit “not yet enough evidence.”

## Public/private boundary

The public layer contains generic contracts, adapters, schemas, reproducible metadata fixtures and evaluation rules. Private systems may add sensitive questions, memory, unpublished claims, proprietary corpora, experimental results and operational decisions. Those layers are intentionally not required by the public contracts.

## Status vocabulary

A status is not a confidence score. It describes the epistemic role of a statement in the investigation. `observed` means directly supported by the cited source metadata. `inferred` means a reviewable interpretation from observations. `hypothesis` is a proposition that still requires a test. `insufficient`, `blocked`, `rejected` and `contradicted` preserve negative evidence instead of hiding it.
