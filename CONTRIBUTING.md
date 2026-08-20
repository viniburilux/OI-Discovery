# Contributing to TraceFoundry

Thank you for considering a contribution. TraceFoundry is intentionally small: a useful contribution makes discovery more reproducible without hiding uncertainty behind a larger abstraction.

## Before opening a pull request

Read the [architecture guide](docs/ARCHITECTURE.md), run the offline tests and describe whether your change affects the public contract, a source adapter, selection policy, provenance or documentation.

```bash
PYTHONPATH=src python tests/run_offline_tests.py
PYTHONPATH=src python tests/run_dsl_registry_tests.py
python3 -m py_compile $(find src scripts tests -name '*.py' -print)
```

## Adding an adapter

A new source adapter should implement the shared contract, preserve official identifiers and URLs, retain version information, normalize native responses into `DatasetRecord` and `AssetRecord`, and expose warnings when the source omits or ambiguously represents a field.

Adapters must be metadata-only by default. They must not download scientific data, execute notebooks, deserialize arbitrary serialized objects or silently invent fields that the source did not return. If a source requires authentication, the adapter must fail explicitly or record a skipped condition without exposing credentials.

## Selection and evidence rules

Selection rules belong in the common layer, not inside a source-specific adapter. A candidate must remain distinguishable from a scientific conclusion. Rejection reasons, insufficient evidence, dependency blocks and true zero-candidate results must remain separate states.

When a change affects these states, add or update an offline fixture and a test that demonstrates the intended behavior.

## Documentation standard

Documentation should state what was observed, what was inferred and what remains hypothetical. Avoid claims such as “validated,” “scientifically suitable,” “first,” “state of the art” or “production-ready” unless the repository contains a reproducible basis for that wording.

## Pull requests

A pull request should explain the user problem, the changed contract, the evidence supporting the implementation and the limitations that remain. Prefer small, reviewable changes over broad refactors. Do not include private datasets, credentials, raw biological files, personal information or generated artifacts that cannot be reproduced from public metadata.

## Scope

TraceFoundry is the public infrastructure layer. Domain-specific research pipelines, private claims, investigation state, experimental data and LuxMemory records belong in the appropriate private repository.
