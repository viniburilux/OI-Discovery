# OI Discovery — test matrix v1

**Run date:** 2026-08-19. **Policy:** metadata-only; no dataset content was downloaded.

## Executive result

The same OI Discovery contract successfully ran against three distinct public metadata sources: DANDI for organoid assets, Zenodo for mangrove-related records, and OpenAlex for technology papers. This is evidence that the adapter and manifest architecture generalizes structurally beyond the original organoid use case. It is not evidence of scientific suitability, source completeness, licensing clearance, or commercial value.

## Matrix

| Type | Claim or hypothesis | Test | Observed result | Status | Next step |
|---|---|---|---|---|---|
| Fact | The public core has deterministic selection, manifests, schemas and an OI→LuxMemory bridge. | `PYTHONPATH=src python3 tests/run_offline_tests.py` | `offline_tests_ok: selection, manifest, bridge, legacy manifest, schema` | Observed and reproducible | Keep this as the regression gate for every adapter. |
| Fact | The DANDI adapter can query a live public dandiset without downloading an asset. | `PYTHONPATH=src python3 tests/run_live_metadata_tests.py` | 111 assets discovered; 1 selected; `download_performed=false` | Observed in this run | Add pagination and rate-limit telemetry before batch use. |
| Fact | The DANDI asset selection can preserve an official asset reference when the listing response does not provide one directly. | Live DANDI test plus source URL probe | One NWB asset selected with official API reference; no download | Observed in this run | Add a test for expired or inaccessible asset URLs. |
| Fact | The same contract works for a public Zenodo search. | Cross-domain runner, query `mangrove Brazil` | 25 records returned; 3 selected; manifest and LuxMemory link generated | Observed in this run | Add deduplication across Zenodo versions and record files. |
| Fact | The same contract works for a public OpenAlex works search. | Cross-domain runner, query `lithium recovery technology` | 25 papers returned; 3 selected; manifest and LuxMemory link generated | Observed in this run | Preserve DOI, abstract availability and open-access status as first-class fields. |
| Inference | OI Discovery is not structurally tied to organoids. | Compare the three live runs under one runner and one selection layer | The common adapter/manifest/bridge path succeeded in all three domains | Strong structural inference | Evaluate precision and user value with domain-expert questions. |
| Hypothesis | Researchers benefit from an explainable candidate list more than from a raw API result. | Human benchmark of 10–20 real discovery questions | Not run yet | Unvalidated | Ask a researcher to rate source coverage, reasons, time saved and next action. |
| Hypothesis | A manifest is useful as a handoff between discovery, memory and later analysis. | Re-open generated link in LuxMemory and review provenance fields | Link generated and status remains `candidate`; no automatic DB mutation | Partially tested | Add an explicit LuxMemory import/review screen or CLI queue. |
| Hypothesis | OI Discovery can support patents as well as papers and datasets. | Implement a patent-specific adapter and run the same matrix | Not implemented; OpenAlex test covers papers, not patents | Unvalidated | Choose an authorized/public patent source and define claim/family fields. |
| Boundary | A selected asset is not proof of scientific relevance or data quality. | Inspect manifest semantics and epistemic status | Selected items are operational candidates; link status is `candidate` | Explicitly preserved | Do not promote selection to evidence without domain review. |

## Commands

From the repository root:

```bash
python3 -m py_compile $(find src scripts tests -name '*.py' -print)
PYTHONPATH=src python3 tests/run_offline_tests.py
PYTHONPATH=src python3 tests/run_live_metadata_tests.py
PYTHONPATH=src python3 tests/run_cross_domain_live_tests.py
```

The live commands require network access. They query only metadata endpoints and write temporary outputs under `/tmp/`.

## What the tests do not establish

The test suite does not establish that a DANDI, Zenodo or OpenAlex result is scientifically relevant to a particular hypothesis. It does not benchmark recall against a gold-standard corpus, verify every license for downstream derivatives, download or inspect raw biological files, compare against conventional search/RAG, or implement patent coverage. Those are separate experiments and must be labeled as such.

## References

[1] [DANDI API](https://api.dandiarchive.org/api/) — public dandiset and asset metadata API.  
[2] [Zenodo Records API](https://developers.zenodo.org/) — public record search and metadata API.  
[3] [OpenAlex API](https://docs.openalex.org/) — public scholarly works metadata API.  
[4] [OI-Discovery repository](https://github.com/viniburilux/OI-Discovery) — public implementation and test runners.  
[5] [LuxMemory repository](https://github.com/viniburilux/LuxMemory) — structured memory and capability layer used by the bridge.
